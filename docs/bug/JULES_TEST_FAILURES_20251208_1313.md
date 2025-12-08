# 🧪 Test Failures - Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-08 13:13
**File sorgente:** junit.xml

## 📊 Statistiche Test

| Metrica | Valore |
|---------|--------|
| Test totali | 583 |
| ✅ Passati | 541 |
| ❌ Falliti | 26 |
| 💥 Errori | 0 |
| ⏭️ Skippati | 16 |
| ⏱️ Tempo | 103.84s |
| Success Rate | 92.8% |

## 🏷️ Tipi di Errore

| Tipo | Count | Descrizione |
|------|-------|-------------|
| ❌ AssertionError | 17 | Il test ha verificato una condizione che... |
| 🔍 AttributeError | 3 | Tentativo di accedere a un attributo ine... |
| ❓ NameError | 2 | Errore durante l'esecuzione del test... |
| ❓  | 2 | Errore durante l'esecuzione del test... |
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

## 📄 `tests/app/api/routers/test_users_full.py`
**1 test falliti**

### ❌ `test_create_user_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.routers.test_users_full::test_create_user_success` |
| Tipo Errore | ❓ NameError |
| Status | FAILURE |
| Riga | 30 |
| Tempo | 0.013s |

**❌ Messaggio di Errore:**

```
NameError: name 'os' is not defined. Did you forget to import 'os'
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA33D3D0>, admin_token_headers = {'Authorization': 'Bearer admin-token'}, admin_user = <app.db.models.User object at 0x000002B9CA3CA930>

    def test_create_user_success(test_client, admin_token_headers, admin_user):
        payload = {
            "username": "newuser",
            "account_name": "New User",
            "is_admin": False,
            "password": "initialpassword"
        }
    
>       response = test_client.post("/users/", json=payload, headers=admin_token_headers)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\app\api\routers\test_users_full.py:30: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
... (troncato) ...
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
        # Force default password to "primoaccesso"
>       default_password = os.getenv("DEFAULT_USER_PASSWORD", "primoaccesso") # NOSONAR
                           ^^
E       NameError: name 'os' is not defined. Did you forget to import 'os'

app\api\routers\users.py:45: NameError
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

## 📄 `tests/app/api/test_csv_orphan_sync.py`
**1 test falliti**

### ❌ `test_csv_import_moves_orphan_file`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.api.test_csv_orphan_sync::test_csv_import_moves_orphan_file` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 58 |
| Tempo | 0.021s |

**❌ Messaggio di Errore:**

```
AssertionError: Old orphan file should be moved
assert not True
 +  where True = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Bianchi Mario (N-A)\\ANTINCENDIO\\ATTIVO\\Bianchi Mario (N-A) - ANTINCENDIO - 01_01_2030.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA0141A0>, db_session = <sqlalchemy.orm.session.Session object at 0x000002B9CA0145F0>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-46/data0')

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
E        +  where True = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Bianchi Mario (N-A)\\ANTINCENDIO\\ATTIVO\\Bianchi Mario (N-A) - ANTINCENDIO - 01_01_2030.pdf')
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
| Tempo | 0.014s |

**❌ Messaggio di Errore:**

```
Failed: File was not removed from original location.
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA014710>, db_session = <sqlalchemy.orm.session.Session object at 0x000002B9CA016EA0>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-46/data0')

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
 +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2030.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA06B2F0>, db_session = <sqlalchemy.orm.session.Session object at 0x000002B9CA06B620>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-46/data0')

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
E        +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\ATTIVO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2030.pdf')
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
 +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\STORICO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf')
 +    where <built-in function _path_exists> = <module 'ntpath' (frozen)>.exists
 +      where <module 'ntpath' (frozen)> = os.path
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA412D50>, db_session = <sqlalchemy.orm.session.Session object at 0x000002B9CA413680>
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-46/data0')

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
E        +  where False = <built-in function _path_exists>('C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\data0\\DOCUMENTI DIPENDENTI\\Rossi Mario (123)\\ANTINCENDIO\\STORICO\\Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf')
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
test_dirs = WindowsPath('C:/Users/gianc/AppData/Local/Temp/pytest-of-gianc/pytest-46/data0')

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
mock_path = 'C:\\Users\\gianc\\AppData\\Local\\Temp\\pytest-of-gianc\\pytest-46\\test_acquire_generic_exception0\\.lock'

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
| Tempo | 0.001s |

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
**2 test falliti**

