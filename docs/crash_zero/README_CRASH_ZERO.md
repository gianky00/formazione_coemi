# 🚀 Guida alla Migrazione "Crash Zero"

**Versione**: 1.0  
**Data**: Dicembre 2024  
**Target**: Intelleo Project - Eliminazione Completa Crash

---

## 📚 Panoramica

Questa migrazione trasforma Intelleo in un'applicazione **enterprise-grade** con:
- ✅ **Zero crash** in qualsiasi scenario d'uso
- ✅ **Self-healing** - Recovery automatico da errori
- ✅ **Observability completa** - Sentry + logging strutturato
- ✅ **Test di simulazione utente** - Copertura scenari reali

**Risultati Attesi**:
- 🎯 Crash rate: **0%** (da ~5% stimato)
- 🎯 Test coverage: **>80%**
- 🎯 User simulation tests: **100% pass**

---

## 📁 Struttura File della Migrazione

Hai ricevuto **11 file markdown** che devono essere eseguiti **SEQUENZIALMENTE**:

```
FASE_0_OVERVIEW.md              ← Leggi SEMPRE per primo (contesto)
├── FASE_1_WIDGET_LIFECYCLE.md  → Widget Lifecycle Guard System
├── FASE_2_ANIMATION_MANAGER.md → AnimationManager centralizzato
├── FASE_3_SIGNAL_SLOT.md       → Signal/Slot Hardening  
├── FASE_4_ERROR_BOUNDARIES.md  → Error Boundaries & Self-Healing
├── FASE_5_STATE_MACHINE.md     → Qt State Machine per transizioni
├── FASE_6_OBSERVABILITY.md     → Sentry enhancement, -PostHog
├── FASE_7_USER_SIMULATION.md   → Test simulazione utente reale
├── FASE_8_DOCUMENTATION.md     → Update docs completo
├── README_CRASH_ZERO.md        ← Sei qui (Quick Start)
└── CURSOR_PROMPTS_READY.md     → Prompts per Cursor/Opus 4.5
```

---

## ⚡ Quick Start (Per Cursor/Jules)

### Step 0: Preparazione
```bash
# Backup del repository
git tag v_pre_crash_zero -m "Backup before Crash Zero migration"
git push origin v_pre_crash_zero

# Verifica test esistenti
pytest tests/ -v --tb=short

# Conta riferimenti PostHog (da rimuovere in Fase 6)
grep -r "posthog" --include="*.py" | wc -l
```

### Step 1: Leggi Overview
```bash
# Apri e leggi completamente
FASE_0_OVERVIEW.md
```
**Checklist**:
- [ ] Ho capito il crash pattern (Widget Lifecycle Violation)
- [ ] Ho letto la lista dei file critici
- [ ] So che le Fasi 1, 2, 4 sono CRITICHE

### Step 2: Esegui Fasi Sequenzialmente

**⚠️ NON saltare fasi!** Ogni fase dipende dalla precedente.

