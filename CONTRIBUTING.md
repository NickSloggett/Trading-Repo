# Contributing to Trading-Repo

Thank you for your interest in contributing to the Trading Development Platform! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for everyone, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race or ethnicity
- Age
- Religion or nationality

### Expected Behavior

- Be respectful and considerate
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Publishing others' private information
- Professional misconduct
- Other conduct inappropriate for a professional setting

## Getting Started

### Prerequisites for Contributors

- Python 3.11+ installed
- Git knowledge
- Docker and Docker Compose (for testing)
- Familiarity with the relevant platform (Pine Script, Java, C++, C#, or Python)

### Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Trading-Repo.git
cd Trading-Repo

# Add upstream remote
git remote add upstream https://github.com/NickSloggett/Trading-Repo.git
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (canonical source: pyproject.toml)
python -m pip install --upgrade pip
pip install -e .[dev]

# Optional: generate a pinned lock artifact when preparing releases
# pip install pip-tools
# pip-compile pyproject.toml --extra dev -o requirements.lock.txt

# Start services
cd data-management/database
docker-compose up -d
cd ../..
```

### Branch Protection and Required Checks

The protected `main` branch should require these checks before merge:

- `CI / Ruff Lint`
- `CI / MyPy Type Check`
- `CI / Pytest (Python 3.11)`
- `CI / Pytest (Python 3.12)`
- `CI / Pytest (Python 3.13)`
- `CI / Security Checks`
- `Dependency Review / Dependency Review`

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**: Found a bug? Report it!
2. **Feature Requests**: Have an idea? Share it!
3. **Code Contributions**: Fix bugs or add features
4. **Documentation**: Improve or add documentation
5. **Examples**: Share trading strategies or examples
6. **Testing**: Help improve test coverage
7. **Reviews**: Review pull requests

### Reporting Bugs

When reporting bugs, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Error messages or logs**
- **Screenshots** if applicable

Use the bug report template:

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 13.0]
- Python Version: [e.g., 3.11]
- Package Versions: [relevant packages]

## Additional Context
Any other information
```

### Suggesting Features

When suggesting features, include:

- **Clear use case**: Why is this needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches
- **Impact**: Who benefits and how?

## Development Workflow

### Branch Naming

Use descriptive branch names:

- `feature/add-alpaca-provider` - New features
- `fix/database-connection-error` - Bug fixes
- `docs/update-getting-started` - Documentation
- `refactor/improve-backtesting` - Code refactoring
- `test/add-provider-tests` - Adding tests

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```bash
feat(data): add Alpaca data provider

Implements a new data provider for Alpaca API with support
for stocks, crypto, and real-time streaming.

Closes #123
```

```bash
fix(backtest): correct commission calculation

Commission was being applied twice in certain scenarios.
Updated calculation to apply once per trade.

Fixes #456
```

### Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge into your main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Formatter**: Black (with default settings)
- **Linter**: flake8, pylint
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Google-style docstrings

Example:

```python
from typing import List, Optional
import pandas as pd


def calculate_returns(
    prices: pd.Series,
    periods: int = 1,
    log_returns: bool = False
) -> pd.Series:
    """
    Calculate returns from price series.
    
    Args:
        prices: Series of prices
        periods: Number of periods for return calculation
        log_returns: Use logarithmic returns if True
        
    Returns:
        Series of returns
        
    Raises:
        ValueError: If prices series is empty
        
    Examples:
        >>> prices = pd.Series([100, 105, 103, 108])
        >>> returns = calculate_returns(prices)
        >>> print(returns)
    """
    if prices.empty:
        raise ValueError("Price series cannot be empty")
    
    if log_returns:
        return np.log(prices / prices.shift(periods))
    else:
        return prices.pct_change(periods)
```

### Code Formatting

```bash
# Format code with Black
black .

# Sort imports
isort .

# Check style
flake8 .

# Type checking
mypy data-management/ python-algorithms/
```

### Platform-Specific Guidelines

#### Pine Script
- Use v5 syntax
- Include `//@version=5` at top
- Add descriptive comments
- Use input() for parameters
- Follow TradingView naming conventions

#### Java (MotiveWave)
- Follow Java conventions
- Use @StudyHeader annotation
- Document all public methods
- Handle errors gracefully

#### C++ (Sierra Chart)
- Follow ACSIL guidelines
- Use SCDLLName for study name
- Comment complex calculations
- Optimize performance

#### C# (NinjaTrader)
- Follow C# conventions
- Use [NinjaScriptProperty] attributes
- Document properties
- Handle State changes properly

## Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Backtest tests**: Validate strategy logic
- **Data quality tests**: Verify data integrity

Example unit test:

```python
import pytest
from data_management.storage.timescale_handler import TimescaleHandler


class TestTimescaleHandler:
    """Test suite for TimescaleHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance for testing"""
        return TimescaleHandler(
            host='localhost',
            database='trading_data_test'
        )
    
    def test_insert_ohlc_data(self, handler, sample_data):
        """Test OHLC data insertion"""
        count = handler.insert_ohlc_data(
            sample_data,
            symbol='TEST',
            timeframe='1d'
        )
        
        assert count == len(sample_data)
        
        # Verify data was inserted
        retrieved = handler.query_ohlc_data('TEST', '1d')
        assert len(retrieved) == count
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_timescale_handler.py

# Run with coverage
pytest --cov=data-management --cov-report=html

# Run fast tests only
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

### Test Coverage

- Aim for **80%+ coverage** for new code
- Critical paths should have **100% coverage**
- Include edge cases and error handling
- Test with different data types and sizes

## Documentation

### Code Documentation

- **Docstrings**: Every public function/class
- **Type hints**: For function parameters and returns
- **Comments**: Explain complex logic, not obvious code
- **README files**: In each major directory

### Documentation Style

Use Google-style docstrings:

```python
def my_function(arg1: int, arg2: str, arg3: Optional[bool] = None) -> List[str]:
    """
    Brief description of function.
    
    More detailed description if needed. Can span multiple lines
    and include usage examples or important notes.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        arg3: Optional description. Defaults to None.
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When and why this is raised
        TypeError: When and why this is raised
        
    Examples:
        >>> result = my_function(42, "test")
        >>> print(result)
        ['expected', 'output']
        
    Note:
        Any important notes or warnings
    """
    pass
```

### Updating Documentation

When adding features:
1. Update relevant README files
2. Add docstrings to new code
3. Update API reference docs
4. Add examples if applicable
5. Update CHANGELOG.md

## Pull Request Process

### Before Submitting

1. **Update your fork** with latest upstream changes
2. **Run tests** and ensure they pass
3. **Format code** with Black and isort
4. **Update documentation** as needed
5. **Add tests** for new functionality
6. **Update CHANGELOG.md** with your changes

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**:
   - Use descriptive title
   - Fill out PR template
   - Link related issues
   - Add labels if applicable

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring
   - [ ] Performance improvement
   
   ## Related Issues
   Closes #issue_number
   
   ## Testing
   - [ ] Added unit tests
   - [ ] Added integration tests
   - [ ] Manual testing performed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests pass locally
   
   ## Screenshots (if applicable)
   
   ## Additional Notes
   ```

### Review Process

1. **Automated checks** run (CI/CD)
2. **Code review** by maintainers
3. **Feedback** and requested changes
4. **Approval** from at least one maintainer
5. **Merge** into main branch

### After Merge

- Delete your branch
- Update your fork
- Celebrate! 🎉

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Explain the "why" behind suggestions
- Approve when ready, don't nitpick
- Test the changes if possible

### As an Author

- Respond to all comments
- Don't take criticism personally
- Ask for clarification if needed
- Make requested changes promptly

## Getting Help

### Resources

- **Documentation**: Check `/docs` directory
- **Examples**: See `examples/` and `python-algorithms/strategies/`
- **GitHub Discussions**: Ask questions
- **GitHub Issues**: Search existing issues

### Contact

- **GitHub**: [@NickSloggett](https://github.com/NickSloggett)
- **Issues**: [Create an issue](https://github.com/NickSloggett/Trading-Repo/issues)
- **Discussions**: [Start a discussion](https://github.com/NickSloggett/Trading-Repo/discussions)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Documentation credits

Thank you for contributing! 🙏

---

**License**: By contributing, you agree that your contributions will be licensed under the MIT License.




