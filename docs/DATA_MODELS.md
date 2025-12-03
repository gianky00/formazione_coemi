# Data Models & Schema Definitions

## Database Schema (SQLAlchemy)

Defined in `app/db/models.py`. The database is stored in `database_documenti.db` (SQLite), which is encrypted at rest and loaded into memory at runtime.

### `User` (Table: `users`)
Represents an authorized user of the application.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Index | Internal ID |
| `username` | String | Unique, Index | Login Username |
| `hashed_password` | String | | Bcrypt hash |
| `account_name` | String | | Display Name (e.g., "Mario Rossi") |
| `is_admin` | Boolean | | Admin privileges |
| `last_login` | DateTime | | Timestamp of current/last login |
| `previous_login` | DateTime | | Timestamp of the login before the current one |
| `created_at` | DateTime | | Creation timestamp |

### `AuditLog` (Table: `audit_logs`)
Records security-critical actions for compliance and auditing.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Index | Internal ID |
| `user_id` | Integer | FK(`users.id`) | Actor ID (Nullable for System events) |
| `username` | String | Index | Snapshot of username |
| `action` | String | Index | Event Type (e.g., "LOGIN_FAILED") |
| `category` | String | Index | Scope (e.g., "AUTH", "CERTIFICATE") |
| `details` | String | | Human-readable description |
| `timestamp` | DateTime | Index | Event time (UTC) |
| `ip_address` | String | Index | Client IP |
| `severity` | String | | "LOW", "MEDIUM", "CRITICAL" |
| `device_id` | String | | Client Hardware ID / Fingerprint |
| `changes` | String | | JSON diff of modified data |

### `Dipendente` (Table: `dipendenti`)
Represents an employee in the organization.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Index | Internal ID |
| `matricola` | String | Unique, Index | Employee Badge/ID |
| `nome` | String | Index | First Name |
| `cognome` | String | Index | Last Name |
| `data_nascita` | Date | | Date of Birth |
| `email` | String | Unique, Index | Optional contact email |
| `categoria_reparto` | String | | Optional department |

### `Corso` (Table: `corsi`)
Represents a master course definition.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Index | Internal ID |
| `nome_corso` | String | Index | Specific course name |
| `validita_mesi` | Integer | | Validity period in months (0 = custom) |
| `categoria_corso` | String | Index | Broad category (e.g., "ANTINCENDIO") |

**Constraint**: Unique (`nome_corso`, `categoria_corso`).

#### Reference Data: Course Validity Defaults
Defined in `app/db/seeding.py` and enforced by AI Logic.

| Category | Validity (Months) | Behavior |
| :--- | :--- | :--- |
| **ANTINCENDIO** | 60 | Fixed 5 years |
| **PRIMO SOCCORSO** | 36 | Fixed 3 years |
| **PREPOSTO** | 24 | Fixed 2 years |
| **BLSD** | 12 | Fixed 1 year |
| **ATEX** | 60 | Default 5 years |
| **VISITA MEDICA** | 0 | Extracts "Da rivedere entro..." |
| **UNILAV** | 0 | Extracts "Data Fine" |
| **PATENTE** | 0 | Extracts "4b" |
| **CARTA DI IDENTITA** | 0 | Extracts "Scadenza" |
| **NOMINA** | 0 | No expiration (Active) |
| **MODULO RECESSO...** | 0 | No expiration |
| **HLO** | 0 | No expiration |
| **TESSERA HLO** | 0 | Scadenza extracted |
| **(Others)** | 60 | Default 5 years |

### `Certificato` (Table: `certificati`)
Represents an issued certificate instance.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Index | Internal ID |
| `dipendente_id` | Integer | FK(`dipendenti.id`), Nullable | Linked Employee (Null if orphan) |
| `corso_id` | Integer | FK(`corsi.id`) | Linked Course |
| `data_rilascio` | Date | | Issue Date |
| `data_scadenza_calcolata` | Date | Nullable | Calculated Expiration Date |
| `file_path` | String | | Path to stored PDF |
| `stato_validazione` | Enum | `AUTOMATIC` or `MANUAL` | Workflow status |
| `nome_dipendente_raw` | String | Nullable | Raw extracted name (for orphans) |
| `data_nascita_raw` | String | Nullable | Raw extracted DOB (for orphans) |

## Pydantic Schemas (DTOs)

Defined in `app/schemas/schemas.py`. Used for API validation.

### `CertificatoSchema` (Response)
```python
{
    "id": int,
    "nome": str,               # Full name (computed)
    "data_nascita": str,       # DD/MM/YYYY or null
    "matricola": str,          # Null if orphan
    "corso": str,
    "categoria": str,
    "data_rilascio": str,      # DD/MM/YYYY
    "data_scadenza": str,      # DD/MM/YYYY or null
    "stato_certificato": str,  # "attivo", "in_scadenza", "scaduto", "rinnovato"
    "assegnazione_fallita_ragione": str # Optional error message
}
```

### `CertificatoCreazioneSchema` (Request)
```python
{
    "nome": str,               # Required, min_length=1
    "data_nascita": str,       # Optional
    "corso": str,              # Required
    "categoria": str,          # Required
    "data_rilascio": str,      # Required (DD/MM/YYYY)
    "data_scadenza": str       # Optional (DD/MM/YYYY)
}
```

### `CertificatoAggiornamentoSchema` (Request)
Used for `PUT` operations. All fields are optional.
```python
{
    "nome": str,
    "corso": str,
    "categoria": str,
    "data_rilascio": str,
    "data_scadenza": str
}
```

## JSON Interfaces (AI Response)
The AI Service (`extract_entities_with_ai`) returns:

```json
{
    "nome": "Mario Rossi",
    "data_nascita": "01-01-1980",
    "corso": "Corso Antincendio",
    "categoria": "ANTINCENDIO",
    "data_rilascio": "10-01-2023",
    "data_scadenza": "10-01-2028"  // Or null
}
```
*Note: Dates in AI response are normalized to `DD/MM/YYYY` by the Frontend/API before persistence.*

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