```bash
# ═══════════════════════════════════════════════════════════
# FASE 1: Widget Lifecycle Guard (90 min)
# ═══════════════════════════════════════════════════════════
# Leggi FASE_1_WIDGET_LIFECYCLE.md
# Crea desktop_app/core/widget_guard.py
# Crea desktop_app/mixins/safe_widget_mixin.py
pytest tests/desktop_app/core/test_widget_guard.py  # DEVE passare

# ═══════════════════════════════════════════════════════════
# FASE 2: Animation Manager (120 min) 🏗️ CRITICA
# ═══════════════════════════════════════════════════════════
# Leggi FASE_2_ANIMATION_MANAGER.md
# Crea desktop_app/core/animation_manager.py
# Refactora animated_widgets.py, login_view.py, etc.
pytest tests/desktop_app/core/test_animation_manager.py  # DEVE passare

# ═══════════════════════════════════════════════════════════
# FASE 3: Signal/Slot Hardening (60 min)
# ═══════════════════════════════════════════════════════════
# Leggi FASE_3_SIGNAL_SLOT.md
# Crea desktop_app/core/signal_guard.py
# Refactora workers/*.py
pytest tests/desktop_app/workers/test_signal_safety.py  # DEVE passare

# ═══════════════════════════════════════════════════════════
# FASE 4: Error Boundaries (90 min) 🏗️ CRITICA
# ═══════════════════════════════════════════════════════════
# Leggi FASE_4_ERROR_BOUNDARIES.md
# Crea desktop_app/core/error_boundary.py
# Applica a tutte le view
pytest tests/desktop_app/core/test_error_boundary.py  # DEVE passare

# ═══════════════════════════════════════════════════════════
# FASE 5: State Machine (120 min)
# ═══════════════════════════════════════════════════════════
# Leggi FASE_5_STATE_MACHINE.md
# Crea desktop_app/core/state_machine.py
# Integra in main.py per gestire transizioni
pytest tests/desktop_app/core/test_state_machine.py  # DEVE passare

# ═══════════════════════════════════════════════════════════
# FASE 6: Observability (60 min)
# ═══════════════════════════════════════════════════════════
# Leggi FASE_6_OBSERVABILITY.md
# Rimuovi TUTTI i riferimenti PostHog
# Potenzia integrazione Sentry
grep -r "posthog" --include="*.py"  # DEVE essere vuoto
pytest tests/  # DEVE essere 100% green

# ═══════════════════════════════════════════════════════════
# FASE 7: User Simulation Testing (180 min) 🧪 CRITICA
# ═══════════════════════════════════════════════════════════
# Leggi FASE_7_USER_SIMULATION.md
# Crea tests/desktop_app/simulation/
# Implementa tutti gli scenari di test
pytest tests/desktop_app/simulation/ -v  # DEVE dare 100% pass

# ═══════════════════════════════════════════════════════════
# FASE 8: Documentation (60 min)
# ═══════════════════════════════════════════════════════════
# Leggi FASE_8_DOCUMENTATION.md
# Aggiorna docs/DESKTOP_CLIENT.md
# Aggiorna docs/CONTRIBUTING.md
# Crea docs/CRASH_ZERO_ARCHITECTURE.md
```

### Step 3: Verifica Finale
```bash
# Test completi?
pytest tests/ -v  # 100% green

# User simulation?
pytest tests/desktop_app/simulation/ -v  # 100% pass

# Stress test?
pytest tests/desktop_app/simulation/test_stress.py -v  # 100% pass

# PostHog rimosso?
grep -r "posthog" --include="*.py"  # Vuoto

# Coverage?
pytest tests/ --cov=desktop_app --cov-report=html
# Apri htmlcov/index.html -> deve essere >80%
```

---

## 🎯 Metriche di Successo (Criteri di Completamento)

La migrazione è **completa e validata** solo se:

| Criterio | Target | Come Verificare |
|----------|--------|-----------------|
| **Pytest Pass** | 100% | `pytest tests/ -v` |
| **User Simulation** | 100% pass | `pytest tests/desktop_app/simulation/` |
| **Stress Test** | 0 crash su 1000 azioni | `test_stress.py` |
| **Coverage** | >80% | `pytest --cov` |
| **PostHog Refs** | 0 | `grep -r "posthog"` |
| **Memory Leaks** | 0 | `test_memory_leaks.py` |
| **Sentry Integration** | Funzionante | Test manuale |

---

## ⚠️ Red Flags & Quando Fermarsi

**STOP e chiedi aiuto se**:

### Durante Fase 1 (Widget Guard)
- ❌ Import circolari dopo aggiunta mixin
- ❌ Test esistenti iniziano a fallire
- ❌ `TypeError` su classi esistenti

### Durante Fase 2 (Animation Manager)
- ❌ Animazioni non partono più
- ❌ UI si blocca durante transizioni
- ❌ Memory leak (RAM cresce continuamente)

### Durante Fase 4 (Error Boundaries)
- ❌ Errori vengono "swallowed" silenziosamente
- ❌ UI in stato inconsistente dopo recovery
- ❌ Sentry non riceve più eventi

### Durante Fase 7 (User Simulation)
- ❌ Test flaky (passano/falliscono random)
- ❌ Test richiedono display fisico
- ❌ Timeout frequenti

---

## 📊 Report Post-Fase (Template)

