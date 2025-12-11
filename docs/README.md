# Intelleo Documentation

Benvenuto nella documentazione tecnica di **Intelleo**, il sistema avanzato per la gestione della sicurezza sul lavoro e la conformità documentale.

Questa cartella contiene la documentazione ufficiale per sviluppatori, sistemisti e agenti AI.

## 📚 Indice della Documentazione

### 1. Architettura e Design
*   **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)**: Panoramica del sistema, sequenza di avvio, gestione processi.
*   **[SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)**: Sicurezza "Zero-Trust Local", Crittografia DB, Licensing e Audit.
*   **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: Mappa completa del codice sorgente (Backend/Frontend).

### 2. Backend Services
*   **[AI_ENGINE.md](AI_ENGINE.md)**: Funzionamento del motore di estrazione Gemini (Prompt, Retry, Parsing).
*   **[CERTIFICATE_LOGIC.md](CERTIFICATE_LOGIC.md)**: Regole di business per validità, scadenze e stati.
*   **[NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md)**: Generazione report PDF e invio email.
*   **[DATA_MODELS.md](DATA_MODELS.md)**: Schema Database e API Objects.
*   **[API_REFERENCE.md](API_REFERENCE.md)**: Endpoint REST API.

### 3. Frontend & Desktop
*   **[DESKTOP_CLIENT.md](DESKTOP_CLIENT.md)**: Architettura PyQt6, ViewModels, Worker.
*   **[FRONTEND_BRIDGE.md](FRONTEND_BRIDGE.md)**: Integrazione React e QWebChannel.

### 4. Guide Operative
*   **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)**: Come compilare il progetto con Nuitka e creare l'installer.
*   **[OPERATIONAL_GUIDE.md](OPERATIONAL_GUIDE.md)**: Manuale per il rilascio, generazione licenze e gestione clienti.
*   **[TEST_GUIDE.md](TEST_GUIDE.md)**: Strategie di testing e QA ("Green Suite").
*   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Standard di codice, Git workflow e policy.

### 5. Meta & AI
*   **[AGENTS.md](AGENTS.md)**: Istruzioni per AI Agents (Persona "Jules").
*   **[LYRA_PROFILE.md](LYRA_PROFILE.md)**: Profilo dell'assistente virtuale Lyra.

---

## 📂 Archivio Storico
La cartella `MIGRAZIONE FINALIZZATA CON NIUTKA/` contiene i report storici delle fasi di sviluppo e note di migrazione. Consultare solo per archeologia del software.
