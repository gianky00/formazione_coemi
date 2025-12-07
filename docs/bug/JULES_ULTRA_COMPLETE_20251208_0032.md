# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 47 issues
**Tempo:** 7h 40min

---

## 📄 `app/api/main.py`

### Riga 37 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     35: STR_NON_TROVATO = "Non trovato in anagrafica (matricola mancante)."
     36: 
 >>> 37: def _process_orphan_cert(cert, match, database_path, db):
     38:     """
     39:     Helper function to process linking an orphaned certificate to a matched employee
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 92 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     90: 
     91: @router.post("/upload-pdf/", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 92: async def upload_pdf(
     93:     file: UploadFile = File(...),
     94:     db: Session = Depends(get_db),
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 145 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     143: 
     144: @router.get("/certificati/", response_model=List[CertificatoSchema], dependencies=[Depends(deps.verify_license)])
 >>> 145: def get_certificati(validated: Optional[bool] = Query(None), db: Session = Depends(get_db)):
     146:     query = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso))
     147:     if validated is not None:
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 190 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Certificato non trovato" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     188:     db_cert = db.get(Certificato, certificato_id)
     189:     if not db_cert:
 >>> 190:         raise HTTPException(status_code=404, detail="Certificato non trovato")
     191: 
     192:     status = certificate_logic.get_certificate_status(db, db_cert)
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 241 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     239: 
     240: @router.post("/certificati/", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 241: def create_certificato(
     242:     certificato: CertificatoCreazioneSchema,
     243:     db: Session = Depends(get_db),
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 382 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 77 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     380: 
     381: @router.put("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 382: def update_certificato(
     383:     certificato_id: int,
     384:     certificato: CertificatoAggiornamentoSchema,
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 602 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 57 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     600: 
     601: @router.post("/dipendenti/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 602: async def import_dipendenti_csv(
     603:     file: UploadFile = File(...),
     604:     db: Session = Depends(get_db),
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 749 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Dipendente non trovato" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     747: 
     748:     if not dipendente:
 >>> 749:         raise HTTPException(status_code=404, detail="Dipendente non trovato")
     750: 
     751:     # Calculate status for all certs
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

## 📄 `desktop_app/main.py`

### Riga 482 🟡 🟢
**Problema:** Remove this unneeded "pass".
**Regola:** `python:S2772` - "pass" should not be used needlessly

```python
     480:         if os.name != 'nt':
     481:             return
 >>> 482:         pass
     483: 
     484:     def check_backend_health(self):
```

**❓ Perché è un problema:**
The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

### Noncompliant code example

```
def foo(arg):
    print(arg)
    pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

### Compliant solution

```
def foo(arg):
    print(arg)
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 494 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     492:                 try:
     493:                     detail = response.json().get("detail", "Errore sconosciuto")
 >>> 494:                 except:
     495:                     detail = response.text
     496: 
```

**❓ Perché è un problema:**
A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseEx

**✅ Come risolvere:**
Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

### Noncompliant code example

```
try:
    ...
except SystemExit:  # Noncompliant: the SystemExit exception is not re-raised.
    pass

try:
    ...
except BaseException:  # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
    pass

try:
    ...
except:  # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
    pass
```

### Compliant solution

```
try:
    ...
except SystemExit as e:
    ...
    raise e

try:
    ...
except BaseException as e:
    ...
    raise e

try:
    ...
except FileNotFoundError:
    ... # Handle a more specific exception
```

**📚 Risorse:**
### Documentation

  -  PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

  -  Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

  -  Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
  

  -  CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 503 🟡 🟢
**Problema:** Remove this unneeded "pass".
**Regola:** `python:S2772` - "pass" should not be used needlessly

```python
     501:             print(f"[DEBUG] Health Check Warning: {e}")
     502:             # We proceed, as network errors might be temporary or handled by LoginView
 >>> 503:             pass
     504: 
     505:     def show_notification(self, title, message, icon_name="file-text.svg"):
```

**❓ Perché è un problema:**
The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

### Noncompliant code example

```
def foo(arg):
    print(arg)
    pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

### Compliant solution

```
def foo(arg):
    print(arg)
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 539 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Sola Lettura" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     537:         """
     538:         if self.dashboard and getattr(self.dashboard, 'is_read_only', False):
 >>> 539:             CustomMessageDialog.show_warning(self.master_window, "Sola Lettura", "Impossibile avviare l'analisi in modalità Sola Lettura.")
     540:             return
     541: 
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 573 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     571:             CustomMessageDialog.show_error(self.master_window, "Errore Importazione", f"Impossibile importare il file:\n{e}")
     572: 
 >>> 573:     def on_login_success(self, user_info):
     574:         # Create Dashboard if not exists
     575:         if not self.dashboard:
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 591 🟡 🟢
**Problema:** Remove this unneeded "pass".
**Regola:** `python:S2772` - "pass" should not be used needlessly

