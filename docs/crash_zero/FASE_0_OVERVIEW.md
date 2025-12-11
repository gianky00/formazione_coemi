# 🎯 FASE 0: Overview & Diagnosi - Progetto "Crash Zero"

## 📋 Contesto del Progetto

### Obiettivo Primario
**Eliminare completamente ogni possibilità di crash** nell'applicazione Intelleo, trasformandola in un software di livello enterprise con robustezza assoluta.

### Priorità di Qualità (in ordine)
1. **Robustezza** - Zero crash, self-healing, resilienza totale
2. **Performance** - Avvio <2s, UI fluida 60fps, RAM <300MB
3. **UX/UI** - Moderna, intuitiva, accessibile
4. **Maintainability** - Codice pulito, test coverage >80%, docs aggiornate
5. **Scalability** - Gestisce 10,000+ certificati, 100+ dipendenti
6. **Observability** - Monitoring, alerting, troubleshooting rapido
7. **Security** - Audit trail completo, encryption everywhere

---

## 🔴 Crash Osservati - Analisi Root Cause

### Crash #1: Login Success Animation (CRITICO)
```
RuntimeError: wrapped C/C++ object of type QFrame has been deleted
File "login_view.py", line 870, in _animate_success_exit
    self.opacity_effect = QGraphicsOpacityEffect(self.container)
```

**Root Cause**: 
- La view di login viene distrutta durante la transizione verso la dashboard
- Le animazioni tentano di accedere a widget C++ già deallocati
- Il recovery (`_on_login_error`) fallisce perché anche `AnimatedButton` è distrutto

**Pattern Problematico**:
```
Login Success 
    → ApplicationController.switch_view() 
    → Old view scheduled for deletion
    → _animate_success_exit() chiamato
    → Widget C++ già distrutto
    → CRASH
```

### Crash Pattern Generico: Widget Lifecycle Violation
Questo pattern si ripete potenzialmente in:
- `splash_screen.py` → transizione a login
- `login_view.py` → transizione a dashboard ✅ CONFERMATO
- `import_view.py` → animazioni di feedback
- `validation_view.py` → transizioni tra stati
- Qualsiasi view con animazioni durante cambio schermata

---

## 🏗️ Architettura Attuale (Problemi Identificati)

### Threading Model
```
┌─────────────────────────────────────────────────────────┐
│                    MAIN THREAD (UI)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ QApplication│  │   Views     │  │   Animations    │ │
│  │             │  │ (QWidget)   │  │ (QPropertyAnim) │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│         │                │                  │          │
│         └────────────────┼──────────────────┘          │
│                          │                              │
│                   ┌──────▼──────┐                       │
│                   │ Event Loop  │                       │
│                   └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Backend Thread│ │ Worker Thread │ │ Worker Thread │
│   (Uvicorn)   │ │  (QThread)    │ │  (QRunnable)  │
│   FastAPI     │ │  chat_worker  │ │ file_scanner  │
└───────────────┘ └───────────────┘ └───────────────┘
```

**Problemi**:
1. **Nessun AnimationManager** - Animazioni gestite localmente in ogni view
2. **Signal/Slot non disconnessi** - Worker emettono segnali dopo distruzione view
3. **Nessun guard su widget lifecycle** - Accesso a widget senza verifica esistenza
4. **Transizioni non atomiche** - View distrutta prima che animazione finisca

### File Critici da Modificare

| File | LOC | Rischio | Motivo |
|------|-----|---------|--------|
| `desktop_app/views/login_view.py` | ~900 | 🔴 Alto | Crash confermato |
| `desktop_app/components/animated_widgets.py` | ~200 | 🔴 Alto | Base di tutti i widget animati |
| `desktop_app/components/animated_stacked_widget.py` | ~150 | 🔴 Alto | Transizioni tra view |
| `desktop_app/main.py` | ~400 | 🔴 Alto | Controller applicazione |
| `desktop_app/main_window_ui.py` | ~600 | 🟡 Medio | Gestione view stack |
| `desktop_app/views/splash_screen.py` | ~200 | 🟡 Medio | Prima transizione |
| `desktop_app/workers/*.py` | ~500 | 🟡 Medio | Signal emission |
| `desktop_app/components/toast.py` | ~150 | 🟡 Medio | Notifiche animate |
| `desktop_app/components/floating_chat_widget.py` | ~300 | 🟡 Medio | Widget fluttuante |

---

## 🛠️ Soluzione Proposta: Redesign Selettivo

### Principi Guida
1. **Mantieni stack tecnologico** - PyQt6 + FastAPI rimane
2. **Ridisegna moduli critici** - UI transitions, animation system
3. **Introduci pattern moderni** - AnimationManager, Event Bus, Guards
4. **Zero breaking changes esterni** - API e comportamento utente invariati

### Nuovi Componenti da Creare

```
desktop_app/
├── core/
│   ├── animation_manager.py      # NUOVO - Gestione centralizzata animazioni
│   ├── widget_guard.py           # NUOVO - Decorator e utility per widget safety
│   ├── error_boundary.py         # NUOVO - Exception handling a livello view
│   ├── state_machine.py          # NUOVO - Qt State Machine per transizioni
│   └── thread_manager.py         # ESISTENTE - Da potenziare
├── mixins/
│   ├── safe_widget_mixin.py      # NUOVO - Mixin per widget sicuri
│   └── animation_mixin.py        # NUOVO - Mixin per animazioni sicure
└── testing/
    └── user_simulation.py        # NUOVO - Framework test simulazione utente
```

