# AI Extraction Engine

Questo documento descrive il funzionamento del motore di estrazione dati basato sull'Intelligenza Artificiale (Google Gemini 2.5 Pro), responsabile dell'analisi dei certificati PDF.

## 1. Panoramica del Servizio

Il modulo `app.services.ai_extraction.py` implementa un'architettura **Single-Pass Extraction** che converte i PDF non strutturati in dati JSON strutturati in un'unica chiamata API.

### Componenti Chiave
*   **Modello**: `gemini-2.5-pro` (Hardcoded per performance/costi ottimali).
*   **Client**: Pattern Singleton (`GeminiClient`) con Double-Checked Locking.
*   **Resilienza**: Libreria `tenacity` per retry esponenziali su errori 429/500.

---

## 2. Flusso di Esecuzione

1.  **Ricezione PDF**: Il backend riceve il file (bytes) via API `POST /certificati/upload-pdf/`.
2.  **Costruzione Prompt**:
    *   Genera dinamicamente la lista delle categorie (inclusa "ATEX" se mancante).
    *   Injecta regole di business gerarchiche (es. "NOMINA" vs "PREPOSTO").
3.  **Chiamata AI**:
    *   Invia prompt + PDF (MIME `application/pdf`) a Gemini.
    *   Gestisce il lock globale `ai_global_lock` per evitare race condition con il modulo Chat.
4.  **Parsing & Validazione**:
    *   Estrae il JSON dalla risposta markdown (` ```json ... ``` `).
    *   Gestisce risposte che tornano liste invece di oggetti singoli.
    *   Verifica lo stato `REJECT` (es. Syllabus, Programmi generici).

---

## 3. Logica del Prompt (Business Rules)

Il prompt è ingegnerizzato per risolvere ambiguità specifiche del dominio sicurezza sul lavoro.

### Gerarchia delle Regole
L'AI deve seguire un ordine di priorità rigoroso:

1.  **Filtro Binario**: Se il documento non ha un nome partecipante -> `REJECT`.
2.  **Mapping Categorie Forzato**:
    *   "DIRETTIVA SEVESO" vince su tutto se presente la dicitura.
    *   "NOMINA" (lettere di incarico) vince su "ANTINCENDIO/PREPOSTO".
    *   "PREPOSTO" è riservato agli attestati di formazione.
    *   "TESSERA HLO" (Badge) vs "HLO" (Attestato).

### Formato Dati Richiesto
L'AI normalizza i dati in uscita:
*   `nome`: Sempre UPPERCASE ("ROSSI MARIO").
*   `data_nascita`: Formato DD-MM-YYYY.
*   `categoria`: Una delle categorie statiche (es. "ANTINCENDIO").

---

## 4. Gestione Errori e Retry

Il sistema utilizza `tenacity` per garantire robustezza:

```python
@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    retry=retry_if_exception_type((
        exceptions.ResourceExhausted,  # 429
        exceptions.ServiceUnavailable, # 503
        exceptions.InternalServerError # 500
    ))
)
```

### Gestione Risposte Atipiche
*   **Lista invece di Oggetto**: Se l'AI restituisce `[{...}]`, il parser estrae il primo elemento e logga un warning.
*   **JSON Rotto**: Utilizza un estrattore stack-based (`_extract_json_block`) per isolare il JSON valido dal testo discorsivo.
