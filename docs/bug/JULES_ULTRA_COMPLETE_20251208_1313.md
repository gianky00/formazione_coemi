# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 11 issues
**Tempo:** 2h 41min

---

## 📄 `app/api/main.py`

### Riga 423 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 68 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     421: 
     422: @router.put("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 423: def update_certificato(
     424:     certificato_id: int,
     425:     certificato: CertificatoAggiornamentoSchema,
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

### Riga 661 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     659: 
     660: @router.post("/dipendenti/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 661: async def import_dipendenti_csv(
     662:     file: UploadFile = File(...),
     663:     db: Session = Depends(get_db),
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

## 📄 `desktop_app/main.py`

### Riga 548 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "Sola Lettura" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     546:             # S1192: Use duplicated string literal if extracting constants or just ignore 3 times.
     547:             # Using literal here as extracting to a constant file for UI messages is out of scope for this pass.
 >>> 548:             CustomMessageDialog.show_warning(self.master_window, "Sola Lettura", "Impossibile avviare l'analisi in modalità Sola Lettura.")
     549:             return
     550: 
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

### Riga 579 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     577:             CustomMessageDialog.show_error(self.master_window, "Errore Importazione", f"Impossibile importare il file:\n{e}")
     578: 
 >>> 579:     def on_login_success(self, user_info):
     580:         # Create Dashboard if not exists
     581:         if not self.dashboard:
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

## 📄 `desktop_app/views/login_view.py`

### Riga 767 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 22 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     765:         user_info["pending_documents_count"] = self.pending_count
     766: 
 >>> 767:     def _handle_password_change(self):
     768:         """Helper to handle forced password change workflow."""
     769:         while True:
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

## 📄 `desktop_app/views/import_view.py`

### Riga 224 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     222:             self.log_message.emit(f"Impossibile spostare il file {os.path.basename(source_path)}: {e}", "red")
     223: 
 >>> 224:     def process_pdf(self, file_path):
     225:         original_filename = os.path.basename(file_path)
     226:         self.current_file_path = file_path # Store for fallback
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

## 📄 `app/api/routers/auth.py`

### Riga 142 🟡 🔴
**Problema:** Change this default value to "None" and initialize this parameter inside the function/method.
**Regola:** `python:S5717` - Function parameters' default values should not be modified or assigned

```python
     140:     password_data: UserPasswordUpdate,
     141:     request: Request,
 >>> 142:     current_user: deps.User = Depends(deps.get_current_user),
     143:     db: Session = Depends(get_db)
     144: ):
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