---

## 📊 Struttura della Migrazione (9 Fasi)

```
FASE_0_OVERVIEW.md              ← Sei qui (Contesto generale)
FASE_1_WIDGET_LIFECYCLE.md      → Widget Lifecycle Guard System
FASE_2_ANIMATION_MANAGER.md     → AnimationManager centralizzato
FASE_3_SIGNAL_SLOT.md           → Signal/Slot Hardening
FASE_4_ERROR_BOUNDARIES.md      → Error Boundaries & Self-Healing
FASE_5_STATE_MACHINE.md         → Qt State Machine per transizioni
FASE_6_OBSERVABILITY.md         → Sentry enhancement, PostHog removal
FASE_7_USER_SIMULATION.md       → Test simulazione utente reale
FASE_8_DOCUMENTATION.md         → Update documentazione
```

### ⚠️ CRITICAL PATH
Le fasi **1**, **2** e **4** sono **bloccanti**:
- **FASE 1**: Senza guard, ogni accesso a widget può crashare
- **FASE 2**: Senza AnimationManager, animazioni restano incontrollabili
- **FASE 4**: Senza Error Boundaries, errori propagano e crashano

---

## 🧪 Strategia di Testing

### Test Pre-Migrazione (Baseline)
```bash
# 1. Esegui test suite esistente
pytest tests/ -v --tb=short > pre_migration_tests.log

# 2. Conta test esistenti
pytest tests/ --collect-only | tail -5

# 3. Verifica coverage attuale
pytest tests/ --cov=desktop_app --cov-report=html
```

### Test Post-Ogni-Fase
Dopo ogni fase:
1. ✅ `pytest tests/` deve rimanere green
2. ✅ Nuovo test specifico della fase deve passare
3. ✅ Test di simulazione utente deve passare

### Test di Simulazione Utente (NUOVO)
Creeremo test automatici che simulano:
- Avvio applicazione completo
- Login con credenziali valide/invalide
- Navigazione tra tutte le view
- Import file (drag & drop simulato)
- Apertura/chiusura dialoghi
- Stress test: azioni rapide ripetute
- Edge case: doppio click, azioni durante transizioni

---

## 📈 Metriche di Successo

| Metrica | Target | Baseline | Come Misurare |
|---------|--------|----------|---------------|
| **Crash Rate** | 0% | ~5% stimato | Stress test 1000 azioni |
| **Test Coverage** | >80% | Da verificare | `pytest --cov` |
| **Tempo Avvio** | <2s | ~3-4s | Profiling |
| **User Simulation Pass** | 100% | N/A | Nuovi test |
| **Memory Leaks** | 0 | Da verificare | `tracemalloc` |
| **PostHog References** | 0 | Da contare | `grep -r "posthog"` |

---

## 🔧 Tools & Risorse Necessari

### Software (Già Presente)
- [x] Python 3.12
- [x] PyQt6 6.8.0
- [x] pytest + pytest-qt
- [x] Sentry SDK

### Da Verificare/Installare
- [ ] `pytest-qt` per test GUI headless
- [ ] `pytest-xvfb` per CI senza display
- [ ] `pytest-timeout` per test con timeout
- [ ] `pytest-repeat` per stress test

### Comandi di Verifica
```bash
# Verifica pytest-qt
pip show pytest-qt

# Installa se mancante
pip install pytest-qt pytest-xvfb pytest-timeout pytest-repeat
```

---

## 🚨 Red Flags & Checkpoints

### ✅ Checklist Pre-Volo
- [ ] Repository pulito (`git status` clean)
- [ ] Tag di backup creato (`git tag v_pre_crash_zero`)
- [ ] Test esistenti passano (`pytest tests/`)
- [ ] Documentazione letta (tutti i file `docs/*.md`)
- [ ] Ambiente virtuale attivo

### 🔴 Quando Fermarsi e Chiedere Aiuto
1. **Test esistenti falliscono** → Ripristina, analizza il problema
2. **Crash durante sviluppo** → Documenta, non procedere
3. **Merge conflict** → Risolvi prima di continuare
4. **Dubbio architetturale** → Chiedi prima di implementare

---

## 📝 Formato Report Post-Fase

Dopo ogni fase, crea un file `FASE_X_REPORT.md`:

```markdown
# Report FASE X: [Nome Fase]

## ✅ Completato
- [x] Task 1
- [x] Task 2

## ⚠️ Problemi Incontrati
- Descrizione problema
- Soluzione applicata

## 🧪 Test Eseguiti
- Test 1: PASS/FAIL
- Test 2: PASS/FAIL

## 📊 File Modificati
| File | Modifiche |
|------|-----------|
| path/to/file.py | Descrizione |

## ⏱️ Tempo Impiegato
[Es: 2 ore]

## ⭐ Pronto per Fase Successiva: SÌ/NO
```

---

## 🎯 Prossimo Step: FASE 1

**Sei pronto?** Se hai letto questo overview:
→ **Apri `FASE_1_WIDGET_LIFECYCLE.md`** e inizia! 🚀

---

**Timestamp**: Dicembre 2024
**Autore**: Claude (AI Agent)
**Versione**: 1.0.0
**Progetto**: Intelleo Crash Zero Initiative
