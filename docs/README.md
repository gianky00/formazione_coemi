# Intelleo - Predict. Validate. Automate.

**Intelleo** è una piattaforma avanzata per la gestione della sicurezza sul lavoro, progettata per automatizzare l'analisi, la validazione e il monitoraggio delle scadenze dei certificati formativi.

![Intelleo Dashboard](desktop_app/assets/logo.png)

## 🚀 Caratteristiche Principali

*   **Analisi AI Single-Pass**: Estrazione automatica di entità da PDF tramite Google Gemini 2.5 Pro.
*   **Sicurezza Zero-Trust**: Database cifrato in memoria, Node-Locking hardware, Anti-Tamper temporale.
*   **Workflow Ibrido**: Validazione manuale assistita (Human-in-the-loop) e importazione massiva CSV.
*   **Assistente Lyra**: Chatbot RAG con sintesi vocale per interrogare i dati in linguaggio naturale.
*   **Auto-Update Licenze**: Aggiornamento trasparente delle chiavi di licenza via GitHub CDN.

## 📚 Documentazione Tecnica

La documentazione è strutturata per domini di competenza. **Inizia da qui:**

### Architettura & Design
*   **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)**: Panoramica componenti, Boot sequence e Bridge React.
*   **[System Design Report](docs/SYSTEM_DESIGN_REPORT.md)**: **(Deep Dive)** Crittografia, Licenze, Update Pipeline.
*   **[Project Structure](docs/PROJECT_STRUCTURE_AND_TESTS.md)**: Mappa file e Test Coverage.

### Sviluppo & Dati
*   **[Data Models](docs/DATA_MODELS.md)**: Schema Database e Pydantic.
*   **[API Reference](docs/API_REFERENCE.md)**: Lista endpoint Backend.
*   **[Critical Flows](docs/CRITICAL_FLOWS.md)**: Logiche di business (Import, Linking, Stati).
*   **[Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)**: Dettagli React/Vite.

### Operations & Build
*   **[Build Instructions](docs/BUILD_INSTRUCTIONS.md)**: Come compilare, offuscare e creare l'installer.
*   **[Test Guide](docs/TEST_GUIDE.md)**: Strategie di test e Mocking Qt.
*   **[Dev Protocols](docs/DEV_PROTOCOLS.md)**: Standard di codice e sicurezza.

---

## 🛠️ Setup Ambiente di Sviluppo

### Prerequisiti
*   Python 3.12+
*   Node.js 18+
*   Chiavi API (Gemini, PostHog, Sentry) nel file `.env` (non committato).

### Installazione
```bash
# 1. Clone & Venv
git clone <repo>
python -m venv .venv
.\.venv\Scripts\activate

# 2. Dipendenze Python
pip install -r requirements.txt

# 3. Dipendenze Frontend
cd guide_frontend
npm install
npm run build
cd ..
```

### Avvio (Dev Mode)
```bash
# Lancia l'intera applicazione (Backend + Frontend)
python launcher.py
```

### Test
```bash
python -m pytest
```

---

## ⚖️ Licenza
Software Proprietario protetto da Copyright.
L'uso non autorizzato, la decompilazione o l'elusione dei sistemi di protezione (PyArmor) sono violazioni dei termini di servizio.
