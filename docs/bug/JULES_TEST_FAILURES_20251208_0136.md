# 🧪 Test Failures - Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-08 01:36
**File sorgente:** junit.xml

## 📊 Statistiche Test

| Metrica | Valore |
|---------|--------|
| Test totali | 583 |
| ✅ Passati | 523 |
| ❌ Falliti | 44 |
| 💥 Errori | 0 |
| ⏭️ Skippati | 16 |
| ⏱️ Tempo | 103.90s |
| Success Rate | 89.7% |

## 🏷️ Tipi di Errore

| Tipo | Count | Descrizione |
|------|-------|-------------|
| ❌ AssertionError | 31 | Il test ha verificato una condizione che... |
| ❓  | 7 | Errore durante l'esecuzione del test... |
| 🔍 AttributeError | 4 | Tentativo di accedere a un attributo ine... |
| ❓ Failed | 1 | Errore durante l'esecuzione del test... |
| ❓ Exception | 1 | Errore durante l'esecuzione del test... |

## 📝 Istruzioni per Jules

Per ogni test fallito troverai:
- 📍 **Posizione**: File e nome del test
- ❌ **Errore**: Messaggio e tipo di errore
- 📜 **Stack Trace**: Traceback completo
- ❓ **Perché fallisce**: Spiegazione del tipo di errore
- ✅ **Come risolvere**: Suggerimenti specifici
- 📚 **Risorse**: Link utili

---

## 📄 `tests/app/api/test_csv_orphan_sync.py`
**1 test falliti**

### ❌ `test_csv_import_moves_orphan_file`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_csv_orphan_sync::test_csv_import_moves_orphan_file` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 58 |
| Tempo | 0.023s |

**❌ Messaggio di Errore:**

```
AssertionError: Old orphan file should be moved
assert not True
 +  where True = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Bianchi Mario (N-A)\\ANTINCENDIO\\ATTIVO\\Bianchi Mario (N-A) - ANTINCENDIO - 01_01_2030.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x0000023A499E6C30>, db_session = <sqlalchemy.orm.session.Session object at 0x0000023A49815C10>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0')

    def test_csv_import_moves_orphan_file(test_client, db_session, test_dirs):
        # 1. Setup Orphan Cert
        cat = "ANTINCENDIO"
        orphan_name = "Bianchi Mario"
        corso = Corso(nome_corso="Corso A", categoria_corso=cat)
        cert = Certificato(
            dipendente_id=None,
            nome_dipendente_raw=orphan_name,
            corso=corso,
            data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
            data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date()
        )
... (troncato) ...
        # 6. Verify File Move
        # Old path should be gone
>       assert not os.path.exists(orphan_path), "Old orphan file should be moved"
E       AssertionError: Old orphan file should be moved
E       assert not True
E        +  where True = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Bianchi Mario (N-A)\\ANTINCENDIO\\ATTIVO\\Bianchi Mario (N-A) - ANTINCENDIO - 01_01_2030.pdf')
E        +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
E        +      where <module 'ntpath' (frozen)> = os.path

tests\app\api\test_csv_orphan_sync.py:58: AssertionError
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

## 📄 `tests/app/api/test_delete_cert_file_cleanup.py`
**1 test falliti**

### ❌ `test_delete_certificate_deletes_file`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_delete_cert_file_cleanup::test_delete_certificate_deletes_file` |
| Tipo Errore | ❓ Failed |
| Status | FAILURE |
| Riga | 55 |
| Tempo | 0.022s |

**❌ Messaggio di Errore:**

```
Failed: File was not removed from original location.
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x0000023A498070B0>, db_session = <sqlalchemy.orm.session.Session object at 0x0000023A49805220>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0')

    def test_delete_certificate_deletes_file(test_client, db_session, test_dirs):
        # 1. Setup Data in DB
        cat = "ANTINCENDIO"
        dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
        corso = Corso(nome_corso="Corso A", categoria_corso=cat)
        cert = Certificato(
            dipendente=dip,
            corso=corso,
            data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
            data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date()
        )
    
... (troncato) ...
    
        # 4. Verify DB deletion
        assert db_session.get(Certificato, cert_id) is None
    
        # 5. Verify File deletion from original location
        if os.path.exists(file_path):
>           pytest.fail("File was not removed from original location.")
E           Failed: File was not removed from original location.

tests\app\api\test_delete_cert_file_cleanup.py:55: Failed
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

## 📄 `tests/app/api/test_employee_hooks.py`
**1 test falliti**

### ❌ `test_create_employee_links_orphan`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_employee_hooks::test_create_employee_links_orphan` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 66 |
| Tempo | 0.020s |

**❌ Messaggio di Errore:**

```
AssertionError: assert False
 +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2030.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x0000023A4977AE10>, db_session = <sqlalchemy.orm.session.Session object at 0x0000023A49778EC0>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0')

    def test_create_employee_links_orphan(test_client, db_session, test_dirs):
        # Setup Orphan Cert
        cat = "ANTINCENDIO"
        orphan_name = "Mario Rossi"
        corso = Corso(nome_corso="Corso A", categoria_corso=cat)
        cert = Certificato(
            dipendente_id=None,
            nome_dipendente_raw=orphan_name,
            corso=corso,
            data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
            data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date()
        )
... (troncato) ...
                    print(os.path.join(dirpath, f))
            print("----------------------------\n")
    
>       assert os.path.exists(new_path)
E       AssertionError: assert False
E        +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2030.pdf')
E        +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
E        +      where <module 'ntpath' (frozen)> = os.path

tests\app\api\test_employee_hooks.py:66: AssertionError
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

## 📄 `tests/app/api/test_realtime_archiving.py`
**1 test falliti**

### ❌ `test_realtime_archiving_on_create`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_realtime_archiving::test_realtime_archiving_on_create` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 60 |
| Tempo | 0.019s |

**❌ Messaggio di Errore:**

