# MyPy Error Resolution - Phase 2: `src/core` + `src/bots`

## Context

This is a **continuation** of an ongoing MyPy strict-mode cleanup for the **SyncroJob Enterprise** project (PyQt6 + Selenium automation platform).

**Phase 1** (completed) resolved all MyPy errors in `src/gui/` (~25 errors across 15 files).
**Phase 2** (this task) targets the remaining errors in `src/core/` and `src/bots/`.

The MyPy configuration is strict (`pyproject.toml > [tool.mypy]`):
- `disallow_any_generics = true` (bare `list`, `dict`, `tuple` are errors)
- `warn_return_any = true` + `warn_unreachable = true`
- `warn_unused_ignores = true`
- `show_error_codes = true`

---

## Objective

Fix **all remaining MyPy errors** in `src/core/` and `src/bots/` without changing runtime behavior.

**Run command**: `python -m mypy src --no-incremental`

---

## Errors to Fix (grouped by file)

### TIER 1 - Trivial (missing imports, bare generics)

These are mechanical fixes: add `from typing import Any` where missing, and parameterize bare generic types.

#### `src/core/telegram/handlers/commands.py:46` [name-defined]
```
error: Name "Any" is not defined
```
**Fix**: Add `from typing import Any` at the top of the file.

#### `src/core/telegram_bridge.py:484` [name-defined]
```
error: Name "cast" is not defined
```
**Fix**: Add `cast` to the existing `from typing import ...` import.

#### `src/core/data_synchronizer.py` (7 errors) [type-arg]
Lines: 74, 107, 150, 195, 238, 247, 258.
All are `list[tuple]` -> **change to** `list[tuple[Any, ...]]`.
Ensure `from typing import Any` is imported.

#### `src/core/contabilita_queries.py` (5 errors) [type-arg]
Lines: 32, 50, 80, 96, 112.
All are `-> list[tuple]` -> **change to** `-> list[tuple[Any, ...]]`.
Ensure `from typing import Any` is imported.

#### `src/core/contabilita_manager.py` (2 errors) [type-arg]
- Line 204: `list[dict]` -> `list[dict[str, Any]]`
- Line 213: `dict[str, list[dict]]` -> `dict[str, list[dict[str, Any]]]`

#### `src/core/contabilita_worker.py:64` [type-arg]
`-> dict` -> `-> dict[str, Any]`

#### `src/bots/portale_fornitori/prenota_bp/bot.py` (3 type-arg errors)
- Line 54: `row: dict` -> `row: dict[str, Any]`
- Line 96: `-> list[dict]` -> `-> list[dict[str, Any]]`
- Line 105: `row: dict` -> `row: dict[str, Any]`

#### `src/bots/portale_fornitori/scarico_ts/bot.py` (4 type-arg errors)
- Line 48: `-> list` -> `-> list[dict[str, Any]]`
- Line 122: `list[dict]` -> `list[dict[str, Any]]`
- Line 141: `list[dict]` -> `list[dict[str, Any]]`
- Line 324: `files_before: set` -> `files_before: set[str]`

#### `src/bots/portale_fornitori/scarico_ts/scarico_ts_bot.py:32` [type-arg]
`-> list` -> `-> list[dict[str, Any]]`

#### `src/bots/portale_fornitori/dettagli_oda/bot.py:111` [type-arg]
`row: dict` -> `row: dict[str, Any]`

#### `src/bots/portale_fornitori/carico_ts/bot.py:28` [type-arg]
`-> list` -> `-> list[dict[str, Any]]`

---

### TIER 2 - Type Fixes (assignment, no-any-return)

#### `src/core/contabilita_worker.py:35` [assignment]
```python
self.start_time = time.time()  # float assigned to int
```
**Fix**: Change the declaration of `self.start_time` to `float` type:
```python
self.start_time: float = 0
```
Or if it was declared as `int`, change the type annotation to `float`.

#### `src/core/logging/alert_manager.py:68` [assignment]
```python
self._telegram_service = TelegramService()  # assigned to variable typed as None
```
**Fix**: Change the type annotation of `self._telegram_service` from `None` to `TelegramService | None`:
```python
self._telegram_service: TelegramService | None = None
```

#### `src/core/logging/alert_manager.py:239` [no-any-return]
```python
return AlertManager.instance()  # Returning Any
```
**Fix**: Add explicit cast or type annotation:
```python
result: AlertManager = AlertManager.instance()
return result
```
Or fix `instance()` return type to `-> "AlertManager"` if it's using a generic singleton pattern.

#### `src/core/lyra_client.py:195,249` [no-any-return]
```python
return result["candidates"][0]["content"]["parts"][0]["text"]  # returns Any
```
**Fix**: Add `str()` cast:
```python
return str(result["candidates"][0]["content"]["parts"][0]["text"])
```

#### `src/bots/portale_fornitori/dettagli_oda/bot.py:106` [no-any-return]
```python
return rows  # Returning Any from function declared to return list[dict[str, Any]]
```
**Fix**: Add explicit cast: `return list(rows)` or annotate `rows` properly where it's assigned.

#### `src/bots/portale_fornitori/prenota_bp/bot.py:102-103` [no-any-return]
```python
return data.get("rows", [])  # line 102
return data                    # line 103
```
**Fix**: The `data` parameter is `Any`. Cast the returns:
```python
rows: list[dict[str, Any]] = data.get("rows", [])
return rows
```
```python
result: list[dict[str, Any]] = data
return result
```

---

### TIER 3 - Structural Fixes (union-attr, override, unreachable)

