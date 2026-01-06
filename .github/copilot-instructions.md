# Python Project Coding Standards

## Code Style
- Follow PEP 8 strictly; use `black` formatter with 88-char line length
- Use type hints for all function signatures and return types
- Prefer f-strings over `.format()` or `%` string formatting

## Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes; `SCREAMING_SNAKE_CASE` for constants
- Prefix private methods/attributes with single underscore `_`

## Best Practices
- Write docstrings (Google style) for all public functions and classes
- Handle exceptions explicitly; avoid bare `except:` clauses
- Prefer list comprehensions over `map()`/`filter()` for readability
- Use beautifulsoup for web scraping, fastapi for backend, streamlit for frontend

## Code Generation Rules
- Always include error handling with specific exception types
- Add logging by using loguru library, not `print()` statements
- Keep functions under 20 lines; extract logic into helper functions
- Generate code shortly, optimization
- All block code (code snippet) in all functions or methods should be separated by a new line and have comments (with #) before each of them.