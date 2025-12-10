# Architettura Frontend Guida (React + QWebChannel)

Questo documento descrive l'architettura tecnica del modulo `guide_frontend`, una Single Page Application (SPA) React incorporata nell'applicazione desktop PyQt6 per fornire un manuale utente interattivo e moderno.

## 1. Overview Tecnologica

Il modulo è progettato per essere **Mobile-Responsive** (per future estensioni web) e **Desktop-Embedded**.

*   **Core**: React 18.
*   **Build Tool**: Vite (per compilazione rapida e HMR).
*   **Styling**: Tailwind CSS v3 (Utility-first).
*   **Routing**: React Router (virtuale, gestito internamente).
*   **Integrazione**: `QWebEngineView` (Chromium) + `QWebChannel` (IPC).

## 2. Struttura del Progetto (`guide_frontend/`)

```text
guide_frontend/
├── src/
│   ├── components/         # Componenti UI (Header, Sidebar, Layout)
│   ├── pages/              # Pagine di contenuto (Home, ImportGuide, ecc.)
│   ├── hooks/              # Custom Hooks (useSearch)
│   ├── assets/             # Immagini e Icone statiche
│   ├── App.jsx             # Entry point e Routing
│   └── main.jsx            # Mounting React DOM
├── public/                 # Assets pubblici (favicon, qwebchannel.js)
├── index.html              # Template HTML principale
├── vite.config.js          # Configurazione Build (Base URL relativo)
└── package.json            # Dipendenze Node.js
```

## 3. Il Ponte di Comunicazione (The Bridge)

La comunicazione tra Python (PyQt6) e JavaScript (React) avviene tramite **Qt WebChannel**.

### Lato Backend (Python)
Nel file `desktop_app/views/modern_guide_view.py`:
1.  Viene creato un oggetto `GuideBridge(QObject)`.
2.  Viene esposto uno Slot `close_guide()` (o altri metodi).
3.  Il canale viene registrato sulla pagina WebEngine: `channel.registerObject('bridge', self.bridge)`.

### Lato Frontend (JavaScript/React)
Nel file `index.html` viene caricato `qwebchannel.js` (protocollo `qrc://`).
Nel componente React (`App.jsx` o `Layout.jsx`):

```javascript
// Inizializzazione Bridge
useEffect(() => {
  if (window.qt && window.qt.webChannelTransport) {
    new QWebChannel(window.qt.webChannelTransport, (channel) => {
      // Accesso all'oggetto Python esposto
      const bridge = channel.objects.bridge;
      window.bridge = bridge; // Rendilo globale o usa Context
    });
  }
}, []);

// Chiamata a funzione Python
const handleClose = () => {
  if (window.bridge) {
    window.bridge.close_guide(); // Chiama lo slot Python
  }
};
```

## 4. Build & Deployment

Poiché l'app desktop non include un server Node.js, la guida deve essere compilata in file statici HTML/CSS/JS.

### Processo di Build
1.  Comando: `npm run build` (esegue `vite build`).
2.  Output: Cartella `guide_frontend/dist/`.
    *   `index.html`
    *   `assets/index-HASH.js`
    *   `assets/index-HASH.css`

### Configurazione Vite (`vite.config.js`)
È cruciale impostare `base: './'` affinché i percorsi degli asset siano relativi. Questo permette il caricamento via protocollo `file://` all'interno di `QWebEngineView`.

```javascript
export default defineConfig({
  base: './', // Cruciale per file:// protocol
  // ...
})
```

## 5. Verifica e Testing
Per verificare le modifiche frontend senza lanciare l'intera app desktop:
1.  `npm run dev`: Avvia server di sviluppo locale (browser standard).
2.  **Limitazione**: Le funzionalità legate al Bridge (`window.qt`) non funzioneranno nel browser standard. È necessario mockare il bridge o testare nell'app desktop reale.
