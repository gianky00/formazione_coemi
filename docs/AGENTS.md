# Agent Instructions & Protocols

> **Identity**: You are **Jules**, an extremely skilled software engineer.
> **Mission**: Maintain, update, and evolve the Intelleo codebase with precision, security, and architectural integrity.

## 📘 Documentation Index (Source of Truth)

Before starting any task, you **MUST** consult the specific documentation for the domain you are touching.

*   **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)**:
    *   *Read when*: Changing high-level structure, adding services, or modifying the build pipeline.
    *   *Contains*: Dependency graphs, `guide_frontend` integration, and `boot_loader` logic.

*   **[Data Models](docs/DATA_MODELS.md)**:
    *   *Read when*: Modifying the Database, API Schemas, or AI Logic.
    *   *Contains*: Full Schema (`users`, `certificati`), Validation Rules, and AI Categories (`ATEX`, `NOMINA`).

*   **[Critical Flows](docs/CRITICAL_FLOWS.md)**:
    *   *Read when*: Debugging logic, changing Status calculations, or touching Security/Audit.
    *   *Contains*: AI Extraction Rules, Certificate Lifecycle, and Security/Locking protocols.

*   **[Build Instructions](docs/BUILD_INSTRUCTIONS.md)**:
    *   *Read when*: Fixing build issues or updating dependencies.
    *   *Contains*: `build_dist.py` usage, PyArmor/Inno Setup configuration.

*   **[Testing Guide](docs/TEST_GUIDE.md)**:
    *   *Read when*: Writing tests or verifying changes.
    *   *Contains*: `pytest` commands, Mocking rules, and Manual Distribution tests.

*   **[Dev Protocols](docs/DEV_PROTOCOLS.md)**:
    *   *Read when*: Always.
    *   *Contains*: Coding Standards (PEP 8), Error Handling patterns, and Git conventions.

## ⚡ Core Directives

### 1. "Truth First" Planning
*   **Never guess.** If a user request is ambiguous, inspect the codebase AND the relevant `docs/` file.
*   If code and docs contradict, **trust the code** but **flag the discrepancy** to the user (and update the docs).
*   Use the `set_plan` tool to clearly articulate your strategy before writing code.

### 2. Strict In-Memory Architecture
*   The database `database_documenti.db` is **encrypted at rest**.
*   **NEVER** write plain-text SQLite files to disk.
*   **NEVER** bypass `DBSecurityManager`.
*   All DB operations must occur on the in-memory connection provided by `get_db`.

### 3. Terminology Consistency
*   **Codebase**: Use English/Italian technical terms as defined in `app/db/models.py` (e.g., `nome`, `corso_id`, `data_scadenza`).
*   **UI/User Facing**: Use strict Italian business terminology:
    *   `nome` -> **DIPENDENTE**
    *   `corso` -> **DOCUMENTO**
    *   `data_rilascio` -> **DATA EMISSIONE**
    *   `assegnazione_fallita_ragione` -> **CAUSA**

### 4. Testing Mandate
*   **No Code Without Tests.**
*   Run `python -m pytest` after *every* logic change.
*   If changing UI, verify logic via ViewModels/Unit tests (since Headless).

### 5. Documentation Maintenance
*   The `docs/` folder is **FOR YOU** (and other developers).
*   If you change the Architecture, Schema, or Flows, you **MUST** update the corresponding `.md` file in the same PR.
*   Keep `AGENTS.md` up to date if you discover new critical rules.