### ❌ `test_lifespan_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_main_full::test_lifespan_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 928 |
| Tempo | 0.010s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'start' to have been called once. Called 0 times.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='scheduler.start' id='2996991503312'>

    def assert_called_once(self):
        """assert that the mock was called only once.
        """
        if not self.call_count == 1:
            msg = ("Expected '%s' to have been called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
>           raise AssertionError(msg)
E           AssertionError: Expected 'start' to have been called once. Called 0 times.

C:\Program Files\Python312\Lib\unittest\mock.py:928: AssertionError

... (troncato) ...
            # db_security.load_memory_db() is called.
            # If it wasn't called, maybe the try/except block swallowed it?
            # Or maybe test environment patches it differently.
            # We will assume it should be called and debug if needed.
            # Re-verify the patching target.
            # For now, let's relax to asserting start called.
>           mock_sched.start.assert_called_once()
E           AssertionError: Expected 'start' to have been called once. Called 0 times.

tests\app\test_main_full.py:52: AssertionError
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
| Riga | 70 |
| Tempo | 0.207s |

**❌ Messaggio di Errore:**

```
AssertionError: assert None == 'Fatal Lock'
 +  where None = getattr(<starlette.datastructures.State object at 0x000002B9C968F260>, 'startup_error', None)
 +    where <starlette.datastructures.State object at 0x000002B9C968F260> = app.state
```

**📜 Stack Trace:**

```python
@pytest.mark.anyio
    async def test_lifespan_db_load_failure_fatal():
        with patch("app.main.db_security") as mock_sec:
            mock_sec.load_memory_db.side_effect = PermissionError("Fatal Lock")
    
            async with lifespan(app):
                pass
    
            # Use getattr default to avoid AttributeErrors if state was cleared
>           assert getattr(app.state, "startup_error", None) == "Fatal Lock"
E           AssertionError: assert None == 'Fatal Lock'
E            +  where None = getattr(<starlette.datastructures.State object at 0x000002B9C968F260>, 'startup_error', None)
E            +    where <starlette.datastructures.State object at 0x000002B9C968F260> = app.state

tests\app\test_main_full.py:70: AssertionError
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

## 📄 `tests/app/test_security_features.py`
**1 test falliti**

### ❌ `test_audit_logging_on_user_create`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_security_features::test_audit_logging_on_user_create` |
| Tipo Errore | ❓ NameError |
| Status | FAILURE |
| Riga | 73 |
| Tempo | 0.399s |

**❌ Messaggio di Errore:**

```
NameError: name 'os' is not defined. Did you forget to import 'os'
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x000002B9CA9399D0>, db_session = <sqlalchemy.orm.session.Session object at 0x000002B9CA606300>, enable_real_auth = None

    def test_audit_logging_on_user_create(test_client: TestClient, db_session: Session, enable_real_auth):
        # 1. Setup Admin
        username = "auditadmin"
        password = "auditpassword"
        hashed = security.get_password_hash(password)
        user = User(username=username, hashed_password=hashed, is_admin=True)
        db_session.add(user)
        db_session.commit()
    
        login_data = {"username": username, "password": password}
        response_login = test_client.post("/auth/login", data=login_data)
        assert response_login.status_code == 200
        token = response_login.json()["access_token"]
... (troncato) ...
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
        # Force default password to "primoaccesso"
>       default_password = os.getenv("DEFAULT_USER_PASSWORD", "primoaccesso") # NOSONAR
                           ^^
E       NameError: name 'os' is not defined. Did you forget to import 'os'

app\api\routers\users.py:45: NameError
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

## 📄 `tests/desktop_app/services/test_security_service/TestSecurityService.py`
**1 test falliti**

### ❌ `test_is_virtual_environment_detects_file`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_security_service.TestSecurityService::test_is_virtual_environment_detects_file` |
| Tipo Errore | ❓  |
| Status | FAILURE |
| Riga | 54 |
| Tempo | 0.001s |

**❌ Messaggio di Errore:**

```
assert False is True
```

**📜 Stack Trace:**

```python
self = <test_security_service.TestSecurityService object at 0x000002B9C9C327E0>, mock_exists = <MagicMock name='exists' id='2996988310880'>
mock_processes = <MagicMock name='_get_running_processes_wmi' id='2996988233296'>

    @patch('desktop_app.services.security_service.os.name', 'nt')
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    @patch('desktop_app.services.security_service.os.path.exists')
    def test_is_virtual_environment_detects_file(self, mock_exists, mock_processes):
        # Processes clean
        mock_processes.return_value = ["explorer.exe"]
    
        # Simulate VM driver file exists
        # Note: security_service might use os.path.exists directly which we patched
        def side_effect(path):
            # Normalize path for comparison to handle Windows path differences if needed
            return "vboxguest.sys" in str(path).lower()
        mock_exists.side_effect = side_effect
    
        is_vm, msg = is_virtual_environment()
    
        # Similar safe-guard
        if not is_vm and mock_exists.called:
             # Debugging fallback
             pass
        else:
>            assert is_vm is True
E            assert False is True

tests\desktop_app\services\test_security_service.py:54: AssertionError
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
| Tempo | 0.024s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: open('\\tmp\\secure_time.dat', 'wb')
  Actual: open('C:\\Users\\gianc\\AppData\\Local\\Intelleo\\Licenza\\secure_time.dat', 'wb')

pytest introspection follows:

Args:
assert ('C:\\Users\\...me.dat', 'wb') == ('\\tmp\\secu...me.dat', 'wb')
  
  At index 0 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mC:#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mUsers#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mgianc#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33
```

**📜 Stack Trace:**

```python
self = <MagicMock name='open' id='2996992272688'>, args = ('\\tmp\\secure_time.dat', 'wb'), kwargs = {}, expected = call('\\tmp\\secure_time.dat', 'wb')
actual = call('C:\\Users\\gianc\\AppData\\Local\\Intelleo\\Licenza\\secure_time.dat', 'wb'), _error_message = <function NonCallableMock.assert_called_with.<locals>._error_message at 0x000002B9CADC7880>
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
E       assert ('C:\\Users\\...me.dat', 'wb') == ('\\tmp\\secu...me.dat', 'wb')
E         
E         At index 0 diff: #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33mC:#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mUsers#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mgianc#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mAppData#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mLocal#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mIntelleo#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mLicenza#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33msecure_time.dat#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m != #x1B[0m#x1B[33m'#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33mtmp#x1B[39;49;00m#x1B[33m\\#x1B[39;49;00m#x1B[33msecure_time.dat#x1B[39;49;00m#x1B[33m'#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
E         Use -v to get more diff

tests\desktop_app\services\test_time_service_secure.py:24: AssertionError
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
**1 test falliti**

### ❌ `test_check_system_clock_offline_success`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.services.test_time_service_secure.TestTimeServiceLogic::test_check_system_clock_offline_success` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 91 |
| Tempo | 0.334s |

**❌ Messaggio di Errore:**

```
AssertionError: assert ('Offline Mode' in 'OK (Online)' or 'Offline' in 'OK (Online)')
```

**📜 Stack Trace:**

```python
self = <test_time_service_secure.TestTimeServiceLogic object at 0x000002B9C9CC0FE0>, mock_save = <MagicMock name='save_state' id='2996992266736'>, mock_load = <MagicMock name='load_state' id='2996992270096'>
mock_get_time = <MagicMock name='get_network_time' id='2996992272496'>

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
    
        # Verify message content (flexible case)
>       assert "Offline Mode" in msg or "Offline" in msg
E       AssertionError: assert ('Offline Mode' in 'OK (Online)' or 'Offline' in 'OK (Online)')

tests\desktop_app\services\test_time_service_secure.py:91: AssertionError
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
| Riga | 48 |
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
        # But wait, desktop_app.api_client imports get_device_id from .utils
        # If APIClient is already imported, we need to patch desktop_app.api_client.get_device_id
        # OR patch where it's used.
        # The failure showed "0025..." (real) vs "device_123" (mock).
        # This implies it was using the real implementation.
        with patch('desktop_app.api_client.get_device_id', return_value="device_123"):
            # No token
            headers = self.client._get_headers()
>           self.assertEqual(headers.get("X-Device-ID"), "device_123")
E           AssertionError: '0025_384C_41CD_9176' != 'device_123'
E           - 0025_384C_41CD_9176
E           + device_123

tests\desktop_app\test_api_client_coverage.py:48: AssertionError
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
| Riga | 940 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: emit(True, 'OK')
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.emit' id='2996997516240'>, args = (True, 'OK'), kwargs = {}, expected = "emit(True, 'OK')", actual = 'not called.'
error_message = "expected call not found.\nExpected: emit(True, 'OK')\n  Actual: not called."

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
             pass
        else:
             m_start.assert_called()
    
>       worker.startup_complete.emit.assert_called_with(True, "OK")
E       AssertionError: expected call not found.
E       Expected: emit(True, 'OK')
E         Actual: not called.

tests\desktop_app\test_launcher_robustness.py:228: AssertionError
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
**1 test falliti**

### ❌ `test_toast_history_persistence`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.test_toast::test_toast_history_persistence` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 918 |
| Tempo | 0.004s |

**❌ Messaggio di Errore:**

```
AssertionError: Expected 'open' to have been called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='open' id='2996988690256'>

    def assert_called(self):
        """assert that the mock was called at least once
        """
        if self.call_count == 0:
            msg = ("Expected '%s' to have been called." %
                   (self._mock_name or 'mock'))
>           raise AssertionError(msg)
E           AssertionError: Expected 'open' to have been called.

C:\Program Files\Python312\Lib\unittest\mock.py:918: AssertionError

During handling of the above exception, another exception occurred:

... (troncato) ...
                    MockApp.primaryScreen.return_value = screen
                    MockApp.screenAt.return_value = screen
    
                    manager.show_toast(None, "success", "New", "Msg")
    
                    # Should save
>                   m_open.assert_called()
E                   AssertionError: Expected 'open' to have been called.

tests\desktop_app\test_toast.py:61: AssertionError
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
**2 test falliti**

### ❌ `test_audit_log_filters`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_config_view_interactions.TestConfigViewInteractions::test_audit_log_filters` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 196 |
| Tempo | 0.002s |

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
        # Attribute error fix: currentData is a method on QComboBox.
        # widget.user_filter is a QComboBox (MockWidget).
        # We need to ensure calling currentData() returns 5.
        # MockWidget is a MagicMock, so calling it returns a MagicMock.
        # We need to set return_value on the CALL.
    
        # If the code calls `widget.user_filter.currentData()`, then:
>       widget.user_filter.currentData.return_value = 5
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'method' object has no attribute 'return_value'

tests\desktop_app\views\test_config_view_interactions.py:196: AttributeError
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
| Riga | 241 |
| Tempo | 0.002s |

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
        # Attribute error fix: alert_threshold_input is QLineEdit.
        # .text is a method.
>       self.view.general_settings.alert_threshold_input.text.return_value = "0"
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'method' object has no attribute 'return_value'

tests\desktop_app\views\test_config_view_interactions.py:241: AttributeError
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

## 📄 `tests/desktop_app/views/test_import_view_advanced/TestImportViewAdvanced.py`
**1 test falliti**

### ❌ `test_process_dropped_files_start`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_import_view_advanced.TestImportViewAdvanced::test_process_dropped_files_start` |
| Tipo Errore | 🔍 AttributeError |
| Status | FAILURE |
| Riga | 198 |
| Tempo | 4.052s |

**❌ Messaggio di Errore:**

```
AttributeError: 'DummyQWidget' object has no attribute 'append'
```

**📜 Stack Trace:**

```python
self = <urllib3.connection.HTTPConnection object at 0x000002B9CC7B3EF0>

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
        try:
            paths = self.api_client.get_paths()
            output_folder = paths.get("database_path")
        except Exception as e:
            self.results_display.setTextColor(QColor("#DC2626"))
>           self.results_display.append(f"Errore critico: Impossibile recuperare il percorso del database. {e}")
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DummyQWidget' object has no attribute 'append'

desktop_app\views\import_view.py:521: AttributeError
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
**2 test falliti**

### ❌ `test_init_check_license`

| Campo | Valore |
|-------|--------|
| Test | `tests.desktop_app.views.test_login_view_coverage.TestLoginViewCoverage::test_init_check_license` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 940 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: expected call not found.
Expected: setEnabled(False)
  Actual: not called.
```

**📜 Stack Trace:**

```python
self = <MagicMock name='mock.LoginView().username_input.setEnabled' id='2997026318208'>, args = (False,), kwargs = {}, expected = 'setEnabled(False)', actual = 'not called.'
error_message = 'expected call not found.\nExpected: setEnabled(False)\n  Actual: not called.'

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
            # Let's check call args.
    
            # Check if setEnabled(False) was called on username_input
            # view_bad.username_input is a MockWidget (MagicMock)
>           view_bad.username_input.setEnabled.assert_called_with(False)
E           AssertionError: expected call not found.
E           Expected: setEnabled(False)
E             Actual: not called.

tests\desktop_app\views\test_login_view_coverage.py:85: AssertionError
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
| Riga | 176 |
| Tempo | 0.002s |

**❌ Messaggio di Errore:**

```
AssertionError: 'Aggiornamento disponibile' not found in <MagicMock name='mock.LoginView().version_label.text()' id='2997026446256'>
```

**📜 Stack Trace:**

```python
self = <test_login_view_coverage.TestLoginViewCoverage testMethod=test_update_checker_integration>

    def test_update_checker_integration(self):
        view = LoginView(self.mock_api_client)
    
        with patch('desktop_app.views.login_view.UpdateWorker') as MockWorker:
            worker = MockWorker.return_value
            worker.update_available = MagicMock()
    
            view.check_updates()
    
            if MockWorker.call_count == 0:
                pass
            else:
                MockWorker.assert_called()
    
            # Simulate update found
            # Patch show_update_dialog to avoid exec
            with patch.object(view, 'show_update_dialog'):
                view.on_update_available("2.0", "http://url")
>               self.assertIn("Aggiornamento disponibile", view.version_label.text())
E               AssertionError: 'Aggiornamento disponibile' not found in <MagicMock name='mock.LoginView().version_label.text()' id='2997026446256'>

tests\desktop_app\views\test_login_view_coverage.py:176: AssertionError
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
