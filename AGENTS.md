# Agent Instructions

This document provides instructions for AI agents working on this codebase.

## 📘 Documentation for Jules (AI Context)

> **IMPORTANT**: Before starting any task, refer to the detailed documentation in the `.jules-docs/` folder.

*   **[Project Overview](.jules-docs/project_overview.md)**: Architecture, directory structure, and patterns.
*   **[Business Logic](.jules-docs/business_logic.md)**: Certificate lifecycle, status rules, and validities.
*   **[AI Integration](.jules-docs/ai_integration.md)**: How the Gemini prompt works and how to extend it.
*   **[Testing Guide](.jules-docs/testing_guide.md)**: Mocking strategies and test execution.

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
-   The database is seeded with initial data by the `seed_database` function in `app/db/seeding.py`.

## AI Service

-   The AI service is used to extract entities from PDF files.
-   The AI service is mocked in the test environment to ensure that tests are not dependent on it.
-   See `.jules-docs/ai_integration.md` for prompt details.