```
AssertionError: Old file should be archived
assert False
 +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\STORICO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x0000023A496E3380>, db_session = <sqlalchemy.orm.session.Session object at 0x0000023A49850EC0>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0')

    def test_realtime_archiving_on_create(test_client, db_session, test_dirs):
        # Setup Data
        cat = "ANTINCENDIO"
        dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
        corso = Corso(nome_corso="Corso A", categoria_corso=cat)
        # Old cert (Valid but old)
        cert_old = Certificato(
            dipendente=dip,
            corso=corso,
            data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
            data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date()
        )
... (troncato) ...
            print("----------------------------\n")
    
>       assert os.path.exists(archived_path), "Old file should be archived"
E       AssertionError: Old file should be archived
E       assert False
E        +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\STORICO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf')
E        +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
E        +      where <module 'ntpath' (frozen)> = os.path

tests\app\api\test_realtime_archiving.py:60: AssertionError
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

## 📄 `tests/app/api/test_update_cert_file_sync.py`
**1 test falliti**

### ❌ `test_find_document_direct`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_update_cert_file_sync::test_find_document_direct` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 79 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
assert None is not None
```

**📜 Stack Trace:**

```python
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0')

    def test_find_document_direct(test_dirs):
        from app.services.document_locator import find_document
    
        # Setup
        cat = "ANTINCENDIO"
        nome_fs = sanitize_filename("Rossi Mario")
        matr_fs = sanitize_filename("123")
        cat_fs = sanitize_filename(cat)
        filename = f"{nome_fs} ({matr_fs}) - {cat_fs} - 01_01_2030.pdf"
    
        folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} ({matr_fs})", cat_fs, "ATTIVO")
        os.makedirs(folder, exist_ok=True)
        old_path = os.path.join(folder, filename)
        with open(old_path, "w") as f: f.write("content")
    
        cert_data = {
            'nome': "Rossi Mario",
            'matricola': "123",
            'categoria': "ANTINCENDIO",
            'data_scadenza': "01/01/2030"
        }
    
        found_path = find_document(str(test_dirs), cert_data)
>       assert found_path is not None
E       assert None is not None

tests\app\api\test_update_cert_file_sync.py:79: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

## 📄 `tests/app/core/test_db_security_integration.py`
**1 test falliti**

### ❌ `test_initialization_creates_files`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_db_security_integration::test_initialization_creates_files` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 46 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: assert WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0/test_secure.db') == (WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/test_initialization_creates_fi0') / 'test_secure.db')
 +  where WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0/test_secure.db') = <app.core.db_security.DBSecurityManager object at 0x0000023A492D64B0>.db_path
```

**📜 Stack Trace:**

```python
secure_db_env = (WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/test_initialization_creates_fi0'), <app.core.db_security.DBSecurityManager object at 0x0000023A492D64B0>, 'test_secure.db')

    def test_initialization_creates_files(secure_db_env):
        tmp_path, manager, db_name = secure_db_env
    
        # DB path should be set correctly
>       assert manager.db_path == tmp_path / db_name
E       AssertionError: assert WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0/test_secure.db') == (WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/test_initialization_creates_fi0') / 'test_secure.db')
E        +  where WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-45/data0/test_secure.db') = <app.core.db_security.DBSecurityManager object at 0x0000023A492D64B0>.db_path

tests\app\core\test_db_security_integration.py:46: AssertionError
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

## 📄 `tests/app/core/test_lock_manager_deep.py`
**1 test falliti**

### ❌ `test_acquire_generic_exception`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.core.test_lock_manager_deep::test_acquire_generic_exception` |
| Tipo Errore | ❓ Exception |
| Status | FAILURE |
| Riga | 27 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
Exception: Generic Fail
```

**📜 Stack Trace:**

```python
mock_path = 'C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-45\\test_acquire_generic_exception0\\.lock'

    def test_acquire_generic_exception(mock_path):
        mgr = LockManager(mock_path)
    
        with patch("builtins.open", side_effect=Exception("Generic Fail")):
>           success, owner = mgr.acquire({"uuid": "1"}, retries=0)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\app\core\test_lock_manager_deep.py:27: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
app\core\lock_manager.py:66: in acquire
    self._init_lock_file()
app\core\lock_manager.py:29: in _init_lock_file
    with open(self.lock_file_path, 'wb') as f:
... (troncato) ...
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method
    
        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               Exception: Generic Fail

C:\Program Files\Python312\Lib\unittest\mock.py:1198: Exception
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

## 📄 `tests/app/services/test_document_locator.py`
**4 test falliti**

### ❌ `test_find_document_success_active`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.services.test_document_locator::test_find_document_success_active` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 30 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\ROSSI MARIO (12345)\\ANTINCENDIO\\ATTIVO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'
```

**📜 Stack Trace:**

```python
mock_db_path = '\\mock\\db\\path', base_cert_data = {'categoria': 'ANTINCENDIO', 'data_scadenza': '31/12/2025', 'matricola': '12345', 'nome': 'ROSSI MARIO'}

    def test_find_document_success_active(mock_db_path, base_cert_data):
        """Test finding a document in the primary status folder (ATTIVO)."""
        expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
        expected_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "ROSSI MARIO (12345)", "ANTINCENDIO", "ATTIVO", expected_filename)
    
        with patch("os.path.isfile") as mock_isfile:
            # Simulate file exists only at the expected path
            mock_isfile.side_effect = lambda x: x == expected_path
    
            result = find_document(mock_db_path, base_cert_data)
>           assert result == expected_path
E           AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\ROSSI MARIO (12345)\\ANTINCENDIO\\ATTIVO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'

tests\app\services\test_document_locator.py:30: AssertionError
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

### ❌ `test_find_document_success_fallback_status`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.services.test_document_locator::test_find_document_success_fallback_status` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 41 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\ROSSI MARIO (12345)\\ANTINCENDIO\\STORICO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'
```

**📜 Stack Trace:**

```python
mock_db_path = '\\mock\\db\\path', base_cert_data = {'categoria': 'ANTINCENDIO', 'data_scadenza': '31/12/2025', 'matricola': '12345', 'nome': 'ROSSI MARIO'}

    def test_find_document_success_fallback_status(mock_db_path, base_cert_data):
        """Test finding a document in a fallback status folder (e.g., STORICO)."""
        expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
        target_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "ROSSI MARIO (12345)", "ANTINCENDIO", "STORICO", expected_filename)
    
        with patch("os.path.isfile") as mock_isfile:
            mock_isfile.side_effect = lambda x: x == target_path
    
            result = find_document(mock_db_path, base_cert_data)
>           assert result == target_path
E           AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\ROSSI MARIO (12345)\\ANTINCENDIO\\STORICO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'

