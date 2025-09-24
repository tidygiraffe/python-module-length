# python-module-length

A self-contained pre-commit hook that enforces a maximum line count per Python module.

## Features
- Fails commits when any Python file exceeds a configurable line limit
- Clear output grouped by test files vs application modules
- Zero dependencies, pure Python

## Installation
Add to your `.pre-commit-config.yaml` (after publishing this repo):

```yaml
repos:
  - repo: https://github.com/tidygiraffe/python-module-length
    rev: v0.1.0
    hooks:
      - id: python-module-length
        args: ["--max-lines=1000"]
```

## Local testing
Run directly as a CLI:

```bash
python-module-length --max-lines 1000 path/to/file.py
```


## License
MIT