```python
     589:             
     590:             # We can expose a method on Dashboard to register for completion.
 >>> 591:             pass
     592: 
     593:         # Start Inactivity Timer (1 hour)
```

**❓ Perché è un problema:**
The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

### Noncompliant code example

```
def foo(arg):
    print(arg)
    pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

### Compliant solution

```
def foo(arg):
    print(arg)
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 641 🟡 🟢
**Problema:** Remove the unused local variable "pending_count".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     639: 
     640:         # Check for pending documents notification
 >>> 641:         pending_count = user_info.get("pending_documents_count", 0)
     642:         
     643:         # Play Welcome Speech (Voice Service)
```

**❓ Perché è un problema:**
An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

### What is the potential impact?

Having unused local variables in your code can lead to several issues:

  -  **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
  can distract from the main logic of the code. 

  -  **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
  to confusion and misinterpretation of the code’s inte

**✅ Come risolvere:**
The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

### Noncompliant code example

```
def hello(name):
    message = "Hello " + name # Noncompliant - message is unused
    print(name)
for i in range(10): # Noncompliant - i is unused
    foo()
```

### Compliant solution

```
def hello(name):
    message = "Hello " + name
    print(message)
for _ in range(10):
    foo()
```

---

## 📄 `desktop_app/views/import_view.py`

### Riga 80 🟡 🟢
**Problema:** Remove the unused local variable "reason".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     78: 
     79:         error_category = "ALTRI ERRORI"
 >>> 80:         reason = "Errore Generico" # Default
     81: 
     82:         # Determine category and paths
```

**❓ Perché è un problema:**
An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

### What is the potential impact?

Having unused local variables in your code can lead to several issues:

  -  **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
  can distract from the main logic of the code. 

  -  **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
  to confusion and misinterpretation of the code’s inte

**✅ Come risolvere:**
The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

### Noncompliant code example

```
def hello(name):
    message = "Hello " + name # Noncompliant - message is unused
    print(name)
for i in range(10): # Noncompliant - i is unused
    foo()
```

### Compliant solution

```
def hello(name):
    message = "Hello " + name
    print(message)
for _ in range(10):
    foo()
```

---

### Riga 96 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal '%d/%m/%Y' 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     94:             else:
     95:                 try:
 >>> 96:                     scadenza_date = datetime.strptime(data_scadenza_str, '%d/%m/%Y').date()
     97:                     file_scadenza = scadenza_date.strftime(DATE_FORMAT_FILE)
     98: 
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 120 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     118:             return False, None, None, None, None, None
     119: 
 >>> 120:     def _handle_save_response(self, save_response, original_filename, certificato, current_op_path):
     121:         if save_response.status_code == 200:
     122:             cert_data = save_response.json()
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 183 🟡 🟢
**Problema:** Replace the unused local variable "err_cat_override" with "_".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     181: 
     182:         if data:
 >>> 183:             success, err_cat_override, emp_folder, cat_fs, status, new_name = self._process_single_cert(os.path.basename(source_path), data, source_path)
     184:             if success:
     185:                 target_dir = os.path.join(self.output_folder, DIR_ANALYSIS_ERRORS, error_category, emp_folder, cat_fs, status)
```

**❓ Perché è un problema:**
An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

### What is the potential impact?

Having unused local variables in your code can lead to several issues:

  -  **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
  can distract from the main logic of the code. 

  -  **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
  to confusion and misinterpretation of the code’s inte

**✅ Come risolvere:**
The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

### Noncompliant code example

```
def hello(name):
    message = "Hello " + name # Noncompliant - message is unused
    print(name)
for i in range(10): # Noncompliant - i is unused
    foo()