tests\app\services\test_document_locator.py:41: AssertionError
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

### ❌ `test_find_document_missing_matricola`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.services.test_document_locator::test_find_document_missing_matricola` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 60 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\VERDI LUIGI (N-A)\\VISITA MEDICA\\ATTIVO\\VERDI LUIGI (N-A) - VISITA MEDICA - 01_01_2024.pdf'
```

**📜 Stack Trace:**

```python
mock_db_path = '\\mock\\db\\path'

    def test_find_document_missing_matricola(mock_db_path):
        """Test that missing matricola defaults to 'N-A'."""
        cert_data = {
            "nome": "VERDI LUIGI",
            "matricola": None, # Missing
            "categoria": "VISITA MEDICA",
            "data_scadenza": "01/01/2024"
        }
    
        # Expect folder "VERDI LUIGI (N-A)"
        expected_filename = "VERDI LUIGI (N-A) - VISITA MEDICA - 01_01_2024.pdf"
        expected_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "VERDI LUIGI (N-A)", "VISITA MEDICA", "ATTIVO", expected_filename)
    
        with patch("os.path.isfile") as mock_isfile:
            mock_isfile.side_effect = lambda x: x == expected_path
    
            result = find_document(mock_db_path, cert_data)
>           assert result == expected_path
E           AssertionError: assert None == '\\mock\\db\\path\\DOCUMENTI DIPENDENTI\\VERDI LUIGI (N-A)\\VISITA MEDICA\\ATTIVO\\VERDI LUIGI (N-A) - VISITA MEDICA - 01_01_2024.pdf'

tests\app\services\test_document_locator.py:60: AssertionError
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

### ❌ `test_find_document_in_error_folders`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.services.test_document_locator::test_find_document_in_error_folders` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 85 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == '\\mock\\db\\path\\ERRORI ANALISI\\ASSENZA MATRICOLE\\ROSSI MARIO (12345)\\ANTINCENDIO\\ATTIVO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'
```

**📜 Stack Trace:**

```python
mock_db_path = '\\mock\\db\\path', base_cert_data = {'categoria': 'ANTINCENDIO', 'data_scadenza': '31/12/2025', 'matricola': '12345', 'nome': 'ROSSI MARIO'}

    def test_find_document_in_error_folders(mock_db_path, base_cert_data):
        """Test finding a document in the ERRORI ANALISI structure."""
        expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
        # Structure: ERRORI ANALISI / <ErrCategory> / <EmployeeFolder> / <Category> / <Status> / <Filename>
        # Note: Logic iterates error_categories. Let's place it in "ASSENZA MATRICOLE"
        target_path = os.path.join(mock_db_path, "ERRORI ANALISI", "ASSENZA MATRICOLE", "ROSSI MARIO (12345)", "ANTINCENDIO", "ATTIVO", expected_filename)
    
        with patch("os.path.isfile") as mock_isfile:
            mock_isfile.side_effect = lambda x: x == target_path
    
            result = find_document(mock_db_path, base_cert_data)
>           assert result == target_path
E           AssertionError: assert None == '\\mock\\db\\path\\ERRORI ANALISI\\ASSENZA MATRICOLE\\ROSSI MARIO (12345)\\ANTINCENDIO\\ATTIVO\\ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf'

tests\app\services\test_document_locator.py:85: AssertionError
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

## 📄 `tests/app/services/test_document_locator_filename.py`
**1 test falliti**

### ❌ `test_find_document_sanitizes_path`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.services.test_document_locator_filename::test_find_document_sanitizes_path` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 31 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == '\\mock\\db\\DOCUMENTI DIPENDENTI\\De_Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\De_Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf'
```

**📜 Stack Trace:**

```python
def test_find_document_sanitizes_path():
        """
        This test verifies that document_locator correctly sanitizes input data
        to match the file system naming conventions.
        """
        db_path = "/mock/db"
        cert_data = {
            "nome": "De/Rossi Mario",
            "matricola": "123",
            "categoria": "ANTINCENDIO",
            "data_scadenza": "01/01/2025"
        }
    
        sanitized_folder = "De_Rossi Mario (123)"
        sanitized_filename = "De_Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf"
    
        expected_path = os.path.join(db_path, "DOCUMENTI DIPENDENTI", sanitized_folder, "ANTINCENDIO", "ATTIVO", sanitized_filename)
        expected_path = os.path.normpath(expected_path)
    
        with patch("os.path.isfile") as mock_isfile:
            mock_isfile.side_effect = lambda p: os.path.normpath(p) == expected_path
    
            result = find_document(db_path, cert_data)
    
            # This assertion will fail until the bug is fixed
>           assert result == expected_path
E           AssertionError: assert None == '\\mock\\db\\DOCUMENTI DIPENDENTI\\De_Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\De_Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf'

tests\app\services\test_document_locator_filename.py:31: AssertionError
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

## 📄 `tests/app/test_main_full.py`
**3 test falliti**

