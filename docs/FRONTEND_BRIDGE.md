# Frontend Bridge (React Integration)

Questo documento descrive come l'applicazione desktop (PyQt6) integra componenti web moderni sviluppati in React (Vite).

## 1. Architettura Ibrida

Alcune parti dell'interfaccia (specificamente il **Manuale Utente** e moduli interattivi complessi) sono realizzate come Single Page Application (SPA) web.

*   **Host**: `QWebEngineView` (Chromium embedded).
*   **Source**: File statici (`index.html`, JS, CSS) serviti dalla cartella `dist/nuitka/Intelleo.dist/guide/` (in produzione) o `guide_frontend/dist/` (in sviluppo).
*   **Protocollo**: `file://` (o server locale in debug).

---

## 2. Il Bridge (QWebChannel)

La comunicazione tra Python (Backend UI) e JavaScript (Frontend React) avviene tramite `QWebChannel`.

### Lato Python (`GuideBridge`)
Classe `QObject` esposta al contesto JavaScript.

```python
class GuideBridge(QObject):
    # Segnali (Python -> JS)
    themeChanged = pyqtSignal(str)

    # Slot (JS -> Python)
    @pyqtSlot()
    def close_guide(self):
        self.parent.close()
```

### Lato React (JavaScript)
Il frontend deve inizializzare il canale al caricamento.

```javascript
// useEffect hook
import { QWebChannel } from './qwebchannel.js';

new QWebChannel(qt.webChannelTransport, (channel) => {
    window.pyBridge = channel.objects.bridge;

    // Chiamata a Python
    window.pyBridge.close_guide();
});
```

---

## 3. Workflow di Sviluppo

### `guide_frontend/`
Progetto standard Node.js/Vite.
1.  **Dev**: `npm run dev` (Server locale).
2.  **Build**: `npm run build`.
    *   Output: `guide_frontend/dist/`.
    *   Configurazione Vite: `base: './'` (per supportare caricamento via `file://`).

### Integrazione in Build
Durante il processo di build Nuitka (`build_nuitka.py`):
1.  Viene eseguito `npm install && npm run build`.
2.  La cartella `dist` viene copiata dentro l'eseguibile distribuito.