```

### Compliant solution

```
def hello(name):
    message = "Hello " + name
    print(message)
for _ in range(10):
    foo()
```

---

### Riga 200 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     198:             self.log_message.emit(f"Impossibile spostare il file {os.path.basename(source_path)}: {e}", "red")
     199: 
 >>> 200:     def process_pdf(self, file_path):
     201:         original_filename = os.path.basename(file_path)
     202:         self.current_file_path = file_path # Store for fallback
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `desktop_app/components/neural_3d.py`

### Riga 13 🔴 🟡
**Problema:** Provide a seed for this random generator.
**Regola:** `python:S6709` - Results that depend on random number generation should be reproducible

```python
     11: 
     12:         # Use new Generator API
 >>> 13:         self.rng = np.random.default_rng()
     14: 
     15:         # --- 3D State (Vectorized) ---
```

**❓ Perché è un problema:**
Data science and machine learning tasks make extensive use of random number generation. It may, for example, be used for:

  -  Model initialization
    
       Randomness is used to initialize the parameters of machine learning models. Initializing parameters with random values helps to break
      symmetry and prevents models from getting stuck in local optima during training. By providing a random starting point, the model can explore
      different regions of the parameter space and potentially find better solutions. 

      
  -  Regularization techniques
    
       Randomness is used to introduce noise into the learning process. Techniques like dropout and data augmentation use random numbers to
      randomly drop or modify features or samples during training. This helps to regula

**✅ Come risolvere:**
To fix this issue, provide a predictable seed to the estimator or the utility function.

### Noncompliant code example

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y) # Noncompliant: no seed parameter is provided
```

### Compliant solution

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import numpy as np

rng = np.random.default_rng(42)
X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y, random_state=rng.integers(1)) # Compliant
```

**📚 Risorse:**
### Documentation

  -  NumPy documentation - [NEP 19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html) 

  -  Scikit-learn documentation - [Glossary random_state](https://scikit-learn.org/stable/glossary.html#term-random_state) 

  -  Scikit-learn documentation - [Controlling randomness](https://scikit-learn.org/stable/common_pitfalls.html#controlling-randomness)
  

### Standards

  -  STIG Viewer - Application Security and
  Development: V-222642 - The application must not contain 

---

### Riga 13 🟣 🟡
**Problema:** Provide a seed for this random generator.
**Regola:** `python:S6709` - Results that depend on random number generation should be reproducible

```python
     11: 
     12:         # Use new Generator API
 >>> 13:         self.rng = np.random.default_rng()
     14: 
     15:         # --- 3D State (Vectorized) ---
```

**❓ Perché è un problema:**
Data science and machine learning tasks make extensive use of random number generation. It may, for example, be used for:

  -  Model initialization
    
       Randomness is used to initialize the parameters of machine learning models. Initializing parameters with random values helps to break
      symmetry and prevents models from getting stuck in local optima during training. By providing a random starting point, the model can explore
      different regions of the parameter space and potentially find better solutions. 

      
  -  Regularization techniques
    
       Randomness is used to introduce noise into the learning process. Techniques like dropout and data augmentation use random numbers to
      randomly drop or modify features or samples during training. This helps to regula

**✅ Come risolvere:**
To fix this issue, provide a predictable seed to the estimator or the utility function.

### Noncompliant code example

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y) # Noncompliant: no seed parameter is provided
```

### Compliant solution

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import numpy as np

rng = np.random.default_rng(42)
X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y, random_state=rng.integers(1)) # Compliant
```

**📚 Risorse:**
### Documentation

  -  NumPy documentation - [NEP 19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html) 

  -  Scikit-learn documentation - [Glossary random_state](https://scikit-learn.org/stable/glossary.html#term-random_state) 

  -  Scikit-learn documentation - [Controlling randomness](https://scikit-learn.org/stable/common_pitfalls.html#controlling-randomness)
  

### Standards

  -  STIG Viewer - Application Security and
  Development: V-222642 - The application must not contain 

---

### Riga 13 🟡 🟡
**Problema:** Provide a seed for this random generator.
**Regola:** `python:S6709` - Results that depend on random number generation should be reproducible

```python
     11: 
     12:         # Use new Generator API
 >>> 13:         self.rng = np.random.default_rng()
     14: 
     15:         # --- 3D State (Vectorized) ---
