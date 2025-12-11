# Architettura Client Desktop (PyQt6)

Questo documento descrive l'architettura dell'applicazione desktop, sviluppata con **PyQt6**, che funge da interfaccia utente principale.

## 1. Struttura Generale

L'applicazione segue un pattern architetturale ibrido **Controller-View-ViewModel (CVVM)** per separare la logica di presentazione dalla logica di business e di rete.

*   **Entry Point**: `launcher.py` (vedi `SYSTEM_ARCHITECTURE.md`).
*   **Controller Principale**: `desktop_app.main.ApplicationController`.
*   **Finestra Master**: `desktop_app.main_window_ui.MasterWindow`.

---

## 2. Componenti Core

### 2.1 Application Controller
Il `ApplicationController` è il "cervello" dell'interfaccia.
*   **Gestione Stato**: Mantiene lo stato dell'autenticazione (`is_logged_in`, `token`).
*   **Navigazione**: Gestisce lo stack delle viste (`QStackedWidget`) e le transizioni (es. Login -> Dashboard).
*   **API Client**: Inizializza e condivide l'istanza di `APIClient`.
*   **Segnali Globali**: Ascolta segnali critici (es. `logout_requested`, `import_completed`) per aggiornare le viste.

### 2.2 Master Window
La finestra principale (`MasterWindow`) è un container shell che ospita:
*   **Sidebar**: Menu di navigazione laterale (collassabile).
*   **Header**: Barra superiore con info utente e controlli finestra.
*   **Content Area**: Area dinamica dove vengono caricate le Viste.
*   **System Tray**: Icona nella barra delle applicazioni per background running.

---

## 3. Viste e ViewModels

Per le viste complesse, utilizziamo un ViewModel dedicato per gestire i dati.

### 3.1 Dashboard (Database Certificati)
*   **View**: `desktop_app.views.dashboard_view.DashboardView`.
    *   Tabella `QTableView` con `QAbstractTableModel` custom.
    *   Filtri (Combo Box) e Ricerca.
*   **ViewModel**: `desktop_app.view_models.dashboard_view_model.DashboardViewModel`.
    *   **Responsabilità**: Fetch dati via API (`GET /certificati`), applicazione filtri in memoria (Pandas/List), paginazione.
    *   **Threading**: Esegue le chiamate API su thread separati per non bloccare la UI.

### 3.2 Scadenzario (Gantt Chart)
*   **View**: `desktop_app.views.scadenzario_view.ScadenzarioView`.
*   **Tecnologia**: `QGraphicsScene` / `QGraphicsView`.
*   **Rendering**: Disegna barre temporali (`GanttBarItem`) su una timeline orizzontale.
*   **Performance**: Utilizza il Culling (disegna solo gli elementi visibili) per gestire migliaia di certificati.

### 3.3 Import & AI
*   **View**: `desktop_app.views.import_view.ImportView`.
*   **Logica**: Drag & Drop area.
*   **Worker**: `ImportWorker` (`QThread`) invia il file al backend e attende la risposta AI asincrona.

---

## 4. Gestione Threading e Asincronicità

Per mantenere l'interfaccia reattiva (60 FPS), nessuna operazione bloccante (IO, Rete) viene eseguita nel Main Thread (UI Thread).

### Pattern `Worker`
Tutte le operazioni lunghe sono incapsulate in classi `QThread` o `QRunnable`.
1.  **UI**: Lancia il worker e connette i segnali (`finished`, `error`).
2.  **Worker**: Esegue il task (es. `requests.get`).
3.  **Signal**: Emette i dati risultanti.
4.  **UI Slot**: Riceve i dati e aggiorna i widget.

*Nota*: I dati complessi (es. Dict/List) passati via segnale vengono spesso serializzati in JSON string o passati come oggetti Python puri (se thread-safe).

---

## 5. Styling (QSS)

L'interfaccia non usa lo stile nativo di Windows ma un tema custom "SaaS-like" definito in `desktop_app/styles.qss` (o inline in `setup_styles`).

*   **Design System**:
    *   Font: Inter (o Segoe UI fallback).
    *   Colori: Palette Tailwind (Slate 900, Blue 600, White).
    *   Border Radius: 8px/12px.
*   **Tecnica**: Fogli di stile Qt (simile a CSS) applicati globalmente a `QApplication`.
