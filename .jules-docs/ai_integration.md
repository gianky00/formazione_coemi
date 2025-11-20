# AI Integration & Prompt Engineering

## Overview

The AI service (`app/services/ai_extraction.py`) uses **Google Gemini 2.5 Pro** to extract entities and classify documents in a **single-pass** operation.

> **Correction**: Previous documentation might refer to a "two-phase" process. The current implementation uses a single, robust prompt that handles both extraction and classification simultaneously to reduce latency and API costs.

## The Prompt Strategy

The prompt is constructed dynamically in `_generate_prompt()` and consists of:

1.  **Role Definition**: "Sei un assistente AI specializzato..."
2.  **Extraction Goal**: Extract specific fields (`nome`, `data_nascita`, `corso`, `data_rilascio`, `data_scadenza`).
3.  **Classification Goal**: Assign one of the `CATEGORIE_STATICHE`.
4.  **Context & Examples**:
    *   A list of allowed categories.
    *   Few-shot examples (e.g., mapping "Addetto Antincendio" -> "ANTINCENDIO").
5.  **Absolute Rules ("REGOLE DI CLASSIFICAZIONE ASSOLUTE")**:
    *   Hard constraints to solve edge cases (e.g., distinguishing "NOMINA PREPOSTO" from the "PREPOSTO" course).
    *   Specific extraction rules for non-standard documents (e.g., field "4b" for Patents).

## Handling AI Responses

*   **JSON Output**: The model is instructed to return purely JSON.
*   **List Handling**: Sometimes the model wraps the JSON in a list (`[...]`). The code (`extract_entities_with_ai`) automatically unwraps this (`data = data[0]`).
*   **Fallback**: If the extracted category is not in the static allowlist, it defaults to `"ALTRO"`.

## Adding New Categories

To add a new document category:
1.  Add the category string to `CATEGORIE_STATICHE` in `app/core/constants.py`.
2.  Update `app/db/seeding.py` to define its `validita_mesi`.
3.  Update the prompt in `app/services/ai_extraction.py`:
    *   Add it to the `esempi_categorie` list.
    *   If it has special rules (e.g., unique expiration field), add a rule to "REGOLE DI CLASSIFICAZIONE ASSOLUTE".
