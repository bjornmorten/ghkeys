# ghkeys

Fetch SSH public keys from GitHub users.

## Usage

```sh
ghkeys [options] USERNAME [USERNAME...]
```

## Options

| Option                  | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `-i, --inline-comments` | Append username to the end of each key                             |
| `-j, --json`            | Output JSON instead of plain text                                  |
| `-a, --append`          | Append to `~/.ssh/authorized_keys` (or `--output` file if given)   |
| `-o, --output FILE`     | Write keys to specified file (requires `--force` unless appending) |
| `-f, --force`           | Overwrite existing file                                            |

## Example output

### Standard output

```
# alice
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIODUglW24j2nFdLmlWMpWqcJ1dtf2SwHJ+NLDCZHI+hJ

# bob
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINKGckU0/hydGxzGSPUnXGZRcnrzm2zIHrflMAgrVC+W
```

### Inline Comments (`--inline-comments`)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIODUglW24j2nFdLmlWMpWqcJ1dtf2SwHJ+NLDCZHI+hJ alice
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINKGckU0/hydGxzGSPUnXGZRcnrzm2zIHrflMAgrVC+W bob
```

### JSON Output (`--json`)

```json
[
  {
    "user": "alice",
    "keys": ["ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIODUglW24j2nFdLmlWMpWqcJ1dtf2SwHJ+NLDCZHI+hJ"],
    "error": null
  },
  {
    "user": "bob",
    "keys": ["ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINKGckU0/hydGxzGSPUnXGZRcnrzm2zIHrflMAgrVC+W"],
    "error": null
  }
]
```

## License

MIT License © 2025 [bjornmorten](https://github.com/bjornmorten)
