# Contributing to FHIR Client

Thank you for your interest in contributing to the FHIR Client project! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and benefits
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Add tests** for any new functionality
4. **Ensure all tests pass** by running `pytest tests/`
5. **Update documentation** if needed
6. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/fhir-client.git
cd fhir-client

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and modular
- Use meaningful variable and function names

### Testing

- Write unit tests for new features
- Maintain or improve code coverage
- Test against multiple Python versions if possible
- Use mocks for external API calls in tests

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

Example:
```
Add search functionality for Observation resources

- Implement search with multiple parameters
- Add unit tests for search operations
- Update documentation with search examples
```

## Code of Conduct

Be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## Questions?

Feel free to open an issue for any questions about contributing!
