# Agent Instructions

This document provides instructions for AI agents working on this codebase.

## Code Style

-   All Python code must follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
-   Use `snake_case` for variables, functions, and methods.
-   Use `PascalCase` for classes.
-   All code must be formatted using a tool that respects the `.editorconfig` file.

## Testing

-   All new features must be accompanied by tests.
-   All tests must pass before a pull request will be merged.
-   To run the tests, execute the following command from the root directory:

    ```bash
    python -m pytest
    ```

## Database

-   The database is managed using SQLAlchemy.
-   All database models are defined in `app/db/models.py`.
-   The database is seeded with initial data by the `seed_database` function in `app/api/main.py`.

## AI Service

-   The AI service is used to extract entities from PDF files.
-   The AI service is mocked in the test environment to ensure that tests are not dependent on it.
-   The mock for the AI service is defined in `tests/conftest.py`.