```

**❓ Perché è un problema:**
Data science and machine learning tasks make extensive use of random number generation. It may, for example, be used for:

  -  Model initialization
    
       Randomness is used to initialize the parameters of machine learning models. Initializing parameters with random values helps to break
      symmetry and prevents models from getting stuck in local optima during training. By providing a random starting point, the model can explore
      different regions of the parameter space and potentially find better solutions. 

      
  -  Regularization techniques
    
       Randomness is used to introduce noise into the learning process. Techniques like dropout and data augmentation use random numbers to
      randomly drop or modify features or samples during training. This helps to regula

**✅ Come risolvere:**
To fix this issue, provide a predictable seed to the estimator or the utility function.

### Noncompliant code example

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y) # Noncompliant: no seed parameter is provided
```

### Compliant solution

```
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import numpy as np

rng = np.random.default_rng(42)
X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y, random_state=rng.integers(1)) # Compliant
```

**📚 Risorse:**
### Documentation

  -  NumPy documentation - [NEP 19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html) 

  -  Scikit-learn documentation - [Glossary random_state](https://scikit-learn.org/stable/glossary.html#term-random_state) 

  -  Scikit-learn documentation - [Controlling randomness](https://scikit-learn.org/stable/common_pitfalls.html#controlling-randomness)
  

### Standards

  -  STIG Viewer - Application Security and
  Development: V-222642 - The application must not contain 

---

### Riga 154 🟡 🟡
**Problema:** Remove this commented out code.
**Regola:** `python:S125` - Sections of code should not be commented out

```python
     152:         active_pulses = []
     153:         for p in self.pulses:
 >>> 154:             p[2] += p[3] # Progress += Speed
     155:             if p[2] &lt; 1.0:
     156:                 active_pulses.append(p)
```

**❓ Perché è un problema:**
Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

## 📄 `admin/offusca/build_dist.py`

### Riga 85 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     83:     return libs
     84: 
 >>> 85: def _scan_file_imports(path, std_libs):
     86:     """Helper to scan imports from a single file."""
     87:     imports = set()
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 101 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     99:                 if root_pkg not in std_libs: imports.add(root_pkg)
     100:     except Exception: # S5754: Catch-all is fine here for scanner resilience, but let's be explicit
 >>> 101:         pass # NOSONAR: Ignore parse errors during scan
     102:     return imports
     103: 
```

**❓ Perché è un problema:**
Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are sup

**✅ Come risolvere:**
Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

  -  Use `# NOSONAR` alone to suppress all issues on the line 

  -  Use `# NOSONAR()` with empty parentheses to suppress all issues 

  -  Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

  -  Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

  -  The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

  -  Close all parentheses properly 

For `# noqa`:

  -  Use `# noqa` alone to suppress all issues on the line 

  -  Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

  -  Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

  -  Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

### Noncompliant code example

```
def example():
    x = 1  # NOSONAR(  # Noncompliant
    y = 2  # NOSONAR(a,)  # Noncompliant
    z 

**📚 Risorse:**
### Documentation

  -  SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

  -  Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

### Riga 194 🟡 🟡
**Problema:** Remove the unused function parameter "iscc_exe".
**Regola:** `python:S1172` - Unused function parameters should be removed

```python
     192:     return modules
     193: 
 >>> 194: def _prepare_obfuscation(iscc_exe):
     195:     kill_existing_process()
     196: 
```

**❓ Perché è un problema:**
A typical code smell known as unused function parameters refers to parameters declared in a function but not used anywhere within the function’s
body. While this might seem harmless at first glance, it can lead to confusion and potential errors in your code. Disregarding the values passed to
such parameters, the function’s behavior will be the same, but the programmer’s intention won’t be clearly expressed anymore. Therefore, removing
function parameters that are not being utilized is considered best practice.

### Exceptions

This rule ignores overriding methods.

```
class C(B):
  def do_something(self, a, b): # no issue reported on b
    return self.compute(a)
```

This rule also ignores variables named with a single underscore `_`. Such naming is a common practice for indicating that t

**✅ Come risolvere:**
Having unused function parameters in your code can lead to confusion and misunderstanding of a developer’s intention. They reduce code readability
and introduce the potential for errors. To avoid these problems, developers should remove unused parameters from function declarations.

### Noncompliant code example

```
def do_something(a, b): # second parameter is unused
  return compute(a)
```

### Compliant solution

```
def do_something(a):
  return compute(a)
```

---

### Riga 238 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 27 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     236:         shutil.copy(os.path.join(ROOT_DIR, FILE_REQUIREMENTS), os.path.join(OBF_DIR, FILE_REQUIREMENTS))
     237: 
 >>> 238: def build():
     239:     # S3776: Refactored to reduce complexity
     240:     try:
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `desktop_app/utils.py`

### Riga 96 🟡 🔴
**Problema:** Replace this "re.sub()" call by a "str.replace()" function call.
**Regola:** `python:S5361` - `str.replace` should be preferred to `re.sub`

```python
     94:     # 1. Always replace acute accents on a, i, u (Phonetic stress markers)
     95:     # S6397: Replaced character class [x] with x
 >>> 96:     text = re.sub(r'á', 'a', text)
     97:     text = re.sub(r'í', 'i', text)
     98:     text = re.sub(r'ú', 'u', text)
```

**❓ Perché è un problema:**
An `re.sub` call always performs an evaluation of the first argument as a regular expression, even if no regular expression features
were used. This has a significant performance cost and therefore should be used with care.

When `re.sub` is used, the first argument should be a real regular expression. If it’s not the case, `str.replace` does
exactly the same thing as `re.sub` without the performance drawback of the regex.

This rule raises an issue for each `re.sub` used with a simple string as first argument which doesn’t contains special regex character
or pattern.

### Noncompliant code example

```
init = "Bob is a Bird... Bob is a Plane... Bob is Superman!"
changed = re.sub(r"Bob is", "It's", init) # Noncompliant
changed = re.sub(r"\.\.\.", ";", changed) # Noncompliant
```

### Compl

---

### Riga 97 🟡 🔴
**Problema:** Replace this "re.sub()" call by a "str.replace()" function call.
**Regola:** `python:S5361` - `str.replace` should be preferred to `re.sub`

```python
     95:     # S6397: Replaced character class [x] with x
     96:     text = re.sub(r'á', 'a', text)
 >>> 97:     text = re.sub(r'í', 'i', text)
     98:     text = re.sub(r'ú', 'u', text)
     99: 
```

**❓ Perché è un problema:**
An `re.sub` call always performs an evaluation of the first argument as a regular expression, even if no regular expression features
were used. This has a significant performance cost and therefore should be used with care.

When `re.sub` is used, the first argument should be a real regular expression. If it’s not the case, `str.replace` does
exactly the same thing as `re.sub` without the performance drawback of the regex.

This rule raises an issue for each `re.sub` used with a simple string as first argument which doesn’t contains special regex character
or pattern.

### Noncompliant code example

```
init = "Bob is a Bird... Bob is a Plane... Bob is Superman!"
changed = re.sub(r"Bob is", "It's", init) # Noncompliant
changed = re.sub(r"\.\.\.", ";", changed) # Noncompliant
```

### Compl

---

### Riga 98 🟡 🔴
**Problema:** Replace this "re.sub()" call by a "str.replace()" function call.
**Regola:** `python:S5361` - `str.replace` should be preferred to `re.sub`

```python
     96:     text = re.sub(r'á', 'a', text)
     97:     text = re.sub(r'í', 'i', text)
 >>> 98:     text = re.sub(r'ú', 'u', text)
     99: 
     100:     # Regex lookahead (?=[^\W_]) ensures the character is followed by a word character
```

**❓ Perché è un problema:**
An `re.sub` call always performs an evaluation of the first argument as a regular expression, even if no regular expression features
were used. This has a significant performance cost and therefore should be used with care.

When `re.sub` is used, the first argument should be a real regular expression. If it’s not the case, `str.replace` does
exactly the same thing as `re.sub` without the performance drawback of the regex.

This rule raises an issue for each `re.sub` used with a simple string as first argument which doesn’t contains special regex character
or pattern.

### Noncompliant code example

```
init = "Bob is a Bird... Bob is a Plane... Bob is Superman!"
changed = re.sub(r"Bob is", "It's", init) # Noncompliant
changed = re.sub(r"\.\.\.", ";", changed) # Noncompliant
```

### Compl

---

## 📄 `desktop_app/main_window_ui.py`

### Riga 156 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     154:     logout_requested = pyqtSignal()
     155: 
 >>> 156:     def __init__(self, parent=None):
     157:         super().__init__(parent)
     158:         self.setFixedWidth(260)
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 261 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Scadenza Licenza" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     259:                   self.license_layout.addWidget(l1)
     260: 
 >>> 261:              expiry_str = license_data.get("Scadenza Licenza", "")
     262:              if expiry_str:
     263:                   l2 = QLabel(f"Scadenza Licenza:\n{expiry_str}")
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 619 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     617:         self._connect_cross_view_signals()
     618: 
 >>> 619:     def _connect_cross_view_signals(self):
     620:         # Refresh logic across views
     621:         imp = self.views.get("import")
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `admin/crea_licenze/admin_license_gui.py`

### Riga 33 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Segoe UI" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     31:         style.theme_use('clam')
     32:         # S1192: Use constant
 >>> 33:         font_style = ("Segoe UI", 10)
     34:         style.configure("TLabel", font=font_style)
     35:         style.configure("TButton", font=("Segoe UI", 10, "bold"))
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 118 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     116:         return config_path
     117: 
 >>> 118:     def generate(self):
     119:         # S3776: Refactored
     120:         disk_serial = self.ent_disk.get().strip()
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `app/services/ai_extraction.py`

### Riga 163 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 21 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     161:         return model.generate_content([pdf_file_part, prompt])
     162: 
 >>> 163: def _find_json_block(text, start_idx, stack):
     164:     for i, char in enumerate(text[start_idx:], start=start_idx):
     165:         if char == '{' or char == '[':
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 168 🟡 🟡
**Problema:** Merge this if statement with the enclosing one.
**Regola:** `python:S1066` - Mergeable "if" statements should be combined

```python
     166:             stack.append(char)
     167:         elif char == '}' or char == ']':
 >>> 168:             if stack:
     169:                 last = stack[-1]
     170:                 # S1066: Merged if statements
```

**❓ Perché è un problema:**
Nested code - blocks of code inside blocks of code - is eventually necessary, but increases complexity. This is why keeping the code as flat as
possible, by avoiding unnecessary nesting, is considered a good practice.

Merging `if` statements when possible will decrease the nesting of the code and improve its readability.

Code like

```
if condition1:
    if condition2:             # Noncompliant
        # ...
```

Will be more readable as

```
if condition1 and condition2:  # Compliant
    # ...
```

**✅ Come risolvere:**
If merging the conditions seems to result in a more complex code, extracting the condition or part of it in a named function or variable is a
better approach to fix readability.

### Noncompliant code example

```
if file.isValid():
  if file.isfile() or file.isdir():     # Noncompliant
    # ...
```

### Compliant solution

```
def isFileOrDirectory(File file):
  return file.isFile() or file.isDirectory()

if file.isValid() and isFileOrDirectory(file): # Compliant
  # ...
```

---

## 📄 `desktop_app/views/config_view.py`

### Riga 252 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     250:                 CustomMessageDialog.show_error(self, "Errore", str(e))
     251: 
 >>> 252:     def change_own_password(self):
     253:         dialog = ChangePasswordDialog(self)
     254:         if dialog.exec():
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 642 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     640:                     # S5754: Or fallback. S5754 says re-raise SystemExit. This catch-all is fine for formatting fallback.
     641:                     # Adding comment as per best practice
 >>> 642:                     # NOSONAR: Fallback to raw string
     643:                     formatted_date = ts_str
     644: 
```

**❓ Perché è un problema:**
Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are sup

**✅ Come risolvere:**
Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

  -  Use `# NOSONAR` alone to suppress all issues on the line 

  -  Use `# NOSONAR()` with empty parentheses to suppress all issues 

  -  Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

  -  Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

  -  The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

  -  Close all parentheses properly 

For `# noqa`:

  -  Use `# noqa` alone to suppress all issues on the line 

  -  Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

  -  Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

  -  Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

### Noncompliant code example

```
def example():
    x = 1  # NOSONAR(  # Noncompliant
    y = 2  # NOSONAR(a,)  # Noncompliant
    z 

**📚 Risorse:**
### Documentation

  -  SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

  -  Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

## 📄 `launcher.py`

### Riga 397 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 22 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     395:     return exists, is_valid
     396: 
 >>> 397: def _handle_recovery_action(parent, msg, target):
     398:     # S3776: Refactored logic
     399:     browse_btn = msg.addButton("Sfoglia / Ripristina...", QMessageBox.ButtonRole.ActionRole)
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `app/services/sync_service.py`

### Riga 185 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 21 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     183:             logging.error(f"Error moving linked orphan file: {e}")
     184: 
 >>> 185: def synchronize_all_files(db: Session):
     186:     """
     187:     Scans all certificates and ensures their PDF files are located in the correct
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `app/services/file_maintenance.py`

### Riga 36 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 18 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     34:     return known_files
     35: 
 >>> 36: def scan_and_archive_orphans(db: Session, database_path: str):
     37:     """
     38:     Bug 8 Fix: Identify files in 'DOCUMENTI DIPENDENTI' that are NOT in the database.
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `desktop_app/views/anagrafica_view.py`

### Riga 16 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     14:     def __init__(self, title, value, color="#3B82F6", parent=None):
     15:         super().__init__(parent)
 >>> 16:         self.setStyleSheet(f"""
 >>> 17:             QFrame {{
 >>> 18:                 background-color: #FFFFFF;
 >>> 19:                 border: 1px solid #E5E7EB;
 >>> 20:                 border-radius: 8px;
 >>> 21:             }}
 >>> 22:         """)
     23:         layout = QVBoxLayout(self)
     24:         layout.setContentsMargins(15, 15, 15, 15)
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

## 📄 `desktop_app/views/login_view.py`

### Riga 767 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 44 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     765:         user_info["pending_documents_count"] = self.pending_count
     766: 
 >>> 767:     def on_login_success(self, response):
     768:         # S3776: Refactored to reduce complexity
     769:         try:
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `app/api/routers/auth.py`

### Riga 143 🟡 🔴
**Problema:** Change this default value to "None" and initialize this parameter inside the function/method.
**Regola:** `python:S5717` - Function parameters' default values should not be modified or assigned

```python
     141:     request: Request,
     142:     # S5717: Fixed mutable default argument (not present here but handled as prevention)
 >>> 143:     current_user: deps.User = Depends(deps.get_current_user),
     144:     db: Session = Depends(get_db)
     145: ):
```

**❓ Perché è un problema:**
In Python, function parameters can have default values.

These default values are expressions which are evalutated when the function is defined, i.e. only once. The same default value will be used every
time the function is called. Therefore, modifying it will have an effect on every subsequent call. This can lead to confusing bugs.

```
def myfunction(param=foo()):  # foo is called only once, when the function is defined.
    ...
```

For the same reason, it is also a bad idea to store mutable default values in another object (ex: as an attribute). Multiple instances will then
share the same value and modifying one object will modify all of them.

This rule raises an issue when:

  -  a default value is either modified in the function or assigned to anything other than a variable and it h

**✅ Come risolvere:**
When a parameter default value is meant to be a mutable object, it is best to keep the parameter optional and instantiate the mutable object in the
function’s body directly.

### Noncompliant code example

In the following example, the parameter "param" has `list()` as a default value. This list is created only once and then reused in every
call. Thus when appending `'a'` to this list in the body of the function, the next call will have `['a']` as a default
value.

```
def myfunction(param=list()):  # Noncompliant: param is a list that gets mutated
    param.append('a')  # modification of the default value.
    return param

print(myfunction()) # returns ['a']
print(myfunction()) # returns ['a', 'a']
print(myfunction()) # returns ['a', 'a', 'a']
```

### Compliant solution

```
def myfunction(param=None):
    if param is None:
        param = list()
    param.append('a')
    return param

print(myfunction()) # returns ['a']
print(myfunction()) # returns ['a']
print(myfunction()) # retu

**📚 Risorse:**
### Documentation

  -  Python documentation - [Function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions) 

### External coding guidelines

  -  The Hitchhiker’s Guide to Python - [Common Gotchas](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)

---

## 📄 `app/services/notification_service.py`

### Riga 258 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     256:         logging.error(f"Failed to send security alert: {e}")
     257: 
 >>> 258: def get_report_data(db: Session):
     259:     # S3776: Refactored logic to reduce complexity
     260:     today = date.today()
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---
