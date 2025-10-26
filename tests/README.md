# Tests Directory

This directory contains all test files and examples for the Option Chain Live Data Service.

## Files

### `test_installation.py`

Comprehensive installation and functionality test script that verifies:

- Configuration loading and validation
- Module imports
- Service initialization
- Basic functionality

**Usage:**

```bash
python tests/test_installation.py
```

### `example.py`

Example usage demonstrations showing how to:

- Initialize servicess
- Load option chain data
- Start live streaming
- Handle data storage
- Use different service methods

**Usage:**

```bash
python tests/example.py
```

## Running Tests

### From Project Root

```bash
# Run installation test
python tests/test_installation.py

# Run examples
python tests/example.py
```

### From Tests Directory

```bash
cd tests
python test_installation.py
python example.py
```

## Test Structure

The tests directory is organized as follows:

```
tests/
├── __init__.py          # Package initialization
├── test_installation.py # Installation verification tests
├── example.py           # Usage examples and demonstrations
└── README.md           # This documentation file
```

## Import Path Handling

Test files use dynamic path resolution to import modules from the parent directory:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

This ensures tests can be run from either the project root or the tests directory.

## Adding New Tests

When adding new test files:

1. Place them in the `tests/` directory
2. Add the import path resolution code at the top
3. Import required modules from the parent directory
4. Update this README with documentation

## Test Categories

### Installation Tests

- Configuration validation
- Module import verification
- Service initialization
- Basic functionality checks

### Example Demonstrations

- Service usage patterns
- Data handling examples
- Error handling demonstrations
- Best practices examples

## Notes

- All tests are designed to run without requiring actual API credentials
- Tests focus on code structure and basic functionality
- Examples demonstrate real-world usage patterns
- Both files can be used for learning and verification purposes
