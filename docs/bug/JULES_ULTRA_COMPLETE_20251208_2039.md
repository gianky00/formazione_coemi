# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 33 issues
**Tempo:** 4h 5min

---

## 📄 `admin/riepilogo_Bug_Sonar.py`

### Riga 133 🟡 🟢
**Problema:** Remove the unused local variable "e".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     131:                 try:
     132:                     return func(*args, **kwargs)
 >>> 133:                 except (requests.exceptions.RequestException,) as e:
     134:                     stats['retries'] += 1
     135:                     if attempt &lt; max_retries - 1:
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

### Riga 225 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal r'<[^>]+>' 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     223:     text = re.sub(r'&lt;br\s*/?&gt;', '\n', text)
     224:     text = re.sub(r'&lt;a[^&gt;]*href="([^"]*)"[^&gt;]*&gt;(.*?)&lt;/a&gt;', r'[\2](\1)', text)
 >>> 225:     text = re.sub(r'&lt;[^&gt;]+&gt;', '', text)
     226:     
     227:     entities = {'&amp;nbsp;': ' ', '&amp;lt;': '&lt;', '&amp;gt;': '&gt;', '&amp;amp;': '&amp;', '&amp;quot;': '"', '&amp;#39;': "'"}
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

### Riga 427 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 32 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     425: # ============================================================
     426: 
 >>> 427: def parse_junit_xml():
     428:     """Parsa il file junit.xml e estrae i dettagli dei test falliti."""
     429:     global test_failures_details
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

### Riga 487 🟡 🟢
**Problema:** Remove the unused local variable "skipped".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     485:                 failure = testcase.find('failure')
     486:                 error = testcase.find('error')
 >>> 487:                 skipped = testcase.find('skipped')
     488:                 
     489:                 if failure is not None or error is not None:
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

### Riga 565 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     563:             }
     564:             return rules_cache[rule_key]
 >>> 565:     except:
     566:         pass
     567:     
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

### Riga 589 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     587:             source_cache[cache_key] = '\n'.join(lines)
     588:             return source_cache[cache_key]
 >>> 589:     except:
     590:         pass
     591:     return None
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

### Riga 605 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     603:             for m in data.get('component', {}).get('measures', []):
     604:                 test_metrics[m.get('metric')] = m.get('value')
 >>> 605:     except:
     606:         pass
     607:     return test_metrics
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

### Riga 621 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     619:             for m in data.get('component', {}).get('measures', []):
     620:                 coverage_metrics[m.get('metric')] = m.get('value')
 >>> 621:     except:
     622:         pass
     623:     return coverage_metrics
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

### Riga 633 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     631:         if data:
     632:             quality_gate = data.get('projectStatus', {})
 >>> 633:     except:
     634:         pass
     635:     return quality_gate
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

### Riga 651 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     649: 
     650: 
 >>> 651: def fetch_all_issues():
     652:     """Recupera tutti gli issues."""
     653:     all_issues = []
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

### Riga 654 🔴 🟢
**Problema:** Replace with dict fromkeys method call
**Regola:** `python:S7519` - Populating a dictionary with a constant value should be done with dict.fromkeys() method call

```python
     652:     """Recupera tutti gli issues."""
     653:     all_issues = []
 >>> 654:     issues_count = {q: 0 for q in SOFTWARE_QUALITIES}
     655:     
     656:     for quality in SOFTWARE_QUALITIES:
```

**❓ Perché è un problema:**
Using a dictionary comprehension to build a dictionary where every key maps to the exact same constant value e.g., {k: 1 for k in
keys} is less efficient and less idiomatic than using the `dict.fromkeys()` class method. `dict.fromkeys()` is
specifically designed for this use case and offers better performance, especially for large iterables, as it avoids the overhead of creating and
processing individual key-value pairs in a comprehension.

**✅ Come risolvere:**
Rewrite the dictionary comprehension `{x: constant for x in iterable}` as `dict.fromkeys(iterable, constant)`. If the
constant value is `None`, you can omit the value argument in `dict.fromkeys()`, as it defaults to `None`.

### Noncompliant code example

```
keys = ['a', 'b', 'c']

dict_comp_one = {k: 1 for k in keys} # Noncompliant
```

### Compliant solution

