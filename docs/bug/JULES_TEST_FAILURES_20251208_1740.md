# 🧪 Test Failures - Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-08 17:40
**File sorgente:** junit.xml

## 📊 Statistiche Test

| Metrica | Valore |
|---------|--------|
| Test totali | 580 |
| ✅ Passati | 575 |
| ❌ Falliti | 5 |
| 💥 Errori | 0 |
| ⏭️ Skippati | 0 |
| ⏱️ Tempo | 113.03s |
| Success Rate | 99.1% |

## 🏷️ Tipi di Errore

| Tipo | Count | Descrizione |
|------|-------|-------------|
| ❌ AssertionError | 4 | Il test ha verificato una condizione che... |
| 🔍 AttributeError | 1 | Tentativo di accedere a un attributo ine... |

## 📝 Istruzioni per Jules

Per ogni test fallito troverai:
- 📍 **Posizione**: File e nome del test
- ❌ **Errore**: Messaggio e tipo di errore
- 📜 **Stack Trace**: Traceback completo
- ❓ **Perché fallisce**: Spiegazione del tipo di errore
- ✅ **Come risolvere**: Suggerimenti specifici
- 📚 **Risorse**: Link utili

---

## 📄 `tests/app/core/test_db_security_failures/TestDBSecurityFailures.py`
**5 test falliti**

### ❌ `test_heartbeat_failure_triggers_readonly`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_failures.TestDBSecurityFailures::test_heartbeat_failure_triggers_readonly` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 107 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AttributeError: 'method' object has no attribute 'return_value'
```

**📜 Stack Trace:**

```python
self = <test_db_security_failures.TestDBSecurityFailures testMethod=test_heartbeat_failure_triggers_readonly>

    def test_heartbeat_failure_triggers_readonly(self):
        """Test that 3 heartbeat failures force read-only mode."""
        mgr = DBSecurityManager()
        mgr.is_read_only = False
>       mgr.lock_manager.update_heartbeat.return_value = False
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'method' object has no attribute 'return_value'

tests\app\core\test_db_security_failures.py:107: AttributeError
```

**❓ Perché fallisce:**

Tentativo di accedere a un attributo inesistente

**Causa probabile:** L'oggetto non ha l'attributo richiesto, potrebbe essere None o di tipo errato

**✅ Come risolvere:**

1. Verifica che l'oggetto non sia None prima di accedere all'attributo
2. Controlla il tipo dell'oggetto con isinstance()
3. Verifica che l'attributo esista nella classe/modulo
4. Usa getattr() con un valore di default se l'attributo è opzionale

**📚 Risorse:**

- https://docs.python.org/3/library/functions.html#getattr

---

### ❌ `test_move_database_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_failures.TestDBSecurityFailures::test_move_database_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.004s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'save_mutable_settings' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='settings.save_mutable_settings' id='1920112141728'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'save_mutable_settings' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
            with patch('pathlib.Path.mkdir'): # prevent actual mkdir globally
                # We already mocked settings in setUp via app.core.db_security.settings
    
                mgr.move_database(target)
    
                m_move.assert_called_with(str(old_path), str(target / 'db.db'))
>               self.mock_settings.save_mutable_settings.assert_called()
E               AssertionError: Expected 'save_mutable_settings' to have been called.

tests\app\core\test_db_security_failures.py:244: AssertionError
```

**❓ Perché fallisce:**

Il test ha verificato una condizione che si è rivelata falsa

**Causa probabile:** Il valore atteso non corrisponde al valore ottenuto

**✅ Come risolvere:**

1. Verifica che il valore atteso nel test sia corretto
2. Se il test è corretto, il bug è nel codice sotto test - correggilo
3. Se il comportamento è cambiato intenzionalmente, aggiorna il test
4. Controlla se ci sono effetti collaterali o stato condiviso tra test

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/assert.html

---

### ❌ `test_stale_lock_recovery_corrupt_json`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_failures.TestDBSecurityFailures::test_stale_lock_recovery_corrupt_json` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.007s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'remove' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='remove' id='1920117283184'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'remove' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
            with patch('app.core.db_security.os.remove') as m_remove:
                # Initialize manager (triggering the check)
                mgr = DBSecurityManager()
    
                # Verify removal was attempted
                # Note: mock_exists.return_value applies to ALL path checks, including lock path
>               m_remove.assert_called()
E               AssertionError: Expected 'remove' to have been called.

tests\app\core\test_db_security_failures.py:62: AssertionError
```

**❓ Perché fallisce:**

Il test ha verificato una condizione che si è rivelata falsa

**Causa probabile:** Il valore atteso non corrisponde al valore ottenuto

**✅ Come risolvere:**

1. Verifica che il valore atteso nel test sia corretto
2. Se il test è corretto, il bug è nel codice sotto test - correggilo
3. Se il comportamento è cambiato intenzionalmente, aggiorna il test
4. Controlla se ci sono effetti collaterali o stato condiviso tra test

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/assert.html

---

### ❌ `test_stale_lock_recovery_dead_pid`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_failures.TestDBSecurityFailures::test_stale_lock_recovery_dead_pid` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.005s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'remove' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='remove' id='1920116325696'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'remove' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
        mock_file_content = b'L' + lock_data
    
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('app.core.db_security.psutil.pid_exists', return_value=False):
                with patch('app.core.db_security.os.remove') as m_remove:
                    mgr = DBSecurityManager()
>                   m_remove.assert_called()
E                   AssertionError: Expected 'remove' to have been called.

tests\app\core\test_db_security_failures.py:74: AssertionError
```

**❓ Perché fallisce:**

Il test ha verificato una condizione che si è rivelata falsa

**Causa probabile:** Il valore atteso non corrisponde al valore ottenuto

**✅ Come risolvere:**

1. Verifica che il valore atteso nel test sia corretto
2. Se il test è corretto, il bug è nel codice sotto test - correggilo
3. Se il comportamento è cambiato intenzionalmente, aggiorna il test
4. Controlla se ci sono effetti collaterali o stato condiviso tra test

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/assert.html

---

### ❌ `test_stale_lock_recovery_unrelated_process`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_failures.TestDBSecurityFailures::test_stale_lock_recovery_unrelated_process` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.006s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'remove' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='remove' id='1920116980432'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'remove' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('app.core.db_security.psutil.pid_exists', return_value=True):
                with patch('app.core.db_security.psutil.Process') as m_proc:
                    m_proc.return_value.name.return_value = "chrome.exe"
                    with patch('app.core.db_security.os.remove') as m_remove:
                        mgr = DBSecurityManager()
>                       m_remove.assert_called()
E                       AssertionError: Expected 'remove' to have been called.

tests\app\core\test_db_security_failures.py:88: AssertionError
```

**❓ Perché fallisce:**

Il test ha verificato una condizione che si è rivelata falsa

**Causa probabile:** Il valore atteso non corrisponde al valore ottenuto

**✅ Come risolvere:**

1. Verifica che il valore atteso nel test sia corretto
2. Se il test è corretto, il bug è nel codice sotto test - correggilo
3. Se il comportamento è cambiato intenzionalmente, aggiorna il test
4. Controlla se ci sono effetti collaterali o stato condiviso tra test

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/assert.html

---