#### `src/core/telegram/service.py` (12 errors) [union-attr]
Lines: 276-311. All are `self.app.bot` or `self.app.initialize()` where `self.app` is typed `Application[...] | None`.

**Fix pattern**: Add a single `assert self.app is not None` guard at the top of each method that uses `self.app`, BEFORE the first access. Example:
```python
async def send_message(self, chat_id: str, text: str, ...):
    assert self.app is not None
    if not self.app.bot:
        await self.app.initialize()
    ...
```
Identify the 3 methods (they look like `send_message`, `send_photo`, `send_document`) and add `assert self.app is not None` as the first line of the `try` block in each.

#### `src/bots/safework/base.py:20` [override]
```python
def _attendi_scomparsa_overlay(self, timeout_secondi: int = 120) -> bool:
```
Supertype defines argument as `int | None`. This violates Liskov substitution.

**Fix**: Match the supertype signature:
```python
def _attendi_scomparsa_overlay(self, timeout_secondi: int | None = 120) -> bool:
```
Then handle `None` internally if needed (`timeout_secondi = timeout_secondi or 120`).

#### `src/bots/safework/pdl/bot.py:8` [unused-ignore]
```python
import fitz  # type: ignore # PyMuPDF
```
**Fix**: Remove the `# type: ignore` comment. If `fitz` is in the mypy overrides for ignored imports, the ignore is redundant. Check the `[[tool.mypy.overrides]]` in `pyproject.toml` - `fitz` should be listed there. If it's not, add it to the override list instead of using inline ignore.

#### `src/bots/portale_fornitori/scarico_ts/scarico_ts_bot.py:60-61` [unreachable]
```python
if isinstance(data, dict):  # unreachable: data is list[dict[str, Any]]
    rows = data.get("rows", [])
```
The `execute()` or `run()` method signature types `data` as `list[dict[str, Any]]`, so the `isinstance(data, dict)` check is unreachable.

**Fix**: Change the method's `data` parameter type to `Any` (since it actually receives either a list or a dict at runtime), OR remove the dead `isinstance` branch if it's truly never called with a dict. Check callers to decide.

#### `src/bots/portale_fornitori/scarico_ts/bot.py:91` [unreachable]
Same pattern as above. The `isinstance(data, dict)` check on a `list`-typed parameter.

**Fix**: Same approach - either widen the type to `Any` or `list[dict[str, Any]] | dict[str, Any]`, or remove the dead branch.

#### `src/bots/portale_fornitori/timbrature/storage.py:347` [operator]
```python
row["data"] = data_val.date().isoformat()
# error: "ndarray[tuple[int], dtype[object_]]" not callable
```
**Fix**: The `data_val` comes from a pandas operation and is being treated as a scalar datetime, but mypy infers it as an ndarray. Cast it explicitly:
```python
import pandas as pd
ts = pd.Timestamp(data_val)
row["data"] = ts.date().isoformat()
```

---

## Rules & Conventions

1. **Do NOT change runtime behavior**. All fixes are type-annotation-only or minimal casts.
2. **Do NOT add `# type: ignore`** unless absolutely unavoidable (e.g., untyped third-party library with no stubs and not in overrides).
3. **Prefer `assert x is not None`** for union-attr on values that are guaranteed non-None at that point in the code.
4. **Use `from typing import Any`** - do NOT use `from __future__ import annotations` unless it's already present.
5. **Bare generics** -> always parameterize: `list[Any]`, `dict[str, Any]`, `tuple[Any, ...]`, `set[str]`.
6. **`no-any-return`** -> prefer `str(...)` for string returns, `list(...)` for list returns, or intermediate typed variables.
7. **Always verify imports** after adding type annotations - if you use `Any`, `cast`, etc., they must be imported.
8. **Run `python -m mypy src --no-incremental`** after all fixes and verify **0 errors**.

---

## Workflow

1. Start with **TIER 1** (mechanical, low risk).
2. Then **TIER 2** (type fixes, still low risk).
3. Finally **TIER 3** (structural, requires understanding code flow).
4. After each tier, run mypy to verify incremental progress.
5. If a fix introduces NEW errors, investigate immediately before proceeding.

---

## Files Already Fixed (Phase 1 - DO NOT touch)

These `src/gui` files were already fixed in Phase 1. Do not modify them:

- `src/gui/panels/base.py`
- `src/gui/panels/dashboard_panel.py`
- `src/gui/panels/notifications_panel.py`
- `src/gui/panels/contabilita_kpi/kpi_panel.py`
- `src/gui/panels/settings/tabs/telegram_tab.py`
- `src/gui/panels/settings/tabs/backup_tab.py`
- `src/gui/panels/ricerca_pdl.py`
- `src/gui/panels/prenota_bp.py`
- `src/gui/panels/dipendenti_manager_panel.py`
- `src/gui/panels/timbrature/panel.py`
- `src/gui/panels/scarico_ore_panel.py`
- `src/gui/panels/health_panel.py`
- `src/gui/controllers/search_controller.py`
- `src/gui/widgets/contabilita/year_tab.py`
- `src/gui/widgets/contabilita/attivita_tab.py`
- `src/gui/widgets/contabilita/giornaliere_tab.py`
- `src/gui/widgets/security_dashboard.py`
- `src/gui/widgets/activity_feed.py`
- `src/gui/main_window/components/menu_bar.py`
- `src/gui/formatters.py`

Also fixed outside gui scope:
- `src/bots/safework/pdl/search_bot.py` (added missing `get_columns()`)