```
keys = ['a', 'b', 'c']

dict_fromkeys_one = dict.fromkeys(keys, 1)
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [dict.fromkeys](https://docs.python.org/3/library/stdtypes.html#dict.fromkeys)

---

### Riga 700 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     698:     """Recupera Security Hotspots."""
     699:     all_hotspots = []
 >>> 700:     print(f"\n   Estrazione Security Hotspots...")
     701:     page = 1
     702:     
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

### Riga 751 🟡 🔴
**Problema:** Specify an exception class to catch or reraise the exception
**Regola:** `python:S5754` - "SystemExit" should be re-raised

```python
     749:                 if line and component:
     750:                     hotspot['source_code'] = get_source_lines(component, line, line, context=3)
 >>> 751:         except:
     752:             pass
     753:         
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

### Riga 763 🟡 🟢
**Problema:** Replace set constructor call with a set comprehension.
**Regola:** `python:S7494` - Comprehensions should be used instead of constructors around generator expressions

```python
     761: def fetch_rules(issues):
     762:     """Recupera regole."""
 >>> 763:     unique_rules = set(i.get('rule', '') for i in issues if i.get('rule'))
     764:     if not unique_rules:
     765:         return
```

**❓ Perché è un problema:**
Using `list()`, `set()`, or `dict()` around a generator expression is redundant when a corresponding comprehension
can directly express the same operation. Comprehensions are clearer, more concise, and often more readable than the equivalent constructor/generator
expression combination.

This principle applies to all three built-in collection types: `list`, `set`, and `dict`:

  -  Use `[f(x) for x in foo]` instead of `list(f(x) for x in foo)` 

  -  Use `{f(x) for x in foo}` instead of `set(f(x) for x in foo)` 

  -  Use `{k: v for k, v in items}` instead of `dict((k, v) for k, v in items)` 

### Exceptions

If the generator expression doesn’t filter or modify the collection, the rule does not raise. For example, `list(x for x in foo)` is
simply copying the iterable `foo` into a list, whi

**✅ Come risolvere:**
Replace the collection constructor with the appropriate comprehension syntax.

### Noncompliant code example

```
def f(x):
    return x * 2

list(f(x) for x in range(5))  # Noncompliant
```

### Compliant solution

```
def f(x):
    return x * 2

[f(x) for x in range(5)] # Compliant
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) 

  -  Python Documentation - [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) 

  -  Python Documentation - [Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)

---

### Riga 890 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     888: # ============================================================
     889: 
 >>> 890: def generate_test_failures_file(junit_summary, test_analysis, timestamp):
     891:     """Genera file JULES_TEST_FAILURES con tutti i dettagli."""
     892:     if not test_failures_details:
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

### Riga 906 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "| Metrica | Valore |" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     904:     md.append("## 📊 Statistiche Test")
     905:     md.append("")
 >>> 906:     md.append("| Metrica | Valore |")
     907:     md.append("|---------|--------|")
     908:     md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
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

### Riga 907 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "|---------|--------|" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     905:     md.append("")
     906:     md.append("| Metrica | Valore |")
 >>> 907:     md.append("|---------|--------|")
     908:     md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
     909:     md.append(f"| ✅ Passati | {junit_summary.get('passed', 0)} |")
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

### Riga 976 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     974:             md.append("**❌ Messaggio di Errore:**")
     975:             md.append("")
 >>> 976:             md.append(f"```")
     977:             md.append(message[:500] if message else "Nessun messaggio")
     978:             md.append("```")
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

### Riga 1006 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "**✅ Come risolvere:**" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     1004:             
     1005:             # Come risolvere
 >>> 1006:             md.append("**✅ Come risolvere:**")
     1007:             md.append("")
     1008:             md.append(error_info.get('how_to_fix', 'Analizza lo stack trace per identificare il problema'))
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

### Riga 1013 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "**📚 Risorse:**" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     1011:             # Risorse
     1012:             if error_info.get('resources'):
 >>> 1013:                 md.append("**📚 Risorse:**")
     1014:                 md.append("")
     1015:                 for resource in error_info.get('resources', []):
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

### Riga 1030 🟡 🟡
**Problema:** Remove the unused function parameter "junit_summary".
**Regola:** `python:S1172` - Unused function parameters should be removed

