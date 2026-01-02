# Contributing to JobPacker

Thank you for your interest in contributing to JobPacker! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive in all interactions. We're building tools to help people find jobs - let's keep the community positive.

## Getting Started

### Prerequisites

- **Python 3.12** (required - numpy/jobspy compatibility issues with 3.13+)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/JobPacker.git
   cd JobPacker
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   py -3.12 -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run without coverage requirement (useful during development)
pytest --no-cov
```

### Code Formatting

We use **black** for formatting and **ruff** for linting.

```bash
# Format code
black jobpacker.py tests/

# Check formatting (CI will fail if not formatted)
black --check jobpacker.py tests/

# Lint code
ruff check jobpacker.py tests/

# Auto-fix lint issues
ruff check --fix jobpacker.py tests/
```

### Before Submitting

1. **Format your code**: `black jobpacker.py tests/`
2. **Run linter**: `ruff check jobpacker.py tests/`
3. **Run tests**: `pytest`
4. **Ensure 80%+ coverage**: Tests must maintain minimum coverage

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clear, focused commits
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run full test suite
pytest

# Check formatting
black --check jobpacker.py tests/

# Run linter
ruff check jobpacker.py tests/
```

### 4. Submit Pull Request

- Fill out the PR template
- Link any related issues
- Describe your changes clearly

### 5. Review Process

- CI must pass (tests, coverage, formatting, linting)
- At least one maintainer review required
- Address feedback promptly

## What to Contribute

### Good First Issues

Look for issues labeled `good first issue` - these are beginner-friendly tasks.

### Feature Ideas

- Additional job board support
- New export formats
- UI/UX improvements
- Documentation improvements
- Test coverage improvements

### Bug Reports

When reporting bugs, include:

1. Python version (`python --version`)
2. Operating system
3. Steps to reproduce
4. Expected vs actual behavior
5. Error messages/tracebacks

## Code Style Guide

### Python

- Follow PEP 8 (enforced by black/ruff)
- Use type hints where helpful
- Write docstrings for functions
- Keep functions focused and small

### Testing

- Test file naming: `test_*.py`
- Test function naming: `test_*`
- Use descriptive test names
- One assertion per test (when practical)
- Use fixtures for shared setup

### Commits

- Use present tense ("Add feature" not "Added feature")
- Keep commits focused on single changes
- Reference issues when relevant (`Fixes #123`)

## Questions?

- Open an issue for questions
- Check existing issues first
- Be patient - maintainers are volunteers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
