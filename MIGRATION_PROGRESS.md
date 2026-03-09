# 🚀 Piano di Migrazione: da Tkinter a PySide6

Stato attuale: **RE-PIANIFICAZIONE (Tkinter rilevato)**
Data inizio: 2026-03-09

## 📊 Avanzamento Lavori
- [ ] **Fase 1: Preparazione Environment** [20%]
  - [x] Creazione Branch `feature/migrate-to-pyside6`
  - [ ] Aggiunta `PySide6` a `requirements.txt`
  - [ ] Rimozione dipendenze Tkinter (dove possibile)
- [x] **Fase 2: Refactoring Core (Main Entry Point)** [100%]
  - [x] Trasformazione `ApplicationController` in `QApplication` / `QMainWindow`
  - [x] Sostituzione `mainloop()` di Tkinter con `exec()` di Qt
  - [x] Migrazione gestione eventi e timer inattività
- [x] **Fase 3: Migrazione View (Riscrittura UI)** [100%]
  - [x] `LoginView`: completato
  - [x] `DashboardView`: completato
  - [x] `ImportView`: completato
  - [x] `ValidationView`: completato
  - [x] `DatabaseView`: completato
  - [x] `ScadenzarioView`: completato
  - [x] `DipendentiView`: completato
  - [x] `LyraView`: completato
  - [x] `ConfigView`: completato
  - [x] `AuditView`: completato
  - [x] `EditCertificatoDialog`: completato
- [ ] **Fase 4: Integrazione e Styling** [50%]
  - [x] Implementazione stile moderno (Fusion + CSS personalizzati)
  - [ ] Verifica componenti custom (Notification Center)
  - [ ] Test di regressione finale
- [ ] **Fase 4: Integrazione e Styling** [0%]
  - [ ] Implementazione stile moderno (Dark/Light Mode o Fusion)
  - [ ] Migrazione `ToastManager` a sistema di notifiche Qt
  - [ ] Test di regressione completo (Nessuna perdita di funzionalità)

## 📝 Note Tecniche
- **SCOPERTA:** L'app originale usa `tkinter`. La migrazione è una riscrittura della UI.
- La logica di business (`app/`) rimane invariata.
- Utilizzare `Signal` e `Slot` per la comunicazione tra componenti.
- Sostituire `root.after` con `QTimer`.

---
*Aggiornato da Gemini CLI*
