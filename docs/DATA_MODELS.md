# Modelli Dati e Schema Database

Questo documento definisce in dettaglio lo schema del database SQLite (cifrato) e i modelli Pydantic utilizzati per la validazione API.

## 1. Schema Database (SQLAlchemy)

File sorgente: `app/db/models.py`.

### `users` (Utenti Sistema)
Gestisce l'autenticazione e i permessi.
*   **Constraints**: `username` UNIQUE.

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key (Auto-increment). |
| `username` | `String` | NO | Identificativo univoco login. |
| `hashed_password` | `String` | NO | Hash Bcrypt. |
| `account_name` | `String` | YES | Nome visualizzato (es. "Mario Rossi"). |
| `is_admin` | `Boolean` | NO | Default `False`. Flag privilegi elevati. |
| `last_login` | `DateTime` | YES | Ultimo accesso. |
| `previous_login` | `DateTime` | YES | Penultimo accesso (per UI). |
| `gender` | `String` | YES | Genere ('M', 'F') per UI customization. |
| `created_at` | `DateTime` | NO | Data creazione record. |

### `blacklisted_tokens` (Sicurezza Sessione)
Tabella per la gestione del Logout (JWT invalidation).

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key. |
| `token` | `String` | NO | Token JWT invalidato. UNIQUE. |
| `blacklisted_on` | `DateTime` | NO | Timestamp logout. |

### `audit_logs` (Audit Trail)
Registro immutabile delle azioni di sicurezza.

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key. |
| `user_id` | `Integer` | YES | FK su `users.id` (NULL se System Action). |
| `username` | `String` | NO | Snapshot username (per storicità se user eliminato). |
| `action` | `String` | NO | Enum (es. `LOGIN`, `UPDATE_CERT`). |
| `category` | `String` | NO | Categoria (es. `AUTH`, `SECURITY`). |
| `details` | `String` | YES | Descrizione human-readable. |
| `timestamp` | `DateTime` | NO | UTC Timestamp. |
| `ip_address` | `String` | YES | IP Client. |
| `severity` | `String` | NO | `LOW`, `MEDIUM`, `CRITICAL`. |
| `device_id` | `String` | YES | ID Hardware Client. |
| `changes` | `JSON` | YES | Diff modifiche (`{key: {old: v, new: v}}`). |

### `dipendenti` (Anagrafica)
Registro centrale del personale.

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key. |
| `matricola` | `String` | NO | UNIQUE. Badge ID. |
| `nome` | `String` | NO | Nome proprio. |
| `cognome` | `String` | NO | Cognome. |
| `data_nascita` | `Date` | YES | Usata per risoluzione omonimie. |
| `email` | `String` | YES | Contatto. |
| `categoria_reparto` | `String` | YES | Dipartimento. |
| `data_assunzione` | `Date` | YES | Data assunzione. |

### `corsi` (Catalogo Formativo)
Definizione dei tipi di documento.
*   **Constraints**: UNIQUE(`nome_corso`, `categoria_corso`).

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key. |
| `nome_corso` | `String` | NO | Nome specifico (es. "Antincendio Rischio Alto"). |
| `validita_mesi` | `Integer` | NO | Durata validità (0 = Custom/Estratta). |
| `categoria_corso` | `String` | NO | Macro-categoria (es. `ANTINCENDIO`, `NOMINA`). |

### `certificati` (Documenti)
Istanza di un corso completato da un dipendente.
*   **Constraints**: UNIQUE(`dipendente_id`, `corso_id`, `data_rilascio`).

| Colonna | Tipo | Nullable | Descrizione |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | NO | Primary Key. |
| `dipendente_id` | `Integer` | YES | FK `dipendenti.id`. NULL se Orfano. |
| `corso_id` | `Integer` | NO | FK `corsi.id`. |
| `data_rilascio` | `Date` | NO | Data emissione. |
| `data_scadenza_calcolata`| `Date` | YES | Data scadenza effettiva. |
| `file_path` | `String` | NO | Path relativo del PDF. |
| `stato_validazione` | `Enum` | NO | `AUTOMATIC` (AI), `MANUAL` (User). |
| `nome_dipendente_raw` | `String` | YES | Nome estratto da AI (Fallback per orfani). |
| `data_nascita_raw` | `String` | YES | Data nascita estratta da AI (Fallback). |

---

## 2. API Schemas (Pydantic)

File sorgente: `app/schemas/schemas.py`.

### `CertificatoSchema` (Response Model)
Utilizzato per visualizzare i dati in tabella.
```python
class CertificatoSchema(BaseModel):
    id: int
    nome: str               # Computed: Dipendente.nome + cognome OR nome_dipendente_raw
    matricola: str | None   # Computed
    data_nascita: str | None # DD/MM/YYYY
    corso: str              # Corso.nome_corso
    categoria: str          # Corso.categoria_corso
    data_rilascio: str      # DD/MM/YYYY
    data_scadenza: str | None
    stato_certificato: str  # "attivo" | "in_scadenza" | "scaduto" | "rinnovato"
    assegnazione_fallita_ragione: str | None # Error msg se orfano
```

### `AuditLogSchema` (Response Model)
```python
class AuditLogSchema(BaseModel):
    timestamp: datetime
    username: str
    action: str
    category: str
    details: str
    severity: str
    changes: str | None     # JSON String
```

## 🤖 AI Metadata (RAG Context)
```json
{
  "type": "data_schema",
  "domain": "database",
  "tables": [
    "User",
    "AuditLog",
    "Dipendente",
    "Corso",
    "Certificato"
  ],
  "relationships": [
    "Dipendente -> Certificato (One-to-Many)",
    "Corso -> Certificato (One-to-Many)",
    "User -> AuditLog (One-to-Many)"
  ],
  "validation_rules": [
    "Unique(Corso.nome + Categoria)",
    "Unique(Certificato.dipendente + corso + data)"
  ]
}
```
