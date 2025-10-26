#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.10"
# dependencies = ["aiohttp"]
# ///
"""
ghkeys: Fetch SSH public keys from GitHub users.

Usage:
  ghkeys alice bob
  ghkeys alice bob --append
  ghkeys alice bob --output ssh_keys.txt
  ghkeys alice bob --json
  ghkeys alice bob --inline-comments

License:
  MIT License (c) 2025 bjornmorten
"""

import argparse
import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from typing import List, NamedTuple

GITHUB_KEYS_URL = "https://github.com/{user}.keys"
PROJECT_URL = "https://github.com/bjornmorten/ghkeys"
USER_AGENT = f"ghkeys/1.0 (+{PROJECT_URL})"


class FetchResult(NamedTuple):
    user: str
    keys: str | None
    error: str | None


async def fetch_keys(session: aiohttp.ClientSession, user: str) -> FetchResult:
    """Fetch the SSH public keys for a single GitHub user."""
    url = GITHUB_KEYS_URL.format(user=user)
    try:
        async with session.get(url, timeout=20) as resp:
            if resp.status == 404:
                return FetchResult(user, None, "User not found")
            if resp.status != 200:
                return FetchResult(user, None, f"HTTP {resp.status}")
            text = (await resp.text()).strip()
            if not text:
                return FetchResult(user, None, "No keys found")
            return FetchResult(user, text, None)
    except asyncio.TimeoutError:
        return FetchResult(user, None, "Request timed out")
    except Exception as e:
        return FetchResult(user, None, str(e))


async def fetch_all(users: List[str]) -> List[FetchResult]:
    """Fetch keys for multiple users concurrently."""
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_keys(session, u) for u in users]
        return await asyncio.gather(*tasks)


def confirm_overwrite(path: Path, force: bool):
    if path.exists() and not force:
        print(f"File {path} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)


def safe_write(path: Path, content: str, force: bool):
    confirm_overwrite(path, force)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"Wrote keys to {path}", file=sys.stderr)


def safe_append(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(content)
    print(f"Appended keys to {path}", file=sys.stderr)


def format_results(results: List[FetchResult], inline: bool = False) -> str:
    combined = []
    had_errors = False

    for result in results:
        if result.error:
            had_errors = True
            print(f"{result.user}: {result.error}", file=sys.stderr)
            continue
        if not result.keys:
            continue
        if inline:
            lines = [f"{line} {result.user}" for line in result.keys.splitlines() if line.strip()]
            combined.extend(lines)
        else:
            combined.append(f"# {result.user}\n{result.keys}\n")
    return ("\n".join(combined).strip() + "\n", had_errors)


async def main():
    parser = argparse.ArgumentParser(description="Fetch SSH public keys from GitHub users.")
    parser.add_argument("users", nargs="+", help="GitHub usernames")
    parser.add_argument("-i", "--inline-comments", action="store_true",
                        help="Append username to the end of each key")
    parser.add_argument("-j", "--json", action="store_true", help="Output JSON instead of SSH keys")
    parser.add_argument("-a", "--append", action="store_true", help="Append to ~/.ssh/authorized_keys (or --output file if given)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write keys to specified file")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing file")
    args = parser.parse_args()

    results = await fetch_all(args.users)

    if args.json:
        data = [
            {"user": r.user, "keys": r.keys.splitlines() if r.keys else [], "error": r.error}
            for r in results
        ]
        print(json.dumps(data, indent=2))
        return

    combined, had_errors = format_results(results, inline=args.inline_comments)
    if not combined.strip():
        print("No keys fetched.", file=sys.stderr)
        return

    if had_errors:
        print(file=sys.stderr)

    if args.append:
        target = Path(args.output).expanduser() if args.output else Path("~/.ssh/authorized_keys").expanduser()
        safe_append(target, combined)
    elif args.output:
        safe_write(Path(args.output).expanduser(), combined, args.force)
    else:
        print(combined, end="")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
