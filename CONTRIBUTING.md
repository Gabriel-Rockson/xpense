# Contributing to xpense

Thank you for your interest in contributing to xpense!

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/Gabriel-Rockson/xpense.git
cd xpense
```

2. Install dependencies:
```bash
uv sync
# or
pip install -e .
```

3. Run the CLI locally:
```bash
uv run xpense --help
# or
python -m xpense.main
```

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated releases and changelog generation.

### Format

```
<type>: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **chore**: Maintenance tasks, dependency updates
- **refactor**: Code refactoring without feature changes
- **test**: Adding or updating tests
- **style**: Code style changes (formatting, semicolons, etc.)
- **perf**: Performance improvements

### Examples

**Feature:**
```
feat: add support for recurring expenses
```

**Bug fix:**
```
fix: correct balance calculation for monthly reports
```

**Documentation:**
```
docs: update installation instructions
```

**Breaking change:**
```
feat!: change default storage location to ~/.xpense

BREAKING CHANGE: Storage directory moved from ~/.expenses to ~/.xpense
```

## Release Process

Releases are automated using [release-please](https://github.com/googleapis/release-please):

1. Make commits following conventional commit format
2. Push to `main` branch
3. Release-please creates/updates a release PR
4. Review and merge the release PR
5. Release is created automatically
6. Package is published to PyPI automatically

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Use conventional commit messages
4. Push to your fork
5. Open a pull request against `main`

## Questions?

Feel free to open an issue for questions or discussions!