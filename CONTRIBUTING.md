# Contributing to NiFi IDOL Workarounds

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a standard code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report:

1. **Check existing issues** to avoid duplicates
2. **Use the search function** to see if the problem has already been reported
3. If you find a closed issue that seems similar, open a new one and reference it

When creating a bug report, include:

- **Clear title** describing the issue
- **NiFi version** and Python version
- **FFmpeg version** (for mpg_to_mp3_chunks.py issues)
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Sample files** or characteristics (file format, size, duration)
- **Error logs** from NiFi or processor output
- **Screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! When suggesting an enhancement:

1. **Use a clear title** for the issue
2. **Provide a detailed description** of the enhancement
3. **Explain why** this enhancement would be useful
4. **Provide examples** of how it would work
5. **List alternative solutions** you've considered

### Contributing Code

We welcome code contributions! Areas where contributions are especially valuable:

1. **New processors** for other IDOL/KeyView limitations
2. **STT engine integrations** (Google, Azure, Deepgram, etc.)
3. **Performance optimizations**
4. **Bug fixes**
5. **Documentation improvements**
6. **Test coverage**

## Development Setup

### Prerequisites

```bash
# Install Python 3.6+
python --version

# Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
# or
brew install ffmpeg  # macOS

# Verify FFmpeg
ffmpeg -version
```

### Clone Repository

```bash
git clone https://github.com/joesoc/nifi-idol-workarounds.git
cd nifi-idol-workarounds
```

### Local Testing

Test processors outside NiFi:

```bash
# Test the chunker
python examples/test_chunker.py /path/to/test.mpg

# Run with Python directly
python processors/mpg_to_mp3_chunks.py
```

### Development Tools (Optional)

```bash
# Install development dependencies
pip install pytest pytest-cov pylint black

# Run linting
pylint processors/*.py

# Format code
black processors/*.py examples/*.py

# Run tests (when test suite exists)
pytest tests/
```

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters** (for code), **80 recommended**
- Use **meaningful variable names**
- Add **docstrings** to all functions and classes

### Processor Standards

When creating new processors:

1. **Use stdlib only** when possible (avoid external dependencies)
2. **Include comprehensive docstrings** at module and function level
3. **Handle errors gracefully** with try/except blocks
4. **Clean up resources** in finally blocks
5. **Provide mock functions** for standalone testing
6. **Log verbosely** using logInfo/logWarn/logError
7. **Document attributes** (input and output)

### Example Processor Structure

```python
"""
Processor Name - NiFi ExecuteScript Processor
=============================================

Brief description.

Requirements:
    - List dependencies

Attributes:
    Input:
        - attr: Description
    Output:
        - attr: Description

Routes:
    - success: Description
    - failure: Description
"""

import os
import sys

# NiFi compatibility layer
try:
    from idolnifi import *
except ImportError:
    def logInfo(*args, **kwargs):
        print("INFO:", *args, **kwargs, file=sys.stderr)
    def logError(*args, **kwargs):
        print("ERROR:", *args, **kwargs, file=sys.stderr)

def handler(context, session, flowfile):
    """
    Main handler function.
    
    Args:
        context: NiFi processor context
        session: NiFi session
        flowfile: Input flowfile
    """
    # Implementation
    pass
```

### Documentation Standards

- Use **Markdown** for all documentation
- Include **code examples** where appropriate
- Add **screenshots** for UI changes
- Keep **line length reasonable** (~80-100 chars for readability)
- Use **tables** for structured data
- Include **links** to related documentation

## Testing

### Manual Testing

Before submitting a PR:

1. **Test locally** with sample files
2. **Test in NiFi** if possible
3. **Verify error handling** with invalid inputs
4. **Check resource cleanup** (no temp file leaks)
5. **Test edge cases** (empty files, corrupted files, etc.)

### Test Files

When adding test files:

- Use **small sample files** (< 1 MB when possible)
- Document **file characteristics** (format, duration, codec)
- Do not commit **large binary files** to the repository
- Provide **download links** for large test files

### Test Script Template

```python
#!/usr/bin/env python3
"""Test script for YourProcessor"""

import sys
from processors.your_processor import handler

class MockSession:
    """Mock NiFi session"""
    def __init__(self):
        self.transferred = []
    
    def transfer(self, flowfile, relationship):
        self.transferred.append((flowfile, relationship))

class MockFlowFile:
    """Mock FlowFile"""
    def __init__(self):
        self.attributes = {}
    
    def getAttribute(self, key):
        return self.attributes.get(key)

def test_processor():
    """Test processor logic"""
    session = MockSession()
    flowfile = MockFlowFile()
    flowfile.attributes['test.attr'] = 'value'
    
    handler(None, session, flowfile)
    
    assert len(session.transferred) > 0
    print(f"✓ Test passed: {len(session.transferred)} outputs")

if __name__ == '__main__':
    test_processor()
```

## Documentation

### When to Update Documentation

Update documentation when you:

- Add a new processor
- Change processor behavior
- Add new features
- Fix bugs that affect documented behavior
- Add examples or integration patterns

### Documentation Files to Update

| Change | Files to Update |
|--------|----------------|
| New processor | `processors/README.md`, main `README.md`, `docs/README.md` |
| Configuration change | `examples/nifi_configuration.md` |
| New integration | Add new file in `examples/`, update `examples/README.md` |
| Bug fix | `CHANGELOG.md` |

### Documentation Review

Before submitting:

1. **Run spell check** on documentation
2. **Verify links** are not broken
3. **Test code examples** if applicable
4. **Review formatting** (render Markdown locally)

## Pull Request Process

### Before Submitting

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** following coding standards
3. **Test thoroughly** (manually and with test scripts)
4. **Update documentation** as needed
5. **Update CHANGELOG.md** with your changes
6. **Commit with clear messages**: `git commit -m "Add feature: description"`

### Commit Message Format

```
Add feature: Brief description

- Detailed point 1
- Detailed point 2

Fixes #123
```

Examples:
- `Add processor: Text encoding converter`
- `Fix: Resource leak in error handling`
- `Docs: Update Whisper integration example`
- `Perf: Optimize FFmpeg command for faster extraction`

### Creating Pull Request

1. **Push your branch**: `git push origin feature/your-feature-name`
2. **Create PR** on GitHub
3. **Fill out PR template** with:
   - Description of changes
   - Testing performed
   - Related issues
   - Documentation updates
4. **Link related issues** using keywords (Fixes #123, Closes #456)

### PR Review Process

1. **Automated checks** will run (if configured)
2. **Maintainers will review** your code
3. **Address feedback** by pushing new commits
4. **PR will be merged** when approved

### After Merge

1. **Delete your feature branch** (optional)
2. **Update your fork** with upstream changes
3. **Celebrate!** 🎉

## Additional Resources

- [NiFi Documentation](https://nifi.apache.org/docs.html)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [IDOL Documentation](https://www.microfocus.com/documentation/idol/)

## Questions?

If you have questions not covered here:

1. Check existing documentation in `docs/` and `examples/`
2. Search through existing issues
3. Open a new issue with the `question` label

Thank you for contributing! 🙏