```python
     1028: 
     1029: 
 >>> 1030: def generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis):
     1031:     """Genera prompt dinamici."""
     1032:     prompts = {}
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

### Riga 1030 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 25 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1028: 
     1029: 
 >>> 1030: def generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis):
     1031:     """Genera prompt dinamici."""
     1032:     prompts = {}
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

### Riga 1089 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1087:             prompts['test_failures'] += f"- {info['emoji']} **{error_type}** ({count}x)\n"
     1088:         
 >>> 1089:         prompts['test_failures'] += f"""
 >>> 1090: ## Strategia di fix
 >>> 1091: 
 >>> 1092: ### Per AssertionError:
 >>> 1093: 1. Verifica se il test o il codice è sbagliato
 >>> 1094: 2. Se il comportamento è cambiato, aggiorna il test
 >>> 1095: 3. Se il test è corretto, correggi il codice
 >>> 1096: 
 >>> 1097: ### Per errori di tipo (TypeError, AttributeError, KeyError):
 >>> 1098: 1. Controlla i tipi dei dati
 >>> 1099: 2. Aggiungi controlli null/None
 >>> 1100: 3. Verifica che i mock siano configurati correttamente
 >>> 1101: 
 >>> 1102: ### Per errori di connessione/file:
 >>> 1103: 1. Mocka le dipendenze esterne
 >>> 1104: 2. Usa fixtures per dati di test
 >>> 1105: 3. Non dipendere da risorse esterne
 >>> 1106: 
 >>> 1107: ## File da modificare
 >>> 1108: """
     1109:         if test_analysis:
     1110:             for filepath in list(test_analysis['by_file'].keys())[:10]:
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

### Riga 1169 🟡 🟢
**Problema:** Remove the unused local variable "qi".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     1167:             continue
     1168:         
 >>> 1169:         qi = [i for i in issues if i.get('software_quality') == quality]
     1170:         effort = format_duration(analysis['effort_by_quality'].get(quality, 0))
     1171:         emoji = get_quality_emoji(quality)
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

### Riga 1197 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 44 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1195: 
     1196: 
 >>> 1197: def generate_summary(issues, analysis, issues_count, hotspots, hotspot_analysis, 
     1198:                      junit_summary, test_analysis, timestamp, generated_files):
     1199:     """Genera SUMMARY."""
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

### Riga 1207 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1205:     md.append(f"**Progetto:** {PROJECT_KEY}")
     1206:     md.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
 >>> 1207:     md.append(f"**Versione:** SonarCloud Exporter v5.0")
     1208:     md.append(f"**Filtro issues:** {ISSUE_STATUSES}")
     1209:     md.append("")
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

### Riga 1393 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1391: 
     1392: 
 >>> 1393: def generate_hotspots_file(hotspots, hotspot_analysis, timestamp):
     1394:     """Genera file hotspots."""
     1395:     if not hotspots:
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

### Riga 1454 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1452: 
     1453: 
 >>> 1454: def generate_quality_specific_file(issues, quality, output_file):
     1455:     """Genera file per quality specifica."""
     1456:     qi = [i for i in issues if i.get('software_quality') == quality]
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

### Riga 1539 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1537: 
     1538: 
 >>> 1539: def generate_ultra_complete(issues, output_file):
     1540:     """Genera file ultra-completo."""
     1541:     by_file = group_by_file(issues)
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

### Riga 1598 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 36 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1596: # ============================================================
     1597: 
 >>> 1598: def main():
     1599:     stats['start_time'] = datetime.now()
     1600:     
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

### Riga 1649 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1647:         test_analysis = analyze_test_failures()
     1648:     else:
 >>> 1649:         print(f"   ○ junit.xml non trovato")
     1650:         print(f"      Per abilitare: pytest --junitxml=junit.xml")
     1651:     
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

### Riga 1650 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1648:     else:
     1649:         print(f"   ○ junit.xml non trovato")
 >>> 1650:         print(f"      Per abilitare: pytest --junitxml=junit.xml")
     1651:     
     1652:     if test_metrics:
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

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 76 🔴 🟡
**Problema:** Either remove this useless object instantiation of "globalContext.QWebChannel" or use it.
**Regola:** `javascript:S1848` - Objects should not be created to be dropped immediately without being used

```jsx
     74:     if (globalContext.qt?.webChannelTransport) {
     75:       // Assign to a variable to prevent object from being dropped immediately
 >>> 76:       new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     77:         if (c.objects?.bridge) {
     78:             setBridge(c.objects.bridge);
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