Dopo ogni fase, crea un file `FASE_X_REPORT.md`:

```markdown
# FASE X REPORT: [Nome Fase]

## ✅ Completato
- [x] Task 1
- [x] Task 2

## ⚠️ Problemi Incontrati
- Nessuno / [Descrizione + soluzione]

## 🧪 Test Eseguiti
| Test | Risultato |
|------|-----------|
| test_xxx | ✅ PASS |
| test_yyy | ✅ PASS |

## 📊 File Creati/Modificati
| File | Azione | LOC |
|------|--------|-----|
| core/widget_guard.py | Creato | 150 |
| views/login_view.py | Modificato | +20/-5 |

## ⏱️ Tempo Impiegato
[Es: 90 minuti]

## 📈 Metriche
- Test coverage delta: +X%
- Nuovi test aggiunti: N

## ⏭️ Pronto per Fase Successiva: ✅ SÌ
```

---

## 🛠️ Troubleshooting Comune

### Errore: Import Circolare
```python
# PROBLEMA
from desktop_app.core.widget_guard import SafeWidgetMixin
# ImportError: circular import

# SOLUZIONE: Usa TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from desktop_app.core.widget_guard import SafeWidgetMixin
```

### Errore: Widget Already Deleted
```python
# PROBLEMA
RuntimeError: wrapped C/C++ object has been deleted

# SOLUZIONE: Usa il guard
from desktop_app.core.widget_guard import is_widget_alive

if is_widget_alive(self.button):
    self.button.setText("Safe!")
```

### Test Flaky (Random Pass/Fail)
```python
# PROBLEMA: Test dipende da timing

# SOLUZIONE: Usa qtbot.waitUntil
qtbot.waitUntil(lambda: widget.isVisible(), timeout=5000)
```

### Animazione Non Si Ferma
```python
# PROBLEMA: Animazione continua dopo distruzione view

# SOLUZIONE: Usa AnimationManager
from desktop_app.core.animation_manager import animation_manager

# Nella view
def closeEvent(self, event):
    animation_manager.cancel_all(owner=self)
    super().closeEvent(event)
```

---

## 📞 Supporto & Escalation

**Per problemi bloccanti**:
1. Leggi la sezione "Troubleshooting" della fase corrente
2. Cerca in `FASE_0_OVERVIEW.md` → "Red Flags"
3. Controlla che tutte le checklist delle fasi precedenti siano ✅
4. Se ancora bloccato: crea issue con:
   - Fase corrente
   - Comando eseguito
   - Output completo errore
   - File modificati

---

## 🎉 Completamento Migrazione

Quando hai finito **tutte le 8 fasi**:

1. **Tag Git**:
   ```bash
   git tag -a v_crash_zero_complete -m "✅ Crash Zero migration completed"
   git push origin v_crash_zero_complete
   ```

2. **Verifica Finale**:
   ```bash
   # Full test suite
   pytest tests/ -v --tb=short
   
   # User simulation
   pytest tests/desktop_app/simulation/ -v
   
   # Coverage report
   pytest tests/ --cov=desktop_app --cov-report=html
   ```

3. **Documentazione**:
   - Verifica che `docs/CRASH_ZERO_ARCHITECTURE.md` sia completo
   - Aggiorna `docs/README.md` con link alla nuova doc

4. **Cleanup**:
   - Rimuovi file temporanei
   - Rimuovi commenti TODO risolti
   - Verifica che non ci siano `print()` di debug

---

## 📚 Risorse Aggiuntive

- **PyQt6 Docs**: https://doc.qt.io/qtforpython-6/
- **Qt State Machine**: https://doc.qt.io/qt-6/qtstatemachine-overview.html
- **Sentry Python**: https://docs.sentry.io/platforms/python/
- **pytest-qt**: https://pytest-qt.readthedocs.io/

---

**Buona fortuna! 🚀**

*Questa migrazione richiederà circa 12-16 ore di lavoro totale. Procedi con calma, non saltare step, e testa dopo ogni fase.*

---

**Versione**: 1.0  
**Autore**: Claude (AI Agent)  
**Last Update**: Dicembre 2024
