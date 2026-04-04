# Contributing to Sudoku Automation System

First off, thank you for considering contributing to Sudoku Automation System! It's people like you that make this such a great tool.

## Code of Conduct

Our project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the [issue list](https://github.com/yourusername/sudoku-automation/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, browser)

### ✨ Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the expected behavior**
* **Explain why this enhancement would be useful**

### 📝 Pull Requests

* Fill in the required template
* Follow the Python and JavaScript style guides
* Include appropriate test cases
* End all files with a newline
* Avoid platform-dependent code

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/sudoku-automation.git
   cd sudoku-automation
   ```

3. **Add upstream remote** to keep your fork updated:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/sudoku-automation.git
   ```

4. **Create a branch** for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/bug-description
   ```

5. **Set up development environment** (Backend):
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest pytest-cov pylint black  # Dev dependencies
   ```

## Styleguides

### Git Commit Messages

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (formatting, missing semicolons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to build process, dependencies, or tooling

**Examples:**
```
feat(solver): add beam search algorithm for faster solutions

docs(readme): update installation instructions for Windows users

fix(api): handle edge case for empty board validation
Fixes #123

refactor(services): optimize digit recognition pipeline
BREAKING CHANGE: removed legacy digit_recognition_old.py
```

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following tools:

* **Formatter**: Black
  ```bash
  black backend/
  ```

* **Linter**: Pylint
  ```bash
  pylint backend/app
  ```

* **Type checking**: Mypy (optional)
  ```bash
  mypy backend/app
  ```

**Style Guidelines:**
- Use meaningful variable names
- Max line length: 100 characters
- Use docstrings for all functions and classes
- Write comments for complex logic
- Keep functions focusing on a single responsibility

Example:
```python
def validate_board(board: List[List[int]]) -> bool:
    """
    Validate a Sudoku board against all constraints.
    
    Args:
        board: 9x9 list of integers (0 for empty cells)
        
    Returns:
        True if board is valid, False otherwise
        
    Raises:
        ValueError: If board format is invalid
    """
    if not isinstance(board, list) or len(board) != 9:
        raise ValueError("Board must be a 9x9 list")
    
    # Check rows, columns, and boxes
    # ...
    return True
```

### JavaScript Code Style

* Use 2 spaces for indentation
* Use `const` and `let`, avoid `var`
* Use meaningful variable names
* Add JSDoc comments for complex functions

```javascript
/**
 * Parse the Sudoku grid from the DOM
 * @returns {number[][]} 9x9 grid array
 */
const parseGrid = () => {
  const grid = [];
  const cells = document.querySelectorAll('[data-row]');
  // ...
  return grid;
};
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_solver.py -v

# Run tests matching a pattern
pytest -k "test_validation" -v
```

**Test File Structure:**
```
backend/tests/
├── test_solver.py          # Solver algorithm tests
├── test_image_processing.py # Image detection tests
├── test_digit_recognition.py # ML model tests
└── conftest.py             # Shared fixtures
```

**Example Test:**
```python
import pytest
from app.services.sudoku_solver import solve_board

def test_solve_valid_board():
    """Test solving a valid Sudoku board."""
    board = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        # ... rest of board
    ]
    
    solution = solve_board(board)
    
    assert solution is not None
    assert len(solution) == 9
    # Validate solution is correct
```

## Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Write/Update Tests**: Ensure all tests pass:
   ```bash
   pytest
   ```

3. **Format Code**:
   ```bash
   black backend/
   pylint backend/app
   ```

4. **Commit Your Changes**:
   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

5. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - List of changes made

7. **Wait for Review**: Maintainers will review your PR and may request changes

## Additional Notes

### Issue and Pull Request Labels

Issues and PRs are organized using labels:

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested
* `wontfix` - This will not be worked on

### Recognition

Contributors will be recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- README.md acknowledgments
- Release notes

## Questions?

Don't hesitate to:
- Open an issue with the `question` label
- Start a GitHub Discussion
- Contact [maintainer email]

Happy contributing! 🎉
