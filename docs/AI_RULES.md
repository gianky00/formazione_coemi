Ecco il file **AI_RULES.md** generato basandosi sull'analisi approfondita del codice sorgente fornito. Questo documento è progettato per essere la "verità assoluta" per qualsiasi Agente AI che operi su questo progetto.

```markdown
# AI_RULES.md - Regole di Sviluppo e Architettura (Progetto Intelleo)

> **AVVISO PER AGENTI AI:** Questo documento definisce gli standard, i pattern e le regole inviolabili per il progetto Intelleo. Ignorare queste regole porterà a codice non funzionante, violazioni di sicurezza o fallimenti nella build Nuitka. Leggere attentamente prima di generare codice.

---

## 1. Filosofia del Codice e Architettura

Il progetto **Intelleo** è un'applicazione desktop ibrida per la gestione della sicurezza sul lavoro.

### Principi Guida
1.  **Sicurezza Paranoica:** Il database è crittografato su disco e decifrato *solo* in memoria (RAM). Le stringhe sensibili (chiavi API, token) non devono MAI apparire in chiaro nel codice sorgente.
2.  **Architettura Ibrida:**
    *   **Backend:** FastAPI (`app/`) in esecuzione locale su porta dinamica. Gestisce logica, DB e AI.
    *   **Frontend Desktop:** Tkinter (`desktop_app/`) funge da client per le API locali.
    *   **Frontend Guida:** React (`guide_frontend/`) integrato come asset statico.
3.  **Portabilità Assoluta:** Il codice deve girare sia come script Python (`dev mode`) sia come eseguibile compilato con Nuitka (`frozen mode`). I percorsi dei file non devono mai essere hardcoded.
4.  **Resilienza:** L'applicazione deve gestire crash, file di lock orfani e assenza di rete senza bloccare l'utente in loop infiniti.

### Diagramma Architetturale
```mermaid
graph TD
    User[Utente] -->|Interagisce| GUI[Tkinter Desktop App]
    GUI -->|HTTP Req| API[FastAPI Backend (Localhost)]
    API -->|CRUD| DB_Mgr[DBSecurityManager]
    DB_Mgr -->|Decrypt/Load| RAM_DB[(In-Memory SQLite)]
    DB_Mgr -->|Encrypt/Save| File_DB[(Encrypted .db File)]
    API -->|Call| AI[Google Gemini AI]
    GUI -->|Visualizza| Guide[React SPA (Static)]
```

---

## 2. Convenzioni Naming COMPLETE

| Entità | Convenzione | Esempio | Note |
| :--- | :--- | :--- | :--- |
| **File Python** | `snake_case` | `license_manager.py` | Nomi descrittivi, minuscoli. |
| **Classi** | `PascalCase` | `LicenseUpdaterService` | Sostantivi che descrivono l'oggetto. |
| **Funzioni/Metodi** | `snake_case` | `get_license_data()` | Verbo + Sostantivo. |
| **Variabili** | `snake_case` | `user_info` | Esplicite, no abbreviazioni criptiche. |
| **Costanti** | `UPPER_SNAKE_CASE` | `MAX_UPLOAD_SIZE` | Definite in `config.py` o `constants.py`. |
| **Variabili Private** | `_snake_case` | `_cached_machine_id` | Uso interno al modulo/classe. |
| **Segreti Offuscati** | `_NAME_OBFUSCATED` | `_FERNET_KEY_OBFUSCATED` | **OBBLIGATORIO** per stringhe sensibili. |
| **Cartelle** | `snake_case` | `desktop_app`, `crea_licenze` | |

---

## 3. Struttura File Standard (Template)

Ogni nuovo file Python deve seguire rigorosamente questa struttura per garantire compatibilità con il logging e la gestione degli errori.

```python
"""
Nome Modulo: [Descrizione breve]
Responsabilità: [Cosa fa questo modulo]
Autore: [AI Agent / Team]
"""
import os
import logging
from typing import Optional, List

# Import interni (usare percorsi assoluti da root quando possibile)
from app.core.config import settings
from app.utils.audit import log_security_action

# Configurazione Logger (usare sempre __name__)
logger = logging.getLogger(__name__)

# Costanti del modulo
MODULE_TIMEOUT = 30

class NomeClasse:
    """
    Docstring della classe che spiega lo scopo.
    """

    def __init__(self, param: str):
        self.param = param

    def metodo_pubblico(self) -> bool:
        """
        Docstring del metodo.
        Returns: True se successo, False altrimenti.
        """
        try:
            logger.debug(f"Esecuzione metodo con param: {self.param}")
            # Logica qui
            return True
        except Exception as e:
            logger.error(f"Errore in metodo_pubblico: {e}", exc_info=True)
            return False

# Funzioni di utilità private alla fine
def _helper_function():
    pass
```

---

## 4. Pattern Obbligatori

### A. Gestione Percorsi (Path Resolution)
**MAI** usare `os.path.abspath(__file__)` o percorsi relativi manuali per accedere a risorse (immagini, DB, licenze). Usare **SEMPRE** `app.core.path_resolver`.

| Risorsa | Funzione da usare |
| :--- | :--- |
| Root App | `get_base_path()` |
| Asset (img, html) | `get_asset_path("rel/path")` |
| Dati Utente (DB, Log) | `get_user_data_path()` |
| Licenza | `get_license_path()` |

**Esempio:**
```python
from app.core.path_resolver import get_asset_path
icon_path = get_asset_path("desktop_app/icons/icon.ico")
```

### B. Gestione Segreti (Obfuscation)
**MAI** inserire chiavi API o password in chiaro. Usare `app.core.string_obfuscation`.

**Workflow:**
1. Generare stringa offuscata offline (`admin/tools/generate_obfuscated_keys.py`).
2. Inserire nel codice la stringa offuscata.
3. De-offuscare a runtime.

**Esempio:**
```python
from app.core.string_obfuscation import deobfuscate_string
# Valore generato offline
_API_KEY_OBFUSCATED = "obf:Tm90QVJlYWxLZXk="

