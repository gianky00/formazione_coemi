# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 4 issues
**Tempo:** 26min

---

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 75 🔴 🟡
**Problema:** Either remove this useless object instantiation of "globalContext.QWebChannel" or use it.
**Regola:** `javascript:S1848` - Objects should not be created to be dropped immediately without being used

```jsx
     73: 
     74:     if (globalContext.qt?.webChannelTransport) {
 >>> 75:       new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     76:         if (c.objects?.bridge) {
     77:             setBridge(c.objects.bridge);
```

**❓ Perché è un problema:**
Creating an object without assigning it to a variable or using it in any function means the object is essentially created for no reason and may be
dropped immediately without being used. Most of the time, this is due to a missing piece of code and could lead to an unexpected behavior.

If it’s intended because the constructor has side effects, that side effect should be moved into a separate method and called directly. This can
help to improve the performance and readability of the code.

```
new MyConstructor(); // Noncompliant: object may be dropped
```

Determine if the objects are necessary for the code to function correctly. If they are not required, remove them from the code. Otherwise, assign
them to a variable for later use.

```
let something = new MyConstructor();
```

### Except

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`Object.prototype.constructor`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/constructor) 

  -  MDN web docs - [constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor) 

  -  MDN web docs - [`new` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/new)

---

## 📄 `app/api/main.py`

### Riga 238 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     236:     return False, None
     237: 
 >>> 238: def _update_cert_identity(db_cert, update_data, db):
     239:     """Updates certificate identity fields (name, date of birth) and matches employee."""
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

## 📄 `desktop_app/main_window_ui.py`

### Riga 255 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     253:         self.main_layout.addWidget(self.nav_container)
     254: 
 >>> 255:     def _setup_license_info(self):
     256:         """Initializes the license information section."""
     257:         self.license_frame = QFrame()
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