### ❌ `test_lifespan_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_main_full::test_lifespan_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 928 |
| Tempo | 0.012s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'load_memory_db' to have been called once. Called 0 times.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='db_security.load_memory_db' id='2449369929184'>

    def assert_called_once(self):
        """assert that the mock was called only once.
        """
        if not self.call_count == 1:
            msg = ("Expected '%s' to have been called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
>           raise AssertionError(msg)
E           AssertionError: Expected 'load_memory_db' to have been called once. Called 0 times.

C:\Program Files\Python312\Lib\unittest\mock.py:928: AssertionError

... (troncato) ...
            mock_sec.db_path.exists.return_value = True
    
            # Run lifespan
            async with lifespan(app):
                pass
    
>           mock_sec.load_memory_db.assert_called_once()
E           AssertionError: Expected 'load_memory_db' to have been called once. Called 0 times.

tests\app\test_main_full.py:37: AssertionError
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

### ❌ `test_lifespan_db_load_failure_fatal`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_main_full::test_lifespan_db_load_failure_fatal` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 51 |
| Tempo | 0.210s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == 'Fatal Lock'
 +  where None = <starlette.datastructures.State object at 0x0000023A48D62DE0>.startup_error
 +    where <starlette.datastructures.State object at 0x0000023A48D62DE0> = app.state
```

**📜 Stack Trace:**

```python
@pytest.mark.anyio
    async def test_lifespan_db_load_failure_fatal():
        with patch("app.main.db_security") as mock_sec:
            mock_sec.load_memory_db.side_effect = PermissionError("Fatal Lock")
    
            async with lifespan(app):
                pass
    
>           assert app.state.startup_error == "Fatal Lock"
E           AssertionError: assert None == 'Fatal Lock'
E            +  where None = <starlette.datastructures.State object at 0x0000023A48D62DE0>.startup_error
E            +    where <starlette.datastructures.State object at 0x0000023A48D62DE0> = app.state

tests\app\test_main_full.py:51: AssertionError
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

### ❌ `test_maintenance_task`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_main_full::test_maintenance_task` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 960 |
| Tempo | 0.019s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'organize_expired_files' to be called once. Called 0 times.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='organize_expired_files' id='2449369957728'>, args = (<MagicMock name='SessionLocal()' id='2449370163216'>,), kwargs = {}
msg = "Expected 'organize_expired_files' to be called once. Called 0 times."

    def assert_called_once_with(self, /, *args, **kwargs):
        """assert that the mock was called exactly once and that that call was
        with the specified arguments."""
        if not self.call_count == 1:
            msg = ("Expected '%s' to be called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
>           raise AssertionError(msg)
E           AssertionError: Expected 'organize_expired_files' to be called once. Called 0 times.

C:\Program Files\Python312\Lib\unittest\mock.py:960: AssertionError

During handling of the above exception, another exception occurred:

    def test_maintenance_task():
        with patch("app.main.SessionLocal") as mock_session_cls, \
             patch("app.main.organize_expired_files") as mock_org:
    
            mock_db = mock_session_cls.return_value
    
            run_maintenance_task()
    
>           mock_org.assert_called_once_with(mock_db)
E           AssertionError: Expected 'organize_expired_files' to be called once. Called 0 times.

tests\app\test_main_full.py:112: AssertionError
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

## 📄 `tests/desktop_app/services/test_security_service/TestSecurityService.py`
**3 test falliti**

### ❌ `test_is_virtual_environment_detects_process`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_security_service.TestSecurityService::test_is_virtual_environment_detects_process` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 20 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
assert False is True
```

**📜 Stack Trace:**

```python
self = <test_security_service.TestSecurityService object at 0x0000023A49301AF0>, mock_processes = <MagicMock name='_get_running_processes_wmi' id='2449388292528'>

    @patch('desktop_app.services.security_service.os.name', 'nt')
    # Patch where the name is used in security_service
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    def test_is_virtual_environment_detects_process(self, mock_processes):
        # Simulate VM process running
        # Must lowercase as the service does
        mock_processes.return_value = ["system", "svchost.exe", "vmtoolsd.exe"]
    
        is_vm, msg = is_virtual_environment()
    
        # Verify
>       assert is_vm is True
E       assert False is True

tests\desktop_app\services\test_security_service.py:20: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

### ❌ `test_is_virtual_environment_detects_file`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_security_service.TestSecurityService::test_is_virtual_environment_detects_file` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 36 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
assert False is True
```

**📜 Stack Trace:**

```python
self = <test_security_service.TestSecurityService object at 0x0000023A49301E50>, mock_exists = <MagicMock name='exists' id='2449388280128'>
mock_processes = <MagicMock name='_get_running_processes_wmi' id='2449388276240'>

    @patch('desktop_app.services.security_service.os.name', 'nt')
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    @patch('desktop_app.services.security_service.os.path.exists')
    def test_is_virtual_environment_detects_file(self, mock_exists, mock_processes):
        # Processes clean
        mock_processes.return_value = ["explorer.exe"]
    
        # Simulate VM driver file exists
        def side_effect(path):
            return path == r"C:\Windows\System32\drivers\vboxguest.sys"
        mock_exists.side_effect = side_effect
    
        is_vm, msg = is_virtual_environment()
>       assert is_vm is True
E       assert False is True

tests\desktop_app\services\test_security_service.py:36: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

### ❌ `test_is_analysis_tool_running_detects_wireshark`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_security_service.TestSecurityService::test_is_analysis_tool_running_detects_wireshark` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 55 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
assert False is True
```

**📜 Stack Trace:**

```python
self = <test_security_service.TestSecurityService object at 0x0000023A49302570>, mock_processes = <MagicMock name='_get_running_processes_wmi' id='2449389338256'>

    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    def test_is_analysis_tool_running_detects_wireshark(self, mock_processes):
        mock_processes.return_value = ["wireshark.exe", "chrome.exe"]
    
        is_tool, msg = is_analysis_tool_running()
>       assert is_tool is True
E       assert False is True

tests\desktop_app\services\test_security_service.py:55: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

## 📄 `tests/desktop_app/services/test_time_service_secure/TestSecureTimeStorage.py`
**1 test falliti**

### ❌ `test_save_state_encrypts`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestSecureTimeStorage::test_save_state_encrypts` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 949 |
| Tempo | 0.136s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: open('/tmp\\secure_time.dat', 'wb')
  Actual: open('C:\\Users\\gianc\\AppData\\Local\\Intelleo\\Licenza\\secure_time.dat', 'wb')

pytest introspection follows:

Args:
assert ('C:\\Users\\...me.dat', 'wb') == ('/tmp\\secur...me.dat', 'wb')
  
  At index 0 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mC:#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mUsers#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mgianc#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33m
```

**📜 Stack Trace:**

```python
self = <MagicMock name='open' id='2449359710464'>, args = ('/tmp\\secure_time.dat', 'wb'), kwargs = {}, expected = call('/tmp\\secure_time.dat', 'wb')
actual = call('C:\\Users\\gianc\\AppData\\Local\\Intelleo\\Licenza\\secure_time.dat', 'wb'), _error_message = <function NonCallableMock.assert_called_with.<locals>._error_message at 0x0000023A4B26B420>
cause = None

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
            raise AssertionError(error_message)
... (troncato) ...
E       
E       pytest introspection follows:
E       
E       Args:
E       assert ('C:\\Users\\...me.dat', 'wb') == ('/tmp\\secur...me.dat', 'wb')
E         
E         At index 0 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mC:#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mUsers#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mgianc#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mAppData#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mLocal#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mIntelleo#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mLicenza#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33msecure_time.dat#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m != #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33m/tmp#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33msecure_time.dat#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
E         Use -v to get more diff

tests\desktop_app\services\test_time_service_secure.py:22: AssertionError
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

## 📄 `tests/desktop_app/services/test_time_service_secure/TestTimeServiceLogic.py`
**5 test falliti**

### ❌ `test_check_system_clock_online_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_online_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.240s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'save_state' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='save_state' id='2449392262400'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'save_state' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
    
        ok, msg = check_system_clock()
    
        assert ok is True
        assert "Online" in msg
>       mock_save.assert_called() # Should save state
        ^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: Expected 'save_state' to have been called.

tests\desktop_app\services\test_time_service_secure.py:38: AssertionError
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

### ❌ `test_check_system_clock_online_desync`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_online_desync` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 49 |
| Tempo | 0.074s |

**❌ Messaggio di Errore:**

```
assert True is False
```

**📜 Stack Trace:**

```python
self = <test_time_service_secure.TestTimeServiceLogic object at 0x0000023A493904D0>, mock_get_time = <MagicMock name='get_network_time' id='2449389047968'>

    @patch("desktop_app.services.time_service.get_network_time")
    def test_check_system_clock_online_desync(self, mock_get_time):
        # Setup: Online, but 10 mins ahead
        now = datetime.now()
        future = now + timedelta(minutes=10)
        mock_get_time.return_value = future
    
        ok, msg = check_system_clock()
    
>       assert ok is False
E       assert True is False

tests\desktop_app\services\test_time_service_secure.py:49: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

### ❌ `test_check_system_clock_offline_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_offline_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 70 |
| Tempo | 0.197s |

**❌ Messaggio di Errore:**

```
AssertionError: assert 'Offline Mode' in 'OK (Online)'
```

**📜 Stack Trace:**

```python
self = <test_time_service_secure.TestTimeServiceLogic object at 0x0000023A49390830>, mock_save = <MagicMock name='save_state' id='2449389055600'>, mock_load = <MagicMock name='load_state' id='2449388861488'>
mock_get_time = <MagicMock name='get_network_time' id='2449388860912'>

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    @patch("desktop_app.services.time_service.SecureTimeStorage.save_state")
    def test_check_system_clock_offline_success(self, mock_save, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None
    
        # Valid state: Check was yesterday, last exec was yesterday
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        mock_load.return_value = {
            "last_online_check": yesterday,
            "last_execution": yesterday
        }
    
        ok, msg = check_system_clock()
    
        assert ok is True
>       assert "Offline Mode" in msg
E       AssertionError: assert 'Offline Mode' in 'OK (Online)'

tests\desktop_app\services\test_time_service_secure.py:70: AssertionError
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

### ❌ `test_check_system_clock_offline_expired`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_offline_expired` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 96 |
| Tempo | 0.102s |

**❌ Messaggio di Errore:**

```
assert True is False
```

**📜 Stack Trace:**

```python
self = <test_time_service_secure.TestTimeServiceLogic object at 0x0000023A49390B90>, mock_load = <MagicMock name='load_state' id='2449388858320'>
mock_get_time = <MagicMock name='get_network_time' id='2449388853184'>

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_expired(self, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None
    
        # Expired state: Check was 5 days ago (Limit is 3)
        now = datetime.now()
        old_date = now - timedelta(days=OFFLINE_BUFFER_DAYS + 1)
        mock_load.return_value = {
            "last_online_check": old_date,
            "last_execution": old_date
        }
    
        ok, msg = check_system_clock()
    
>       assert ok is False
E       assert True is False

tests\desktop_app\services\test_time_service_secure.py:96: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

### ❌ `test_check_system_clock_offline_rollback`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_offline_rollback` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 116 |
| Tempo | 0.197s |

**❌ Messaggio di Errore:**

```
assert True is False
```

**📜 Stack Trace:**

```python
self = <test_time_service_secure.TestTimeServiceLogic object at 0x0000023A49390EF0>, mock_load = <MagicMock name='load_state' id='2449388809216'>
mock_get_time = <MagicMock name='get_network_time' id='2449388809888'>

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_rollback(self, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None
    
        # Rollback detected: System says today, but last execution was TOMORROW (user moved clock back)
        now = datetime.now()
        future_execution = now + timedelta(hours=2)
    
        mock_load.return_value = {
            "last_online_check": now,
            "last_execution": future_execution
        }
    
        ok, msg = check_system_clock()
    
>       assert ok is False
E       assert True is False

tests\desktop_app\services\test_time_service_secure.py:116: AssertionError
```

**❓ Perché fallisce:**

Errore durante l'esecuzione del test

**Causa probabile:** Verifica il messaggio di errore e lo stack trace per dettagli

**✅ Come risolvere:**

1. Leggi attentamente il messaggio di errore
2. Analizza lo stack trace per trovare la riga problematica
3. Verifica i dati di input del test
4. Controlla se il comportamento del codice è cambiato

**📚 Risorse:**

- https://docs.pytest.org/en/stable/how-to/failures.html

---

## 📄 `tests/desktop_app/services/test_voice_service.py`
**1 test falliti**

### ❌ `test_tts_worker_generation`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_voice_service::test_tts_worker_generation` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 949 |
| Tempo | 0.004s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: Communicate('Hello World', 'it-IT-IrmaNeural')
  Actual: Communicate('Hello World', 'it-IT-IsabellaNeural', rate='+10%', pitch='+2Hz')

pytest introspection follows:

Args:
assert ('Hello World...abellaNeural') == ('Hello World...T-IrmaNeural')
  
  At index 1 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mit-IT-IsabellaNeural#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m != #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mit-IT-IrmaNeural#x1B[39
```

**📜 Stack Trace:**

```python
self = <MagicMock name='Communicate' id='2449388853664'>, args = ('Hello World', 'it-IT-IrmaNeural'), kwargs = {}, expected = call('Hello World', 'it-IT-IrmaNeural')
actual = call('Hello World', 'it-IT-IsabellaNeural', rate='+10%', pitch='+2Hz'), _error_message = <function NonCallableMock.assert_called_with.<locals>._error_message at 0x0000023A49C04CC0>, cause = None

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
            raise AssertionError(error_message)
    
... (troncato) ...
E             At index 1 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mit-IT-IsabellaNeural#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m != #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mit-IT-IrmaNeural#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
E             Use -v to get more diff
E           Kwargs:
E           assert {'pitch': '+2...rate': '+10%'} == {}
E             
E             Left contains 2 more items:
E             #x1B[0m{#x1B[33m'#x1B[39;49;00m#x1B[33mpitch#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m: #x1B[33m'#x1B[39;49;00m#x1B[33m+2Hz#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m, #x1B[33m'#x1B[39;49;00m#x1B[33mrate#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m: #x1B[33m'#x1B[39;49;00m#x1B[33m+10#x1B[39;49;00m#x1B[33m%#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m}#x1B[90m#x1B[39;49;00m
E             Use -v to get more diff

tests\desktop_app\services\test_voice_service.py:43: AssertionError
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

## 📄 `tests/desktop_app/test_api_client_coverage/TestAPIClientCoverage.py`
**1 test falliti**

### ❌ `test_get_headers`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_api_client_coverage.TestAPIClientCoverage::test_get_headers` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 43 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
AssertionError: '0025_384C_41CD_9176' != 'device_123'
- 0025_384C_41CD_9176
+ device_123
```

**📜 Stack Trace:**

```python
self = <test_api_client_coverage.TestAPIClientCoverage testMethod=test_get_headers>

    def test_get_headers(self):
        # We patch where it is DEFINED to ensure consistent behavior
        with patch('desktop_app.utils.get_device_id', return_value="device_123"):
            # No token
            headers = self.client._get_headers()
>           self.assertEqual(headers.get("X-Device-ID"), "device_123")
E           AssertionError: '0025_384C_41CD_9176' != 'device_123'
E           - 0025_384C_41CD_9176
E           + device_123

tests\desktop_app\test_api_client_coverage.py:43: AssertionError
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

## 📄 `tests/desktop_app/test_launcher_robustness/TestLauncherRobustness.py`
**1 test falliti**

### ❌ `test_startup_worker_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_launcher_robustness.TestLauncherRobustness::test_startup_worker_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'start_server' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='start_server' id='2449392322800'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'start_server' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
        worker.progress_update = MagicMock()
        worker.startup_complete = MagicMock()
        worker.error_occurred = MagicMock()
    
        worker.run()
    
>       m_start.assert_called()
E       AssertionError: Expected 'start_server' to have been called.

tests\desktop_app\test_launcher_robustness.py:220: AssertionError
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

## 📄 `tests/desktop_app/test_toast.py`
**3 test falliti**

### ❌ `test_toast_history_persistence`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_toast::test_toast_history_persistence` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: assert 0 == 1
 +  where 0 = len(<MagicMock name='mock.ToastManager.instance().history' id='2449396014816'>)
 +    where <MagicMock name='mock.ToastManager.instance().history' id='2449396014816'> = <MagicMock name='mock.ToastManager.instance()' id='2449395929488'>.history
```

**📜 Stack Trace:**

```python
def test_toast_history_persistence():
        from desktop_app.components.toast import ToastManager
        ToastManager._instance = None
    
        # Mock load_history
        with patch("builtins.open", mock_open(read_data='[{"title": "Old", "message": "Msg", "type": "info", "timestamp": "2023-01-01T12:00:00"}]')) as m_open:
            with patch("os.path.exists", return_value=True):
                manager = ToastManager.instance()
>               assert len(manager.history) == 1
E               AssertionError: assert 0 == 1
E                +  where 0 = len(<MagicMock name='mock.ToastManager.instance().history' id='2449396014816'>)
E                +    where <MagicMock name='mock.ToastManager.instance().history' id='2449396014816'> = <MagicMock name='mock.ToastManager.instance()' id='2449395929488'>.history

tests\desktop_app\test_toast.py:20: AssertionError
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

### ❌ `test_toast_thread_safety`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_toast::test_toast_thread_safety` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: emit(None, 'info', 'T', 'M', 3000)
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.ToastManager.instance().request_show_toast.emit' id='2449396181152'>, args = (None, 'info', 'T', 'M', 3000), kwargs = {}, expected = "emit(None, 'info', 'T', 'M', 3000)"
actual = 'not called.', error_message = "expected call not found.\nExpected: emit(None, 'info', 'T', 'M', 3000)\n  Actual: not called."

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
    
                manager.show_toast(None, "info", "T", "M")
    
                # Should have emitted signal
>               manager.request_show_toast.emit.assert_called_with(None, "info", "T", "M", 3000)
E               AssertionError: expected call not found.
E               Expected: emit(None, 'info', 'T', 'M', 3000)
E                 Actual: not called.

tests\desktop_app\test_toast.py:67: AssertionError
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

### ❌ `test_stacking_logic_call`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_toast::test_stacking_logic_call` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 93 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: assert 0 == 1
 +  where 0 = len(<MagicMock name='mock.ToastManager.instance().active_toasts' id='2449396212240'>)
 +    where <MagicMock name='mock.ToastManager.instance().active_toasts' id='2449396212240'> = <MagicMock name='mock.ToastManager.instance()' id='2449395929488'>.active_toasts
```

**📜 Stack Trace:**

```python
def test_stacking_logic_call():
        from desktop_app.components.toast import ToastManager
        ToastManager._instance = None
        manager = ToastManager.instance()
    
        with patch("desktop_app.components.toast.ToastNotification") as MockToast:
            # Mock Toast
            t1 = MockToast.return_value
            t1.width.return_value = 100
            t1.height.return_value = 50
    
            with patch("desktop_app.components.toast.QApplication") as MockApp:
                 # Fix geometry
                 screen = MagicMock()
                 rect = MagicMock()
                 rect.x.return_value = 0
                 rect.y.return_value = 0
                 rect.width.return_value = 1920
                 rect.height.return_value = 1080
                 screen.availableGeometry.return_value = rect
                 MockApp.primaryScreen.return_value = screen
                 MockApp.screenAt.return_value = screen
    
                 manager.show_toast(None, "info", "T1", "M1")
>                assert len(manager.active_toasts) == 1
E                AssertionError: assert 0 == 1
E                 +  where 0 = len(<MagicMock name='mock.ToastManager.instance().active_toasts' id='2449396212240'>)
E                 +    where <MagicMock name='mock.ToastManager.instance().active_toasts' id='2449396212240'> = <MagicMock name='mock.ToastManager.instance()' id='2449395929488'>.active_toasts

tests\desktop_app\test_toast.py:93: AssertionError
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

## 📄 `tests/desktop_app/views/test_config_view_interactions/TestConfigViewInteractions.py`
**5 test falliti**

### ❌ `test_audit_log_export`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_audit_log_export` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.005s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: open('/tmp/audit.csv', 'wb')
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='open' id='2449370293328'>, args = ('/tmp/audit.csv', 'wb'), kwargs = {}, expected = "open('/tmp/audit.csv', 'wb')", actual = 'not called.'
error_message = "expected call not found.\nExpected: open('/tmp/audit.csv', 'wb')\n  Actual: not called."

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
                self.assertTrue(m_get.called)
                self.assertIn("/audit/export", m_get.call_args[0][0])
    
                # Verify file write
>               m_open.assert_called_with("/tmp/audit.csv", "wb")
E               AssertionError: expected call not found.
E               Expected: open('/tmp/audit.csv', 'wb')
E                 Actual: not called.

tests\desktop_app\views\test_config_view_interactions.py:203: AssertionError
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

### ❌ `test_audit_log_filters`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_audit_log_filters` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 169 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AttributeError: 'method' object has no attribute 'return_value'
```

**📜 Stack Trace:**

```python
self = <test_config_view_interactions.TestConfigViewInteractions testMethod=test_audit_log_filters>

    def test_audit_log_filters(self):
        """Test that changing filters triggers refresh."""
        widget = self.view.audit_widget
    
        # Mock date/combo accessors
>       widget.user_filter.currentData.return_value = 5
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'method' object has no attribute 'return_value'

tests\desktop_app\views\test_config_view_interactions.py:169: AttributeError
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

### ❌ `test_general_settings_validation`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_general_settings_validation` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 211 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AttributeError: 'method' object has no attribute 'return_value'
```

**📜 Stack Trace:**

```python
self = <test_config_view_interactions.TestConfigViewInteractions testMethod=test_general_settings_validation>

    def test_general_settings_validation(self):
        """Test validation of threshold inputs."""
        self.view.current_settings = {}
    
        # Invalid Threshold "0" (isdigit=True, <=0 is True)
>       self.view.general_settings.alert_threshold_input.text.return_value = "0"
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'method' object has no attribute 'return_value'

tests\desktop_app\views\test_config_view_interactions.py:211: AttributeError
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

### ❌ `test_user_management_delete_other`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_user_management_delete_other` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: delete_user(2)
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.delete_user' id='2449396571152'>, args = (2,), kwargs = {}, expected = 'delete_user(2)', actual = 'not called.'
error_message = 'expected call not found.\nExpected: delete_user(2)\n  Actual: not called.'

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
        self.mock_dialog.show_question.return_value = True
    
        widget.delete_user()
    
>       self.api_client.delete_user.assert_called_with(2)
E       AssertionError: expected call not found.
E       Expected: delete_user(2)
E         Actual: not called.

tests\desktop_app\views\test_config_view_interactions.py:162: AssertionError
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

### ❌ `test_user_management_delete_self`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_user_management_delete_self` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: show_warning(<ANY>, 'Azione Non Consentita', <ANY>)
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.CustomMessageDialog.show_warning' id='2449389318704'>, args = (<ANY>, 'Azione Non Consentita', <ANY>), kwargs = {}, expected = "show_warning(<ANY>, 'Azione Non Consentita', <ANY>)"
actual = 'not called.', error_message = "expected call not found.\nExpected: show_warning(<ANY>, 'Azione Non Consentita', <ANY>)\n  Actual: not called."

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
        widget.get_selected_user_id = MagicMock(return_value=1) # Same as api_client.user_info id
    
        widget.delete_user()
    
>       self.mock_dialog.show_warning.assert_called_with(ANY, "Azione Non Consentita", ANY)
E       AssertionError: expected call not found.
E       Expected: show_warning(<ANY>, 'Azione Non Consentita', <ANY>)
E         Actual: not called.

tests\desktop_app\views\test_config_view_interactions.py:150: AssertionError
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

## 📄 `tests/desktop_app/views/test_import_view_advanced/TestImportViewAdvanced.py`
**2 test falliti**

### ❌ `test_process_dropped_files_start`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_import_view_advanced.TestImportViewAdvanced::test_process_dropped_files_start` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 198 |
| Tempo | 4.059s |

**❌ Messaggio di Errore:**

```
AttributeError: 'DummyQWidget' object has no attribute 'setTextColor'
```

**📜 Stack Trace:**

```python
self = <urllib3.connection.HTTPConnection object at 0x0000023A4B930650>

    def _new_conn(self) -> socket.socket:
        """Establish a socket connection and set nodelay settings on it.
    
        :return: New socket connection.
        """
        try:
>           sock = connection.create_connection(
                (self._dns_host, self.port),
                self.timeout,
                source_address=self.source_address,
                socket_options=self.socket_options,
            )

... (troncato) ...
        # Get Output Path
        try:
            paths = self.api_client.get_paths()
            output_folder = paths.get("database_path")
        except Exception as e:
>           self.results_display.setTextColor(QColor("#DC2626"))
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DummyQWidget' object has no attribute 'setTextColor'

desktop_app\views\import_view.py:504: AttributeError
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

### ❌ `test_stop_processing`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_import_view_advanced.TestImportViewAdvanced::test_stop_processing` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 201 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AttributeError: 'function' object has no attribute 'assert_called_with'
```

**📜 Stack Trace:**

```python
self = <test_import_view_advanced.TestImportViewAdvanced testMethod=test_stop_processing>

    def test_stop_processing(self):
        """Test stop button functionality."""
        self.view.worker = MagicMock()
        self.view.thread = MagicMock()
        self.view.thread.isRunning.return_value = True
    
        self.view.stop_processing()
    
        self.view.worker.stop.assert_called()
>       self.view.stop_button.setEnabled.assert_called_with(False)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'function' object has no attribute 'assert_called_with'

tests\desktop_app\views\test_import_view_advanced.py:201: AttributeError
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

## 📄 `tests/desktop_app/views/test_login_view_coverage/TestLoginViewCoverage.py`
**6 test falliti**

### ❌ `test_force_password_change`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_force_password_change` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.143s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: change_password('primoaccesso', 'new')
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.change_password' id='2449399218928'>, args = ('primoaccesso', 'new'), kwargs = {}, expected = "change_password('primoaccesso', 'new')", actual = 'not called.'
error_message = "expected call not found.\nExpected: change_password('primoaccesso', 'new')\n  Actual: not called."

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
            # Mock CustomMessageDialog to catch "Success" info
            with patch('desktop_app.views.login_view.CustomMessageDialog'):
                view.on_login_success(response)
    
>           self.mock_api_client.change_password.assert_called_with("primoaccesso", "new")
E           AssertionError: expected call not found.
E           Expected: change_password('primoaccesso', 'new')
E             Actual: not called.

tests\desktop_app\views\test_login_view_coverage.py:130: AssertionError
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

### ❌ `test_init_check_license`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_init_check_license` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 73 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: <MagicMock name='mock.LoginView().username_input.isEnabled()' id='2449397311168'> is not false
```

**📜 Stack Trace:**

```python
self = <test_login_view_coverage.TestLoginViewCoverage testMethod=test_init_check_license>

    def test_init_check_license(self):
        # We need to mock _auto_update_if_needed because it might trigger things
        with patch.object(LoginView, '_auto_update_if_needed'):
            view = LoginView(self.mock_api_client, license_ok=True)
            self.assertTrue(view.username_input.isEnabled())
    
            view_bad = LoginView(self.mock_api_client, license_ok=False)
>           self.assertFalse(view_bad.username_input.isEnabled())
E           AssertionError: <MagicMock name='mock.LoginView().username_input.isEnabled()' id='2449397311168'> is not false

tests\desktop_app\views\test_login_view_coverage.py:73: AssertionError
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

### ❌ `test_license_update_trigger`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_license_update_trigger` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'LicenseUpdateWorker' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='LicenseUpdateWorker' id='2449389206704'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'LicenseUpdateWorker' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

self = <test_login_view_coverage.TestLoginViewCoverage testMethod=test_license_update_trigger>

    def test_license_update_trigger(self):
        view = LoginView(self.mock_api_client)
    
        with patch('desktop_app.views.login_view.LicenseUpdateWorker') as MockWorker:
            view.handle_update_license()
>           MockWorker.assert_called()
E           AssertionError: Expected 'LicenseUpdateWorker' to have been called.

tests\desktop_app\views\test_login_view_coverage.py:109: AssertionError
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

### ❌ `test_login_empty_credentials`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_login_empty_credentials` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.003s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'show_warning' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='CustomMessageDialog.show_warning' id='2449393269648'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'show_warning' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

self = <test_login_view_coverage.TestLoginViewCoverage testMethod=test_login_empty_credentials>

    def test_login_empty_credentials(self):
        view = LoginView(self.mock_api_client)
        view.username_input.setText("")
        view.password_input.setText("")
    
        # Ensure shake_window doesn't cause issues
        with patch.object(view, 'shake_window'):
            with patch('desktop_app.views.login_view.CustomMessageDialog') as mock_dialog:
                view.handle_login()
>               mock_dialog.show_warning.assert_called()
E               AssertionError: Expected 'show_warning' to have been called.

tests\desktop_app\views\test_login_view_coverage.py:84: AssertionError
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

### ❌ `test_login_success_flow`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_login_success_flow` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: set_token({'access_token': 'tok', 'user_id': 1})
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.set_token' id='2449396626160'>, args = ({'access_token': 'tok', 'user_id': 1},), kwargs = {}, expected = "set_token({'access_token': 'tok', 'user_id': 1})", actual = 'not called.'
error_message = "expected call not found.\nExpected: set_token({'access_token': 'tok', 'user_id': 1})\n  Actual: not called."

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
>           raise AssertionError(error_message)
E           AssertionError: expected call not found.
... (troncato) ...
            # Simulate success signal
            response = {"access_token": "tok", "user_id": 1}
            view.on_login_success(response)
    
>           self.mock_api_client.set_token.assert_called_with(response)
E           AssertionError: expected call not found.
E           Expected: set_token({'access_token': 'tok', 'user_id': 1})
E             Actual: not called.

tests\desktop_app\views\test_login_view_coverage.py:102: AssertionError
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

### ❌ `test_update_checker_integration`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_update_checker_integration` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'UpdateWorker' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='UpdateWorker' id='2449393749120'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'UpdateWorker' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

self = <test_login_view_coverage.TestLoginViewCoverage testMethod=test_update_checker_integration>

    def test_update_checker_integration(self):
        view = LoginView(self.mock_api_client)
    
        with patch('desktop_app.views.login_view.UpdateWorker') as MockWorker:
            worker = MockWorker.return_value
            worker.update_available = MagicMock()
    
            view.check_updates()
>           MockWorker.assert_called()
E           AssertionError: Expected 'UpdateWorker' to have been called.

tests\desktop_app\views\test_login_view_coverage.py:140: AssertionError
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

## 📄 `tests/test_launcher_coverage/TestLauncherCoverage.py`
**1 test falliti**

### ❌ `test_startup_worker_failure`

| Campo | Valore |
|-------|--------|
| Test | `tests.test_launcher_coverage.TestLauncherCoverage::test_startup_worker_failure` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 113 |
| Tempo | 0.229s |

**❌ Messaggio di Errore:**

```
AssertionError: 'Timeout' not found in ''
```

**📜 Stack Trace:**

```python
self = <test_launcher_coverage.TestLauncherCoverage testMethod=test_startup_worker_failure>

    def test_startup_worker_failure(self):
        worker = launcher.StartupWorker(8000)
        err_slot = MagicMock()
        worker.error_occurred.connect(err_slot)
    
        with patch('launcher.start_server'), \
             patch('launcher.check_port', return_value=False), \
             patch('threading.Thread'):
    
            # Use side_effect to control loop execution
            # Loop condition: time.time() - t0 < 20
            # We want loop to run at least once (to check port), then timeout
            # Calls: 1. t0 init 2. Loop check (start) 3. Elapsed calc 4. Loop check (end/timeout)
            with patch('time.time', side_effect=[0, 1, 2, 25]):
                 with patch('time.sleep'): # Instant sleep
                     worker.run()
    
            err_slot.assert_called()
            # Verify the error message contains "Timeout"
            if err_slot.call_args:
                args = err_slot.call_args[0]
>               self.assertIn("Timeout", args[0])
E               AssertionError: 'Timeout' not found in ''

tests\test_launcher_coverage.py:113: AssertionError
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
