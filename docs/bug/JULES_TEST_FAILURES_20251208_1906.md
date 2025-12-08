# 🧪 Test Failures - Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-08 19:06
**File sorgente:** junit.xml

## 📊 Statistiche Test

| Metrica | Valore |
|---------|--------|
| Test totali | 580 |
| ✅ Passati | 579 |
| ❌ Falliti | 1 |
| 💥 Errori | 0 |
| ⏭️ Skippati | 0 |
| ⏱️ Tempo | 111.89s |
| Success Rate | 99.8% |

## 🏷️ Tipi di Errore

| Tipo | Count | Descrizione |
|------|-------|-------------|
| ❌ AssertionError | 1 | Il test ha verificato una condizione che... |

## 📝 Istruzioni per Jules

Per ogni test fallito troverai:
- 📍 **Posizione**: File e nome del test
- ❌ **Errore**: Messaggio e tipo di errore
- 📜 **Stack Trace**: Traceback completo
- ❓ **Perché fallisce**: Spiegazione del tipo di errore
- ✅ **Come risolvere**: Suggerimenti specifici
- 📚 **Risorse**: Link utili

---

## 📄 `tests/app/test_password_change.py`
**1 test falliti**

### ❌ `test_change_own_password`

| Campo | Valore |
|-------|--------|
| Test | `tests.app.test_password_change::test_change_own_password` |
| Tipo Errore | ❌ AssertionError |
| Status | FAILURE |
| Riga | 43 |
| Tempo | 0.959s |

**❌ Messaggio di Errore:**

```
AssertionError: assert 'Password agg... con successo' == 'Password agg...con successo.'
  
  #x1B[0m#x1B[91m- Password aggiornata con successo.#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
  ?                                 -#x1B[90m#x1B[39;49;00m
  #x1B[92m+ Password aggiornata con successo#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
```

**📜 Stack Trace:**

```python
test_client = <starlette.testclient.TestClient object at 0x0000022033FBA660>, db_session = <sqlalchemy.orm.session.Session object at 0x0000022034183110>, enable_real_auth = None

    def test_change_own_password(test_client: TestClient, db_session: Session, enable_real_auth):
        # 1. Setup User
        username = "pwchangeuser"
        old_password = "oldpassword"
        new_password = "newpassword"
        hashed = security.get_password_hash(old_password)
        user = User(username=username, hashed_password=hashed, is_admin=False)
        db_session.add(user)
        db_session.commit()
    
        # 2. Login
        login_data = {"username": username, "password": old_password}
        response = test_client.post("/auth/login", data=login_data)
... (troncato) ...
        response = test_client.post("/auth/change-password", json=payload, headers=headers)
        assert response.status_code == 200
>       assert response.json()["message"] == "Password aggiornata con successo."
E       AssertionError: assert 'Password agg... con successo' == 'Password agg...con successo.'
E         
E         #x1B[0m#x1B[91m- Password aggiornata con successo.#x1B[39;49;00m#x1B[90m#x1B[39;49;00m
E         ?                                 -#x1B[90m#x1B[39;49;00m
E         #x1B[92m+ Password aggiornata con successo#x1B[39;49;00m#x1B[90m#x1B[39;49;00m

tests\app\test_password_change.py:43: AssertionError
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
