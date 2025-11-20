# Agent Instructions

This document provides instructions for AI agents working on this codebase.

## 📘 Documentation for Jules (AI Context)

> **IMPORTANT**: Before starting any task, refer to the detailed documentation in the `.jules-docs/` folder.

*   **[System Architecture](.jules-docs/SYSTEM_ARCHITECTURE.md)**: High-level diagrams, dependency graph, and component interactions.
*   **[Data Models](.jules-docs/DATA_MODELS.md)**: Database schema, Pydantic DTOs, and JSON interfaces.
*   **[Critical Flows](.jules-docs/CRITICAL_FLOWS.md)**: Detailed algorithms for ingestion, notification, and status logic.
*   **[Dev Protocols](.jules-docs/DEV_PROTOCOLS.md)**: Coding standards, error handling strategies, and testing requirements.

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
-   See `.jules-docs/DATA_MODELS.md` for schema details.