def get_api_key():
    return deobfuscate_string(_API_KEY_OBFUSCATED)
```

### C. Accesso al Database (Backend)
Il DB è **SQLite In-Memory Encrypted**. Non usare `sqlite3.connect()` direttamente.
Usare sempre la sessione SQLAlchemy fornita da `app.db.session.get_db` o gestire `DBSecurityManager` se necessario operazioni basso livello.

**Esempio (FastAPI Route):**
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

@router.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### D. Task Asincroni (Frontend Tkinter)
Tkinter non è thread-safe. Le operazioni lunghe (chiamate API, I/O) devono usare `desktop_app.utils.TaskRunner` o thread separati che non bloccano la UI.

**Esempio:**
```python
from desktop_app.utils import TaskRunner

def on_button_click(self):
    runner = TaskRunner(self, "Titolo", "Messaggio attendere...")
    try:
        # Esegue self.long_operation in un thread e mostra una progress bar modale
        result = runner.run(self.long_operation, arg1, arg2)
        self.update_ui(result)
    except Exception as e:
        messagebox.showerror("Errore", str(e))
```

---

## 5. DO - Pratiche CORRETTE

| Pratica | Esempio / Dettaglio | Motivazione |
| :--- | :--- | :--- |
| **Type Hinting** | `def func(a: int) -> str:` | Facilita la comprensione e riduce errori di tipo runtime. |
| **Logging** | `logger.info("Utente creato")` | `print()` non è visibile in produzione (no console). |
| **Gestione Errori UI** | `try...except` con `messagebox` | Evita che l'app desktop si chiuda improvvisamente. |
| **Audit Log** | `log_security_action(...)` | Ogni azione critica (login, delete, update) DEVE essere tracciata. |
| **Import Assoluti** | `from app.db.models import User` | Evita confusione tra moduli e problemi con Nuitka. |
| **Patching Test** | Usare `sys.modules` mock in `conftest.py` | I test non devono chiamare servizi esterni (Sentry, WMI). |

---

## 6. DON'T - Pratiche da EVITARE

| Anti-Pattern | Alternativa Corretta | Motivazione |
| :--- | :--- | :--- |
| ❌ `open("file.txt")` | ✅ `open(get_user_data_path() / "file.txt")` | Scrivere nella cartella di installazione è vietato (permessi). |
| ❌ `print("Error")` | ✅ `logger.error("Error")` | I log su file sono essenziali per il debug remoto. |
| ❌ Hardcoding `C:\...` | ✅ `path_resolver` | L'app deve girare su qualsiasi PC e OS. |
| ❌ API Key in chiaro | ✅ `obfuscate_string` | `strings.exe` può estrarre chiavi in chiaro dall'eseguibile. |
| ❌ SQL Raw | ✅ SQLAlchemy ORM | Previene SQL Injection e gestisce la connessione in-memory. |
| ❌ `time.sleep()` in UI | ✅ `root.after()` o `TaskRunner` | `sleep` congela l'interfaccia grafica. |
| ❌ Modificare `settings.json` a mano | ✅ `settings.save_mutable_settings()` | Garantisce la coerenza e triggera eventuali reload. |

---

## 7. Checklist Pre-Commit

Prima di considerare il codice "finito", verificare:

1.  [ ] **Nessun segreto in chiaro?** (Cerca regex `AIza`, `ghp_`, `sk-`).
2.  [ ] **Path Resolution:** Ho usato `path_resolver` per ogni file?
3.  [ ] **Import:** Sono tutti assoluti (`from app...`)? Niente `from ..utils`.
4.  [ ] **Tkinter:** Ho separato la logica pesante dalla UI thread?
5.  [ ] **Logging:** Ho aggiunto log per il successo e il fallimento dell'operazione?
6.  [ ] **Test:** Ho eseguito `pytest`? (In particolare `tests/app/core/test_db_security.py` se tocco il DB).

---

## 8. Code Review Checklist (Specifica per Agenti)

Quando analizzi o generi codice per Intelleo, chiediti:

*   **Sicurezza:** Questo codice tocca il database? Se sì, rispetta il `DBSecurityManager`? Verifica se l'utente ha i permessi (`deps.check_write_permission`).
*   **Compatibilità Nuitka:** Ci sono import dinamici o `eval()`? (Da evitare, rompono la compilazione).
*   **Gestione Errori:** Se l'API backend è giù, il client desktop crasha o mostra un errore gentile?
*   **Privacy:** I log contengono dati sensibili (password, contenuti file)? (Non dovrebbero).

---

## 9. Riferimenti Rapidi

*   **Entry Point API:** `app/main.py`
*   **Entry Point Desktop:** `launcher.py` (che chiama `desktop_app/main.py`)
*   **Build Script:** `admin/offusca/build_nuitka.py`
*   **Configurazione:** `app/core/config.py`
*   **Sicurezza DB:** `app/core/db_security.py`
```
