# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 10 issues
**Tempo:** 1h 8min

---

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 74 🟡 🟡
**Problema:** Prefer using an optional chain expression instead, as it's more concise and easier to read.
**Regola:** `javascript:S6582` - Optional chaining should be preferred

```jsx
     72:     const globalContext = globalThis;
     73: 
 >>> 74:     if (globalContext.qt &amp;&amp; globalContext.qt.webChannelTransport) {
     75:       // Assign to a variable to avoid "new" side effect warning, although QWebChannel is designed this way.
     76:       // eslint-disable-next-line no-unused-vars
```

**❓ Perché è un problema:**
Optional chaining allows to safely access nested properties or methods of an object without having to check for the existence of each intermediate
property manually. It provides a concise and safe way to access nested properties or methods without having to write complex and error-prone
`null`/`undefined` checks.

This rule flags logical operations that can be safely replaced with the `?.` optional chaining operator.

**✅ Come risolvere:**
Replace with `?.` optional chaining the logical expression that checks for `null`/`undefined` before accessing the
property of an object, the element of an array, or calling a function.

### Noncompliant code example

```
function foo(obj, arr, fn) {
    if (obj &amp;&amp; obj.value) {}
    if (arr &amp;&amp; arr[0])    {}
    if (fn &amp;&amp; fn(42))     {}
}
```

### Compliant solution

```
function foo(obj, arr, fn) {
    if (obj?.value) {}
    if (arr?.[0])   {}
    if (fn?.(42))   {}
}
```

**📚 Risorse:**
### Documentation

  -  [typescript-eslint](https://typescript-eslint.io/) - Rule [prefer-optional-chain](https://github.com/typescript-eslint/typescript-eslint/blob/main/packages/eslint-plugin/docs/rules/prefer-optional-chain.mdx) 

  -  MDN web docs - [Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)

---

### Riga 77 🟡 🟡
**Problema:** Remove this useless assignment to variable "channel".
**Regola:** `javascript:S1854` - Unused assignments should be removed

```jsx
     75:       // Assign to a variable to avoid "new" side effect warning, although QWebChannel is designed this way.
     76:       // eslint-disable-next-line no-unused-vars
 >>> 77:       const channel = new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     78:         if (c.objects &amp;&amp; c.objects.bridge) {
     79:             setBridge(c.objects.bridge);
```

**❓ Perché è un problema:**
Dead stores refer to assignments made to local variables that are subsequently never used or immediately overwritten. Such assignments are
unnecessary and don’t contribute to the functionality or clarity of the code. They may even negatively impact performance. Removing them enhances code
cleanliness and readability. Even if the unnecessary operations do not do any harm in terms of the program’s correctness, they are - at best - a waste
of computing resources.

### Exceptions

The rule ignores

  -  Initializations to `-1`, `0`, `1`, `undefined`, `[]`, `{}`,
  `true`, `false` and `""`. 

  -  Variables that start with an underscore (e.g. `_unused`) are ignored. 

  -  Assignment of `null` is ignored because it is sometimes used to help garbage collection 

  -  Increment and decrement expr

**✅ Come risolvere:**
Remove the unnecessary assignment, then test the code to make sure that the right-hand side of a given assignment had no side effects (e.g. a
method that writes certain data to a file and returns the number of written bytes).

### Noncompliant code example

```
function foo(y) {
  let x = 100; // Noncompliant: dead store
  x = 150;     // Noncompliant: dead store
  x = 200;
  return x + y;
}
```

### Compliant solution

```
function foo(y) {
  let x = 200; // Compliant: no unnecessary assignment
  return x + y;
}
```

**📚 Risorse:**
### Standards

  -  CWE - [CWE-563 - Assignment to Variable without Use ('Unused Variable')](https://cwe.mitre.org/data/definitions/563) 

### Related rules

  -  S1763 - All code should be reachable 

  -  S2589 - Boolean expressions should not be gratuitous 

  -  S3516 - Function returns should not be invariant 

  -  S3626 - Jump statements should not be redundant

---

### Riga 78 🟡 🟡
**Problema:** Prefer using an optional chain expression instead, as it's more concise and easier to read.
**Regola:** `javascript:S6582` - Optional chaining should be preferred

```jsx
     76:       // eslint-disable-next-line no-unused-vars
     77:       const channel = new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
 >>> 78:         if (c.objects &amp;&amp; c.objects.bridge) {
     79:             setBridge(c.objects.bridge);
     80:         }
```

**❓ Perché è un problema:**
Optional chaining allows to safely access nested properties or methods of an object without having to check for the existence of each intermediate
property manually. It provides a concise and safe way to access nested properties or methods without having to write complex and error-prone
`null`/`undefined` checks.

This rule flags logical operations that can be safely replaced with the `?.` optional chaining operator.

**✅ Come risolvere:**
Replace with `?.` optional chaining the logical expression that checks for `null`/`undefined` before accessing the
property of an object, the element of an array, or calling a function.

### Noncompliant code example

```
function foo(obj, arr, fn) {
    if (obj &amp;&amp; obj.value) {}
    if (arr &amp;&amp; arr[0])    {}
    if (fn &amp;&amp; fn(42))     {}
}
```

### Compliant solution

```
function foo(obj, arr, fn) {
    if (obj?.value) {}
    if (arr?.[0])   {}
    if (fn?.(42))   {}
}
```

**📚 Risorse:**
### Documentation

  -  [typescript-eslint](https://typescript-eslint.io/) - Rule [prefer-optional-chain](https://github.com/typescript-eslint/typescript-eslint/blob/main/packages/eslint-plugin/docs/rules/prefer-optional-chain.mdx) 

  -  MDN web docs - [Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)

---

## 📄 `app/api/main.py`

### Riga 238 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 21 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     236:     return False, None
     237: 
 >>> 238: def _update_cert_fields(db_cert, update_data, db):
     239:     """Updates basic fields and handles employee matching logic."""
     240:     if 'data_nascita' in update_data:
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

### Riga 611 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     609: 
     610: @router.put("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 611: def update_certificato(
     612:     certificato_id: int,
     613:     certificato: CertificatoAggiornamentoSchema,
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

### Riga 178 🟡 🟡
**Problema:** Merge this if statement with the enclosing one.
**Regola:** `python:S1066` - Mergeable "if" statements should be combined

```python
     176:             stack.append(char)
     177:         elif char == '}' or char == ']':
 >>> 178:             if _check_closing_char(stack, char):
     179:                 return i + 1
     180:     return -1
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

### Riga 143 🟡 🔴
**Problema:** Change this default value to "None" and initialize this parameter inside the function/method.
**Regola:** `python:S5717` - Function parameters' default values should not be modified or assigned

```python
     141:     password_data: UserPasswordUpdate,
     142:     request: Request,
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
