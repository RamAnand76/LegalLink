# Contributing to LegalLink

We welcome contributions! Please follow these standards to maintain code quality.

## Branching Strategy

- **main**: Production-ready code. No direct commits.
- **develop**: Integration branch for new features.
- **feature/feature-name**: Use this for new features (e.g., `feature/user-auth`).
- **bugfix/bug-name**: Use this for bug fixes (e.g., `bugfix/login-error`).

## Workflow

1. Create a new branch from `develop`.
2. Commit your changes with descriptive messages.
3. Keep your branch updated with `develop` using `git rebase develop`.
4. Open a Pull Request (PR) to `develop`.
5. Ensure all tests pass and a code review is completed.

## Coding Standards

- **Python**: Follow PEP 8 guidelines.
- **FastAPI**: 
  - Use type hints for all function arguments and return types.
  - Use Pydantic schemas for request/response validation.
  - Keep logic in `crud/` or `services/`, not in the endpoint functions.
  - Use FastAPI's Dependency Injection system for shared logic (e.g., database sessions).
- **Naming**: 
  - Use `snake_case` for variables and functions.
  - Use `PascalCase` for classes and Pydantic models.

## Pull Request Guidelines

- Provide a clear description of the changes.
- Link any relevant issues.
- Include screenshots or API responses for UI/API changes.
- Ensure the build passes.
