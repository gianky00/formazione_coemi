# 🔧 SonarCloud ULTRA-COMPLETE Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-07 22:13
**Totale issues:** 150
**Tempo stimato totale:** 2g 6h 13min

## Istruzioni per Jules

Questo documento contiene **TUTTE** le informazioni per correggere ogni issue:
- 📍 **Posizione esatta** (file + riga + colonne)
- 💻 **Codice attuale** (snippet con contesto)
- ❓ **Perché è un problema** (root cause)
- ✅ **Come risolverlo** (con esempi di codice)
- 📚 **Risorse** (link documentazione)

## Statistiche

| Categoria | Issues | Tempo | Descrizione |
|-----------|--------|-------|-------------|
| 🟡 MAINTAINABILITY | 150 | 2g 6h 13min | Code smell che rendono il codice difficile da mantenere |

## Priorità

1. 🟣 **SECURITY** - Vulnerabilità (rischio sicurezza)
2. 🔴 **RELIABILITY** - Bug (crash/errori)
3. 🟡 **MAINTAINABILITY** - Code smell

---

## 📄 `desktop_app/components/neural_3d.py`
**12 issue(s)** | Effort: 1h 2min

### Riga 15 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 23-37 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     13:         # Position X, Y, Z centered at 0,0,0
     14:         # Range approx -800 to 800
 >>> 15:         self.points = (np.random.rand(num_nodes, 3) - 0.5) * 1600
     16: 
     17:         # Velocity vector (slow drift)
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 18 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 27-41 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     16: 
     17:         # Velocity vector (slow drift)
 >>> 18:         self.velocities = (np.random.rand(num_nodes, 3) - 0.5) * 1.5
     19: 
     20:         # Phase for "breathing" effect (0 to 2pi)
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 21 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 22-36 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     19: 
     20:         # Phase for "breathing" effect (0 to 2pi)
 >>> 21:         self.phases = np.random.rand(num_nodes) * 2 * math.pi
     22:         self.phase_speeds = np.random.rand(num_nodes) * 0.05 + 0.02
     23: 
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 22 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 28-42 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     20:         # Phase for "breathing" effect (0 to 2pi)
     21:         self.phases = np.random.rand(num_nodes) * 2 * math.pi
 >>> 22:         self.phase_speeds = np.random.rand(num_nodes) * 0.05 + 0.02
     23: 
     24:         # Current Rotation (Euler angles)
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 80 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 23-37 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     78:         self.warp_speed = 0.0
     79:         # Reset positions to ensure we aren't stuck in a "tunnel"
 >>> 80:         self.points = (np.random.rand(self.num_nodes, 3) - 0.5) * 1600
     81:         self.velocities = (np.random.rand(self.num_nodes, 3) - 0.5) * 1.5
     82: 
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 81 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 27-41 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     79:         # Reset positions to ensure we aren't stuck in a "tunnel"
     80:         self.points = (np.random.rand(self.num_nodes, 3) - 0.5) * 1600
 >>> 81:         self.velocities = (np.random.rand(self.num_nodes, 3) - 0.5) * 1.5
     82: 
     83:     def start_warp(self):
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 112 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 48-62 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     110:                  self.points[mask_behind, 2] = 1600
     111:                  # Randomize X/Y for infinite tunnel effect
 >>> 112:                  self.points[mask_behind, 0] = (np.random.rand(respawn_count) - 0.5) * 2000
     113:                  self.points[mask_behind, 1] = (np.random.rand(respawn_count) - 0.5) * 2000
     114: 
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 113 🟡 🟡 MAJOR

**🎯 Problema:** Use a "numpy.random.Generator" here instead of this legacy function.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6711` - numpy.random.Generator should be preferred to numpy.random.RandomState |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 48-62 |
| Tags | data-science, numpy |

**💻 Codice attuale:**
```python
     111:                  # Randomize X/Y for infinite tunnel effect
     112:                  self.points[mask_behind, 0] = (np.random.rand(respawn_count) - 0.5) * 2000
 >>> 113:                  self.points[mask_behind, 1] = (np.random.rand(respawn_count) - 0.5) * 2000
     114: 
     115:              # Also slightly drift rotation to center
```

**❓ Perché è un problema:**

Using a predictable seed is a common best practice when using NumPy to create reproducible results. To that end, using
`np.random.seed(number)` to set the seed of the global `numpy.random.RandomState` has been the privileged solution for a long
time.

`numpy.random.RandomState` and its associated methods rely on a global state, which may be problematic when threads or other forms of
concurrency are involved. The global state may be altered and the global seed may be reset at various points in the program (for instance, through an
imported package or script), which would lead to irreproducible results.

Instead, the preferred best practice to generate reproducible pseudorandom numbers is to instantiate a `numpy.random.Generator` object
with a seed and reuse it in different parts of the code. This avoids the reliance on a global state. Whenever a new seed is needed, a new generator
may be created instead of mutating a global state.

Below is the list of legacy functions and their alterna...

**✅ Come risolvere:**

To fix this issue, replace usages of `numpy.random.RandomState` to `numpy.random.Generator`.

##### Noncompliant code example

```
import numpy as np
np.random.seed(42)
x = np.random.randn() # Noncompliant: this relies on numpy.random.RandomState, which is deprecated
```

##### Compliant solution

```
import numpy as np
generator = np.random.default_rng(42)
x = generator.standard_normal()
```

**📚 Risorse:**

#### Documentation

 - NumPy Documentation - [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html#random-generator) 

 - NumPy Documentation - [Legacy Random Generation](https://numpy.org/doc/stable/reference/random/legacy.html#legacy-random-generation)
 

 - NumPy Documentation - [NEP19 RNG Policy](https://numpy.org/neps/nep-0019-rng-policy.html)

---

### Riga 151 🟡 🟡 MAJOR

**🎯 Problema:** Remove this commented out code.

| Campo | Valore |
|-------|--------|
| Regola | `python:S125` - Sections of code should not be commented out |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 25-44 |
| Tags | unused |

**💻 Codice attuale:**
```python
     149:         active_pulses = []
     150:         for p in self.pulses:
 >>> 151:             p[2] += p[3] # Progress += Speed
     152:             if p[2] &lt; 1.0:
     153:                 active_pulses.append(p)
```

**❓ Perché è un problema:**

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

**📝 Descrizione:**

### Why is this an issue?

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

### Riga 166 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 8-26 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     164: 
     165: 
 >>> 166:     def project_and_render(self, painter, width, height):
     167:         """
     168:         Projects 3D points to 2D and renders everything.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 207 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "coords_2d".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-17 |
| Tags | unused |

**💻 Codice attuale:**
```python
     205:         # Store 2D coords for connection drawing
     206:         # Shape (N, 2)
 >>> 207:         coords_2d = np.column_stack((x_2d, y_2d))
     208: 
     209:         # --- 3. Draw Connections &amp; Pulses ---
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

### Riga 244 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "pulse_color".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-19 |
| Tags | unused |

**💻 Codice attuale:**
```python
     242:         # Draw Pulses
     243:         painter.setPen(Qt.PenStyle.NoPen) # No outline
 >>> 244:         pulse_color = QColor(255, 255, 255) # White core
     245: 
     246:         for p in self.pulses:
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `desktop_app/views/scadenzario_view.py`
**10 issue(s)** | Effort: 1h 2min

### Riga 199 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "dd/MM/yyyy" 6 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 12min |
| Posizione | Colonne 55-67 |
| Tags | design |

**💻 Codice attuale:**
```python
     197:                 date_str = item.get('data_scadenza')
     198:                 if date_str:
 >>> 199:                     qdate = QDate.fromString(date_str, "dd/MM/yyyy")
     200:                     # Rilassiamo il controllo per permettere ai dati di test di passare se necessario,
     201:                     # ma manteniamo la logica principale. Se qdate non è valido, non entra.
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 216 🟡 🟢 MINOR

**🎯 Problema:** Remove this redundant call.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7508` - Redundant collection functions should be avoided |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 35-39 |

**💻 Codice attuale:**
```python
     214:     def _assign_category_colors(self):
     215:         self.category_colors = {}
 >>> 216:         unique_categories = sorted(list(set(cert['categoria'] for cert in self.certificates)))
     217:         for i, category in enumerate(unique_categories):
     218:             self.category_colors[category] = self.color_palette[i % len(self.color_palette)]
```

**❓ Perché è un problema:**

Python’s built-in functions for processing iterables such as `list()`, `tuple()`, `set()`, `sorted()`,
and `reversed()` are designed to accept any iterable as input. When these functions are unnecessarily nested within each other, it creates
redundant operations that add unnecessary computational overhead by creating intermediate data structures, decrease code readability and make the
intention less clear, and waste memory by duplicating data structures temporarily.

**✅ Come risolvere:**

When the outer function is given a collection but could have been given an iterable, the unnecessary conversion should be removed. For example, in
`sorted(list(iterable))`, the outer `sorted()` function can accept an iterable directly, so the inner `list()` call
is redundant and should be removed.

When the function `sorted()` is wrapped with `list()`, remove this conversion operation, since `sorted()` already
returns a list.

##### Noncompliant code example

```
iterable = (3, 1, 4, 1)

sorted_of_list = list(sorted(iterable)) # Noncompliant
```

##### Compliant solution

```
iterable = (3, 1, 4, 1)

sorted_of_list = sorted(iterable)
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [list](https://docs.python.org/3/library/stdtypes.html#list) 

 - Python Documentation - [tuple](https://docs.python.org/3/library/stdtypes.html#tuple) 

 - Python Documentation - [set](https://docs.python.org/3/library/stdtypes.html#set) 

 - Python Documentation - [sorted](https://docs.python.org/3/library/functions.html#sorted) 

 - Python Documentation - [reversed](https://docs.python.org/3/library/functions.html#reversed)

---

### Riga 216 🟡 🟢 MINOR

**🎯 Problema:** Replace set constructor call with a set comprehension.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7494` - Comprehensions should be used instead of constructors around generator expressions |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 40-43 |

**💻 Codice attuale:**
```python
     214:     def _assign_category_colors(self):
     215:         self.category_colors = {}
 >>> 216:         unique_categories = sorted(list(set(cert['categoria'] for cert in self.certificates)))
     217:         for i, category in enumerate(unique_categories):
     218:             self.category_colors[category] = self.color_palette[i % len(self.color_palette)]
```

**❓ Perché è un problema:**

Using `list()`, `set()`, or `dict()` around a generator expression is redundant when a corresponding comprehension
can directly express the same operation. Comprehensions are clearer, more concise, and often more readable than the equivalent constructor/generator
expression combination.

This principle applies to all three built-in collection types: `list`, `set`, and `dict`:

 - Use `[f(x) for x in foo]` instead of `list(f(x) for x in foo)` 

 - Use `{f(x) for x in foo}` instead of `set(f(x) for x in foo)` 

 - Use `{k: v for k, v in items}` instead of `dict((k, v) for k, v in items)` 

#### Exceptions

If the generator expression doesn’t filter or modify the collection, the rule does not raise. For example, `list(x for x in foo)` is
simply copying the iterable `foo` into a list, which is equivalent to `list(foo)` and covered by a different rule.

**✅ Come risolvere:**

Replace the collection constructor with the appropriate comprehension syntax.

##### Noncompliant code example

```
def f(x):
 return x * 2

list(f(x) for x in range(5)) # Noncompliant
```

##### Compliant solution

```
def f(x):
 return x * 2

[f(x) for x in range(5)] # Compliant
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) 

 - Python Documentation - [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) 

 - Python Documentation - [Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)

---

### Riga 232 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "IN SCADENZA" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 73-86 |
| Tags | design |

**💻 Codice attuale:**
```python
     230:                 parsed_date = QDate.fromString(item.get('data_scadenza', ''), "dd/MM/yyyy")
     231:             
 >>> 232:             status = "SCADUTI" if QDate.currentDate() &gt; parsed_date else "IN SCADENZA"
     233:             data_by_category[item['categoria']][status].append(item)
     234: 
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 248 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 13min |
| Posizione | Colonne 8-26 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     246:         self.employee_tree.setUpdatesEnabled(True)
     247: 
 >>> 248:     def redraw_gantt_scene(self):
     249:         # Bug 5 Fix: Disable updates for smooth rendering
     250:         self.gantt_view.setUpdatesEnabled(False)
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 381 🟡 🟢 MINOR

**🎯 Problema:** Remove this redundant call.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7508` - Redundant collection functions should be avoided |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 36-40 |

**💻 Codice attuale:**
```python
     379:             if item.widget(): item.widget().deleteLater()
     380: 
 >>> 381:         visible_categories = sorted(list(set(cert['categoria'] for cert in visible_certs)))
     382:         for category in visible_categories:
     383:             color = self.category_colors.get(category)
```

**❓ Perché è un problema:**

Python’s built-in functions for processing iterables such as `list()`, `tuple()`, `set()`, `sorted()`,
and `reversed()` are designed to accept any iterable as input. When these functions are unnecessarily nested within each other, it creates
redundant operations that add unnecessary computational overhead by creating intermediate data structures, decrease code readability and make the
intention less clear, and waste memory by duplicating data structures temporarily.

**✅ Come risolvere:**

When the outer function is given a collection but could have been given an iterable, the unnecessary conversion should be removed. For example, in
`sorted(list(iterable))`, the outer `sorted()` function can accept an iterable directly, so the inner `list()` call
is redundant and should be removed.

When the function `sorted()` is wrapped with `list()`, remove this conversion operation, since `sorted()` already
returns a list.

##### Noncompliant code example

```
iterable = (3, 1, 4, 1)

sorted_of_list = list(sorted(iterable)) # Noncompliant
```

##### Compliant solution

```
iterable = (3, 1, 4, 1)

sorted_of_list = sorted(iterable)
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [list](https://docs.python.org/3/library/stdtypes.html#list) 

 - Python Documentation - [tuple](https://docs.python.org/3/library/stdtypes.html#tuple) 

 - Python Documentation - [set](https://docs.python.org/3/library/stdtypes.html#set) 

 - Python Documentation - [sorted](https://docs.python.org/3/library/functions.html#sorted) 

 - Python Documentation - [reversed](https://docs.python.org/3/library/functions.html#reversed)

---

### Riga 381 🟡 🟢 MINOR

**🎯 Problema:** Replace set constructor call with a set comprehension.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7494` - Comprehensions should be used instead of constructors around generator expressions |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 41-44 |

**💻 Codice attuale:**
```python
     379:             if item.widget(): item.widget().deleteLater()
     380: 
 >>> 381:         visible_categories = sorted(list(set(cert['categoria'] for cert in visible_certs)))
     382:         for category in visible_categories:
     383:             color = self.category_colors.get(category)
```

**❓ Perché è un problema:**

Using `list()`, `set()`, or `dict()` around a generator expression is redundant when a corresponding comprehension
can directly express the same operation. Comprehensions are clearer, more concise, and often more readable than the equivalent constructor/generator
expression combination.

This principle applies to all three built-in collection types: `list`, `set`, and `dict`:

 - Use `[f(x) for x in foo]` instead of `list(f(x) for x in foo)` 

 - Use `{f(x) for x in foo}` instead of `set(f(x) for x in foo)` 

 - Use `{k: v for k, v in items}` instead of `dict((k, v) for k, v in items)` 

#### Exceptions

If the generator expression doesn’t filter or modify the collection, the rule does not raise. For example, `list(x for x in foo)` is
simply copying the iterable `foo` into a list, which is equivalent to `list(foo)` and covered by a different rule.

**✅ Come risolvere:**

Replace the collection constructor with the appropriate comprehension syntax.

##### Noncompliant code example

```
def f(x):
 return x * 2

list(f(x) for x in range(5)) # Noncompliant
```

##### Compliant solution

```
def f(x):
 return x * 2

[f(x) for x in range(5)] # Compliant
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) 

 - Python Documentation - [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) 

 - Python Documentation - [Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)

---

### Riga 465 🟡 🟡 MAJOR

**🎯 Problema:** Add replacement fields or use a normal string instead of an f-string.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3457` - String formatting should be used correctly |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 62-95 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     463:                 with open(path, 'wb') as f:
     464:                     f.write(response.content)
 >>> 465:                 ToastManager.success("Esportazione Riuscita", f"Report esportato con successo.", self.window())
     466:             except Exception as e:
     467:                 CustomMessageDialog.show_error(self, "Errore", f"Impossibile salvare il file: {e}")
```

**❓ Perché è un problema:**

A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are invalid.

Formatted string literals (also called "f-strings"; available since Python 3.6) are generally simpler to use, and any syntax mistake will cause a
failure at compile time. However, it is easy to...

**✅ Come risolvere:**

A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

##### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"} # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile") # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]" # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice") # Noncompliant. Add 1 missing argument.
```

##### Compliant solution

```
"Error %(message)s" % {"message": "something failed"}

"Error: User {} has not been able to access {}".format("Alice", "MyFile")

user = "Alice"
resource = "MyFile"
message = f"Error: User {user} has not been able to access {resource}"

import logging
logging.error("Error: User %s has not been able to access %s", "Alice", "MyFile")
```

**📚 Risorse:**

- [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

 - Python documentation - printf-style String
 Formatting 

 - [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

 - Python
 documentation - Using particular formatting styles throughout your application 

 - Python documentation - Formatted string
 literals

---

### Riga 472 🟡 🟢 MINOR

**🎯 Problema:** Replace the unused local variable "tb" with "_".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 24-26 |
| Tags | unused |

**💻 Codice attuale:**
```python
     470: 
     471:     def _on_generic_error(self, error_tuple, title):
 >>> 472:         exctype, value, tb = error_tuple
     473:         CustomMessageDialog.show_error(self, title, f"{value}")
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

### Riga 472 🟡 🟢 MINOR

**🎯 Problema:** Replace the unused local variable "exctype" with "_".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-15 |
| Tags | unused |

**💻 Codice attuale:**
```python
     470: 
     471:     def _on_generic_error(self, error_tuple, title):
 >>> 472:         exctype, value, tb = error_tuple
     473:         CustomMessageDialog.show_error(self, title, f"{value}")
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `app/api/main.py`
**8 issue(s)** | Effort: 2h 52min

### Riga 37 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 4-24 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 92 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 16min |
| Posizione | Colonne 10-20 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 145 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 4-19 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 190 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Certificato non trovato" 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 52-77 |
| Tags | design |

**💻 Codice attuale:**
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

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 241 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 16min |
| Posizione | Colonne 4-22 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 382 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 77 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 1h7min |
| Posizione | Colonne 4-22 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 602 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 57 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 47min |
| Posizione | Colonne 10-31 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 749 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Dipendente non trovato" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 52-76 |
| Tags | design |

**💻 Codice attuale:**
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

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

## 📄 `desktop_app/main.py`
**7 issue(s)** | Effort: 36min

### Riga 482 🟡 🟢 MINOR

**🎯 Problema:** Remove this unneeded "pass".

| Campo | Valore |
|-------|--------|
| Regola | `python:S2772` - "pass" should not be used needlessly |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 8-12 |
| Tags | confusing |

**💻 Codice attuale:**
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

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

**📝 Descrizione:**

This rule raises an issue when a `pass` statement is redundant.

### Why is this an issue?

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

#### Code examples

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

### Resources

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 494 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
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
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 503 🟡 🟢 MINOR

**🎯 Problema:** Remove this unneeded "pass".

| Campo | Valore |
|-------|--------|
| Regola | `python:S2772` - "pass" should not be used needlessly |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 12-16 |
| Tags | confusing |

**💻 Codice attuale:**
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

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

**📝 Descrizione:**

This rule raises an issue when a `pass` statement is redundant.

### Why is this an issue?

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

#### Code examples

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

### Resources

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 539 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Sola Lettura" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 65-79 |
| Tags | design |

**💻 Codice attuale:**
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

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 573 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 14min |
| Posizione | Colonne 8-24 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 591 🟡 🟢 MINOR

**🎯 Problema:** Remove this unneeded "pass".

| Campo | Valore |
|-------|--------|
| Regola | `python:S2772` - "pass" should not be used needlessly |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 12-16 |
| Tags | confusing |

**💻 Codice attuale:**
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

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

**📝 Descrizione:**

This rule raises an issue when a `pass` statement is redundant.

### Why is this an issue?

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

#### Code examples

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

### Resources

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 641 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "pending_count".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-21 |
| Tags | unused |

**💻 Codice attuale:**
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

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `admin/offusca/build_dist.py`
**7 issue(s)** | Effort: 1h 24min

### Riga 84 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 39 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 29min |
| Posizione | Colonne 4-16 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     82:     return libs
     83: 
 >>> 84: def scan_imports(source_dirs):
     85:     log_and_print("--- Scanning source code for imports ---")
     86:     detected_imports = set()
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 108 🟡 🟡 MAJOR

**🎯 Problema:** Merge this if statement with the enclosing one.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1066` - Mergeable "if" statements should be combined |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 20-22 |
| Tags | clumsy |

**💻 Codice attuale:**
```python
     106:                         if root_pkg not in std_libs: detected_imports.add(root_pkg)
     107:                 elif isinstance(node, ast.ImportFrom):
 >>> 108:                     if node.module:
     109:                         root_pkg = node.module.split('.')[0]
     110:                         if root_pkg not in std_libs: detected_imports.add(root_pkg)
```

**❓ Perché è un problema:**

Nested code - blocks of code inside blocks of code - is eventually necessary, but increases complexity. This is why keeping the code as flat as
possible, by avoiding unnecessary nesting, is considered a good practice.

Merging `if` statements when possible will decrease the nesting of the code and improve its readability.

Code like

```
if condition1:
 if condition2: # Noncompliant
 # ...
```

Will be more readable as

```
if condition1 and condition2: # Compliant
 # ...
```

**✅ Come risolvere:**

If merging the conditions seems to result in a more complex code, extracting the condition or part of it in a named function or variable is a
better approach to fix readability.

##### Noncompliant code example

```
if file.isValid():
 if file.isfile() or file.isdir(): # Noncompliant
 # ...
```

##### Compliant solution

```
def isFileOrDirectory(File file):
 return file.isFile() or file.isDirectory()

if file.isValid() and isFileOrDirectory(file): # Compliant
 # ...
```

---

### Riga 111 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     109:                         root_pkg = node.module.split('.')[0]
     110:                         if root_pkg not in std_libs: detected_imports.add(root_pkg)
 >>> 111:         except: pass
     112: 
     113:     detected_imports.discard("app")
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 118 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 9min |
| Posizione | Colonne 4-22 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     116:     return list(detected_imports)
     117: 
 >>> 118: def verify_environment():
     119:     log_and_print("--- Step 1/7: Environment Diagnostics ---")
     120:     log_and_print(f"Running with Python: {sys.executable}")
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 134 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "requirements.txt" 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 38-56 |
| Tags | design |

**💻 Codice attuale:**
```python
     132:         sys.exit(1)
     133: 
 >>> 134:     req_path = os.path.join(ROOT_DIR, "requirements.txt")
     135:     if os.path.exists(req_path):
     136:         log_and_print(f"Checking dependencies from {req_path}...")
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 180 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 37 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 27min |
| Posizione | Colonne 4-9 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     178:     return modules
     179: 
 >>> 180: def build():
     181:     try:
     182:         log_and_print("Starting Build Process...")
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 392 🟡 🟡 MAJOR

**🎯 Problema:** Add replacement fields or use a normal string instead of an f-string.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3457` - String formatting should be used correctly |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 17-40 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     390:                  iscc_exe,
     391:                  f"/dBuildDir={build_dir_abs}",
 >>> 392:                  f"/dMyAppVersion=1.0.0",
     393:                  "setup_script.iss"
     394:              ]
```

**❓ Perché è un problema:**

A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are invalid.

Formatted string literals (also called "f-strings"; available since Python 3.6) are generally simpler to use, and any syntax mistake will cause a
failure at compile time. However, it is easy to...

**✅ Come risolvere:**

A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

##### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"} # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile") # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]" # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice") # Noncompliant. Add 1 missing argument.
```

##### Compliant solution

```
"Error %(message)s" % {"message": "something failed"}

"Error: User {} has not been able to access {}".format("Alice", "MyFile")

user = "Alice"
resource = "MyFile"
message = f"Error: User {user} has not been able to access {resource}"

import logging
logging.error("Error: User %s has not been able to access %s", "Alice", "MyFile")
```

**📚 Risorse:**

- [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

 - Python documentation - printf-style String
 Formatting 

 - [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

 - Python
 documentation - Using particular formatting styles throughout your application 

 - Python documentation - Formatted string
 literals

---

## 📄 `desktop_app/views/config_view.py`
**6 issue(s)** | Effort: 44min

### Riga 228 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 8-17 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     226:         return int(self.table.item(rows[0].row(), 0).text())
     227: 
 >>> 228:     def edit_user(self):
     229:         user_id = self.get_selected_user_id()
     230:         if not user_id: return
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 252 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 8-27 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 275 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     273:                     else:
     274:                         CustomMessageDialog.show_error(self, "Errore", str(e))
 >>> 275:                 except:
     276:                     CustomMessageDialog.show_error(self, "Errore", str(e))
     277: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 344 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Ottimizza Database Ora" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 40-64 |
| Tags | design |

**💻 Codice attuale:**
```python
     342:         self.form_layout.addRow(maint_separator)
     343: 
 >>> 344:         self.optimize_btn = QPushButton("Ottimizza Database Ora")
     345:         self.optimize_btn.setToolTip("Esegue VACUUM e ANALYZE per recuperare spazio e migliorare le prestazioni.")
     346:         self.optimize_btn.clicked.connect(self.optimize_db)
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 635 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     633:                     dt = datetime.fromisoformat(ts_str)
     634:                     formatted_date = dt.strftime("%d/%m/%Y %H:%M:%S")
 >>> 635:                 except:
     636:                     formatted_date = ts_str
     637: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 958 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 25 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 15min |
| Posizione | Colonne 8-19 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     956:                 CustomMessageDialog.show_error(self, "Errore", f"Impossibile importare: {e}")
     957: 
 >>> 958:     def save_config(self):
     959:         if getattr(self, 'is_read_only', False):
     960:             return
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/utils.py`
**6 issue(s)** | Effort: 30min

### Riga 95 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     93:     """
     94:     # 1. Always replace acute accents on a, i, u (Phonetic stress markers)
 >>> 95:     text = re.sub(r'[á]', 'a', text)
     96:     text = re.sub(r'[í]', 'i', text)
     97:     text = re.sub(r'[ú]', 'u', text)
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

### Riga 96 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     94:     # 1. Always replace acute accents on a, i, u (Phonetic stress markers)
     95:     text = re.sub(r'[á]', 'a', text)
 >>> 96:     text = re.sub(r'[í]', 'i', text)
     97:     text = re.sub(r'[ú]', 'u', text)
     98: 
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

### Riga 97 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     95:     text = re.sub(r'[á]', 'a', text)
     96:     text = re.sub(r'[í]', 'i', text)
 >>> 97:     text = re.sub(r'[ú]', 'u', text)
     98: 
     99:     # Regex lookahead (?=[^\W_]) ensures the character is followed by a word character
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

### Riga 107 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     105: 
     106:     # 3. Also clean other accents inside words if used for stress (e.g. càsa)
 >>> 107:     text = re.sub(r'[à](?=[^\W_])', 'a', text)
     108:     text = re.sub(r'[ì](?=[^\W_])', 'i', text)
     109:     text = re.sub(r'[ù](?=[^\W_])', 'u', text)
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

### Riga 108 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     106:     # 3. Also clean other accents inside words if used for stress (e.g. càsa)
     107:     text = re.sub(r'[à](?=[^\W_])', 'a', text)
 >>> 108:     text = re.sub(r'[ì](?=[^\W_])', 'i', text)
     109:     text = re.sub(r'[ù](?=[^\W_])', 'u', text)
     110: 
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

### Riga 109 🟡 🟡 MAJOR

**🎯 Problema:** Replace this character class by the character itself.

| Campo | Valore |
|-------|--------|
| Regola | `python:S6397` - Character classes in regular expressions should not contain only one character |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-22 |
| Tags | regex |

**💻 Codice attuale:**
```python
     107:     text = re.sub(r'[à](?=[^\W_])', 'a', text)
     108:     text = re.sub(r'[ì](?=[^\W_])', 'i', text)
 >>> 109:     text = re.sub(r'[ù](?=[^\W_])', 'u', text)
     110: 
     111:     return text
```

**❓ Perché è un problema:**

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

**📝 Descrizione:**

### Why is this an issue?

Character classes in regular expressions are a convenient way to match one of several possible characters by listing the allowed characters or
ranges of characters. If a character class contains only one character, the effect is the same as just writing the character without a character
class.

Thus, having only one character in a character class is usually a simple oversight that remained after removing other characters of the class.

#### Noncompliant code example

```
r"a[b]c"
```

#### Compliant solution

```
r"abc"
```

#### Exceptions

This rule does not raise when the character inside the class is a metacharacter. This notation is sometimes used to avoid escaping (e.g.,
`[.]{3}` to match three dots).

---

## 📄 `app/services/sync_service.py`
**5 issue(s)** | Effort: 1h 14min

### Riga 82 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 4-28 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     80:     return new_filename
     81: 
 >>> 82: def archive_certificate_file(db: Session, cert: Certificato) -&gt; bool:
     83:     """
     84:     Moves a certificate's file to the STORICO folder.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 82 🟡 🟡 MAJOR

**🎯 Problema:** Remove the unused function parameter "db".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1172` - Unused function parameters should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 29-40 |
| Tags | unused |

**💻 Codice attuale:**
```python
     80:     return new_filename
     81: 
 >>> 82: def archive_certificate_file(db: Session, cert: Certificato) -&gt; bool:
     83:     """
     84:     Moves a certificate's file to the STORICO folder.
```

**❓ Perché è un problema:**

A typical code smell known as unused function parameters refers to parameters declared in a function but not used anywhere within the function’s
body. While this might seem harmless at first glance, it can lead to confusion and potential errors in your code. Disregarding the values passed to
such parameters, the function’s behavior will be the same, but the programmer’s intention won’t be clearly expressed anymore. Therefore, removing
function parameters that are not being utilized is considered best practice.

#### Exceptions

This rule ignores overriding methods.

```
class C(B):
 def do_something(self, a, b): # no issue reported on b
 return self.compute(a)
```

This rule also ignores variables named with a single underscore `_`. Such naming is a common practice for indicating that the variable
is insignificant.

```
def do_something(a, _): # no issue reported on _
 return compute(a)
```

The rule also won’t raise an issue if the parameter is referenced in a docstring or a comment:
...

**✅ Come risolvere:**

Having unused function parameters in your code can lead to confusion and misunderstanding of a developer’s intention. They reduce code readability
and introduce the potential for errors. To avoid these problems, developers should remove unused parameters from function declarations.

##### Noncompliant code example

```
def do_something(a, b): # second parameter is unused
 return compute(a)
```

##### Compliant solution

```
def do_something(a):
 return compute(a)
```

---

### Riga 98 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal '%d/%m/%Y' 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 63-73 |
| Tags | design |

**💻 Codice attuale:**
```python
     96:         'matricola': cert.dipendente.matricola if cert.dipendente else None,
     97:         'categoria': cert.corso.categoria_corso,
 >>> 98:         'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
     99:     }
     100: 
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 128 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 46 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 36min |
| Posizione | Colonne 4-30 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     126:     return False
     127: 
 >>> 128: def link_orphaned_certificates(db: Session, dipendente: Dipendente) -&gt; int:
     129:     """
     130:     Scans for orphaned certificates that match the given employee and links them.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 195 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 30 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 20min |
| Posizione | Colonne 4-25 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     193:     return linked_count
     194: 
 >>> 195: def synchronize_all_files(db: Session):
     196:     """
     197:     Scans all certificates and ensures their PDF files are located in the correct
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/views/import_view.py`
**5 issue(s)** | Effort: 1h 50min

### Riga 43 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "processed_files".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-23 |
| Tags | unused |

**💻 Codice attuale:**
```python
     41:     def run(self):
     42:         total_files = len(self.file_paths)
 >>> 43:         processed_files = 0
     44:         for i, file_path in enumerate(self.file_paths):
     45:             if self._is_stopped:
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

### Riga 75 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 93 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 1h23min |
| Posizione | Colonne 8-19 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     73:         self.finished.emit(self.archived_count, self.verify_count)
     74: 
 >>> 75:     def process_pdf(self, file_path):
     76:         original_filename = os.path.basename(file_path)
     77: 
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 108 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal '%d/%m/%Y' 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 81-91 |
| Tags | design |

**💻 Codice attuale:**
```python
     106:                     else:
     107:                         try:
 >>> 108:                             scadenza_date = datetime.strptime(data_scadenza_str, '%d/%m/%Y').date()
     109:                             file_scadenza = scadenza_date.strftime('%d_%m_%Y')
     110:                             # Bug 5 Fix: Use backend-aligned logic for status (considering threshold)
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 120 🟡 🟡 MAJOR

**🎯 Problema:** Either merge this branch with the identical one on line "117" or change one of the implementations.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1871` - Two branches in a conditional structure should not have exactly the same implementation |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 10min |
| Posizione | Colonne 32-48 |
| Tags | design, suspicious |

**💻 Codice attuale:**
```python
     118:                             # If expiring soon, it is technically "ATTIVO" folder (as per sync_service logic: attivo/in_scadenza -&gt; ATTIVO)
     119:                             elif scadenza_date &gt;= datetime.now().date():
 >>> 120:                                 stato = 'ATTIVO'
     121:                             # Else it is expired
     122:                         except ValueError:
```

**❓ Perché è un problema:**

When the same code is duplicated in two or more separate branches of a conditional, it can make the code harder to understand, maintain, and can
potentially introduce bugs if one instance of the code is changed but others are not.

Having two branches in the same `if` structure with the same implementation is at best duplicate code, and at worst a coding error.

```
if 0 &lt;= a &lt; 10:
 do_first()
 do_second()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
elif 20 &lt;= a &lt; 50:
 do_first() # Noncompliant; duplicates first condition
 do_second()
```

If the same logic is needed for both instances, then the conditions should be combined.

```
if (0 &lt;= a &lt; 10) or (20 &lt;= a &lt; 50):
 do_first()
 do_second()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
```

#### Exceptions

Blocks in an `if` chain that contain a single line of code are ignored.

```
if 0 &lt;= a &lt; 10:
 do_first()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
elif 20 &lt;= a &lt; 50:
 do_first() # no issu...

**📝 Descrizione:**

### Why is this an issue?

When the same code is duplicated in two or more separate branches of a conditional, it can make the code harder to understand, maintain, and can
potentially introduce bugs if one instance of the code is changed but others are not.

Having two branches in the same `if` structure with the same implementation is at best duplicate code, and at worst a coding error.

```
if 0 &lt;= a &lt; 10:
 do_first()
 do_second()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
elif 20 &lt;= a &lt; 50:
 do_first() # Noncompliant; duplicates first condition
 do_second()
```

If the same logic is needed for both instances, then the conditions should be combined.

```
if (0 &lt;= a &lt; 10) or (20 &lt;= a &lt; 50):
 do_first()
 do_second()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
```

#### Exceptions

Blocks in an `if` chain that contain a single line of code are ignored.

```
if 0 &lt;= a &lt; 10:
 do_first()
elif 10 &lt;= a &lt; 20:
 do_the_other_thing()
elif 20 &lt;= a &lt...

**📚 Risorse:**

#### Related rules

 - S3923 - All branches in a conditional structure should not have exactly the same implementation

---

### Riga 133 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "ERRORI ANALISI" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 66-82 |
| Tags | design |

**💻 Codice attuale:**
```python
     131:                     new_filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"
     132: 
 >>> 133:                     target_dir = os.path.join(self.output_folder, "ERRORI ANALISI", error_category, employee_folder_name, categoria_fs, stato)
     134:                     os.makedirs(target_dir, exist_ok=True)
     135:                     shutil.move(source_path, os.path.join(target_dir, new_filename))
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

## 📄 `desktop_app/services/license_updater_service.py`
**5 issue(s)** | Effort: 34min

### Riga 53 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 9min |
| Posizione | Colonne 8-22 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     51:         return sha256_hash.hexdigest()
     52: 
 >>> 53:     def update_license(self, hardware_id):
     54:         try:
     55:             config = self._load_config()
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 85 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "manifest.json" 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 66-81 |
| Tags | design |

**💻 Codice attuale:**
```python
     83: 
     84:             # Confronta con il manifest locale, se esiste
 >>> 85:             local_manifest_path = os.path.join(get_license_dir(), "manifest.json")
     86:             if os.path.exists(local_manifest_path):
     87:                 with open(local_manifest_path, 'r') as f:
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 99 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "pyarmor.rkey" 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 37-51 |
| Tags | design |

**💻 Codice attuale:**
```python
     97: 
     98:                 # Scarica gli altri file
 >>> 99:                 files_to_download = ["pyarmor.rkey", "config.dat"]
     100:                 for filename in files_to_download:
     101:                     file_api_url = f"{api_url}/{filename}"
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 99 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "config.dat" 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 53-65 |
| Tags | design |

**💻 Codice attuale:**
```python
     97: 
     98:                 # Scarica gli altri file
 >>> 99:                 files_to_download = ["pyarmor.rkey", "config.dat"]
     100:                 for filename in files_to_download:
     101:                     file_api_url = f"{api_url}/{filename}"
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 144 🟡 🟡 MAJOR

**🎯 Problema:** Add replacement fields or use a normal string instead of an f-string.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3457` - String formatting should be used correctly |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 26-105 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     142:             elif e.response.status_code == 401 or e.response.status_code == 403:
     143:                 return False, "Errore di autenticazione: Accesso non autorizzato. Contattare il supporto."
 >>> 144:             return False, f"Errore di rete durante il download della licenza. Verificare la connessione."
     145:         except (ValueError, KeyError) as e:
     146:             return False, f"Errore di validazione: {e}"
```

**❓ Perché è un problema:**

A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are invalid.

Formatted string literals (also called "f-strings"; available since Python 3.6) are generally simpler to use, and any syntax mistake will cause a
failure at compile time. However, it is easy to...

**✅ Come risolvere:**

A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

##### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"} # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile") # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]" # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice") # Noncompliant. Add 1 missing argument.
```

##### Compliant solution

```
"Error %(message)s" % {"message": "something failed"}

"Error: User {} has not been able to access {}".format("Alice", "MyFile")

user = "Alice"
resource = "MyFile"
message = f"Error: User {user} has not been able to access {resource}"

import logging
logging.error("Error: User %s has not been able to access %s", "Alice", "MyFile")
```

**📚 Risorse:**

- [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

 - Python documentation - printf-style String
 Formatting 

 - [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

 - Python
 documentation - Using particular formatting styles throughout your application 

 - Python documentation - Formatted string
 literals

---

## 📄 `app/services/ai_extraction.py`
**4 issue(s)** | Effort: 31min

### Riga 163 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 16min |
| Posizione | Colonne 4-23 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     161:         return model.generate_content([pdf_file_part, prompt])
     162: 
 >>> 163: def _extract_json_block(text: str) -&gt; str:
     164:     """
     165:     Robustly extracts the first valid JSON block from text, handling nested structures.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 185 🟡 🟡 MAJOR

**🎯 Problema:** Merge this if statement with the enclosing one.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1066` - Mergeable "if" statements should be combined |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 12-14 |
| Tags | clumsy |

**💻 Codice attuale:**
```python
     183:             stack.append(char)
     184:         elif char == '}' or char == ']':
 >>> 185:             if stack:
     186:                 last = stack[-1]
     187:                 if (last == '{' and char == '}') or (last == '[' and char == ']'):
```

**❓ Perché è un problema:**

Nested code - blocks of code inside blocks of code - is eventually necessary, but increases complexity. This is why keeping the code as flat as
possible, by avoiding unnecessary nesting, is considered a good practice.

Merging `if` statements when possible will decrease the nesting of the code and improve its readability.

Code like

```
if condition1:
 if condition2: # Noncompliant
 # ...
```

Will be more readable as

```
if condition1 and condition2: # Compliant
 # ...
```

**✅ Come risolvere:**

If merging the conditions seems to result in a more complex code, extracting the condition or part of it in a named function or variable is a
better approach to fix readability.

##### Noncompliant code example

```
if file.isValid():
 if file.isfile() or file.isdir(): # Noncompliant
 # ...
```

##### Compliant solution

```
def isFileOrDirectory(File file):
 return file.isFile() or file.isDirectory()

if file.isValid() and isFileOrDirectory(file): # Compliant
 # ...
```

---

### Riga 240 🟡 🟡 MAJOR

**🎯 Problema:** Remove this commented out code.

| Campo | Valore |
|-------|--------|
| Regola | `python:S125` - Sections of code should not be commented out |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-53 |
| Tags | unused |

**💻 Codice attuale:**
```python
     238:         # Actually, if we allow dynamic, we don't need this block at all.
     239:         
 >>> 240:         # valid_categories = list(CATEGORIE_STATICHE)
     241:         # if "ATEX" not in valid_categories:
     242:         #     valid_categories.append("ATEX")
```

**❓ Perché è un problema:**

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

**📝 Descrizione:**

### Why is this an issue?

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

### Riga 244 🟡 🟡 MAJOR

**🎯 Problema:** Remove this commented out code.

| Campo | Valore |
|-------|--------|
| Regola | `python:S125` - Sections of code should not be commented out |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-55 |
| Tags | unused |

**💻 Codice attuale:**
```python
     242:         #     valid_categories.append("ATEX")
     243: 
 >>> 244:         # if data["categoria"] not in valid_categories:
     245:         #     logging.warning(f"Invalid category '{data['categoria']}'. Defaulting to 'ALTRO'.")
     246:         #     data["categoria"] = "ALTRO"
```

**❓ Perché è un problema:**

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

**📝 Descrizione:**

### Why is this an issue?

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

## 📄 `desktop_app/views/login_view.py`
**4 issue(s)** | Effort: 52min

### Riga 216 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Hardware ID" 5 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 10min |
| Posizione | Colonne 28-41 |
| Tags | design |

**💻 Codice attuale:**
```python
     214:             }
     215:         """)
 >>> 216:         if license_data and "Hardware ID" in license_data:
     217:             stored_hw_id = license_data["Hardware ID"]
     218:             if stored_hw_id == current_hw_id:
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 242 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "color: #93C5FD; font-size: 13px; font-weight: 500;" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 40-92 |
| Tags | design |

**💻 Codice attuale:**
```python
     240:             license_label.setStyleSheet("color: #FBBF24; font-size: 13px; font-weight: 600;")
     241:         else:
 >>> 242:             license_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
     243:         license_label.setWordWrap(True)
     244:         license_info_layout.addWidget(license_label)
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 749 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 44 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 34min |
| Posizione | Colonne 8-24 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     747:         CustomMessageDialog.show_error(self, "Errore di Accesso", error_msg)
     748: 
 >>> 749:     def on_login_success(self, response):
     750:         try:
     751:             self.api_client.set_token(response)
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 765 🟡 🟢 MINOR

**🎯 Problema:** Remove this unneeded "pass".

| Campo | Valore |
|-------|--------|
| Regola | `python:S2772` - "pass" should not be used needlessly |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 21-25 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     763:                      # But we are trapped.
     764:                      # Let's show warning and then continue to Read-Only mode, skipping the loop.
 >>> 765:                      pass
     766:                 else:
     767:                     while True:
```

**❓ Perché è un problema:**

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

**📝 Descrizione:**

This rule raises an issue when a `pass` statement is redundant.

### Why is this an issue?

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

#### Code examples

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

### Resources

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

## 📄 `admin/crea_licenze/admin_license_gui.py`
**4 issue(s)** | Effort: 31min

### Riga 32 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Segoe UI" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 40-50 |
| Tags | design |

**💻 Codice attuale:**
```python
     30:         style = ttk.Style()
     31:         style.theme_use('clam')
 >>> 32:         style.configure("TLabel", font=("Segoe UI", 10))
     33:         style.configure("TButton", font=("Segoe UI", 10, "bold"))
     34: 
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 69 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     67:             self.ent_disk.delete(0, tk.END)
     68:             self.ent_disk.insert(0, self.root.clipboard_get().strip())
 >>> 69:         except: pass
     70: 
     71:     def generate(self):
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 71 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 14min |
| Posizione | Colonne 8-16 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     69:         except: pass
     70: 
 >>> 71:     def generate(self):
     72:         disk_serial = self.ent_disk.get().strip()
     73:         client_name = self.ent_name.get().strip()
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 102 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "pyarmor.rkey" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 51-65 |
| Tags | design |

**💻 Codice attuale:**
```python
     100:             if res.returncode == 0:
     101:                 # PyArmor di default mette l'output in "dist/pyarmor.rkey" relativo alla CWD
 >>> 102:                 src_default = os.path.join("dist", "pyarmor.rkey")
     103:                 
     104:                 if os.path.exists(src_default):
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

## 📄 `app/db/seeding.py`
**3 issue(s)** | Effort: 41min

### Riga 13 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 16min |
| Posizione | Colonne 4-18 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     11: from datetime import datetime
     12: 
 >>> 13: def migrate_schema(db: Session):
     14:     """
     15:     Checks for missing columns in existing tables (due to lack of migrations)
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 123 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 33 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 23min |
| Posizione | Colonne 4-27 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     121:         raise # Critical failure
     122: 
 >>> 123: def cleanup_deprecated_data(db: Session):
     124:     """
     125:     Removes data related to deprecated categories like 'MEDICO COMPETENTE'.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 246 🟡 🟢 MINOR

**🎯 Problema:** Use the opposite operator ("!=") instead.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1940` - Boolean checks should not be inverted |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 15-90 |
| Tags | pitfall |

**💻 Codice attuale:**
```python
     244:             # Bug 1 Fix: Ensure password matches settings
     245:             current_admin_password = settings.FIRST_RUN_ADMIN_PASSWORD
 >>> 246:             if not get_password_hash(current_admin_password) == admin_user.hashed_password: # Simple check wont work with salt
     247:                 # Verify properly
     248:                 from app.core.security import verify_password
```

**❓ Perché è un problema:**

It is needlessly complex to invert the result of a boolean comparison. The opposite comparison should be made instead.

#### Noncompliant code example

```
if not a == 2: # Noncompliant
 b = not i &lt; 10 # Noncompliant
```

#### Compliant solution

```
if a != 2 :
 b = i &gt;= 10
```

**📝 Descrizione:**

### Why is this an issue?

It is needlessly complex to invert the result of a boolean comparison. The opposite comparison should be made instead.

#### Noncompliant code example

```
if not a == 2: # Noncompliant
 b = not i &lt; 10 # Noncompliant
```

#### Compliant solution

```
if a != 2 :
 b = i &gt;= 10
```

---

## 📄 `app/services/chat_service.py`
**3 issue(s)** | Effort: 19min

### Riga 15 🟡 🔴 CRITICAL

**🎯 Problema:** Add a nested comment explaining why this method is empty, or complete the implementation.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1186` - Functions and methods should not be empty |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-16 |
| Tags | suspicious |

**💻 Codice attuale:**
```python
     13: 
     14: class ChatService:
 >>> 15:     def __init__(self):
     16:         pass
     17: 
```

**❓ Perché è un problema:**

An empty method is generally considered bad practice and can lead to confusion, readability, and maintenance issues. Empty methods bring no
functionality and are misleading to others as they might think the method implementation fulfills a specific and identified requirement.

There are several reasons for a method not to have a body:

 - It is an unintentional omission, and should be fixed to prevent an unexpected behavior in production. 

 - It is not yet, or never will be, supported. In this case an exception should be thrown. 

 - The method is an intentionally-blank override. In this case a nested comment should explain the reason for the blank override. 

#### Exceptions

No issue will be raised when the empty method is abstract and meant to be overridden in a subclass, i.e. it is decorated with
`abc.abstractmethod`, `abc.abstractstaticmethod`, `abc.abstractclassmethod` or `abc.abstractproperty`.
Note however that these methods should normally have a docstring explaining how subc...

**✅ Come risolvere:**

##### Noncompliant code example

```
def shouldNotBeEmpty(): # Noncompliant - method is empty
 pass

def notImplemented(): # Noncompliant - method is empty
 pass

def emptyOnPurpose(): # Noncompliant - method is empty
 pass
```

##### Compliant solution

```
def shouldNotBeEmpty():
 doSomething()

def notImplemented():
 raise NotImplementedError("notImplemented() cannot be performed because ...")

def emptyOnPurpose():
 pass # comment explaining why the method is empty

def emptyOnPurposeBis():
 """
 Docstring explaining why this function is empty.
 """
```

---

### Riga 18 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 9min |
| Posizione | Colonne 8-23 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     16:         pass
     17: 
 >>> 18:     def get_rag_context(self, db: Session, user: User) -&gt; str:
     19:         """
     20:         Retrieves context from the database to ground the AI.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 99 🟡 🟡 MAJOR

**🎯 Problema:** Merge this if statement with the enclosing one.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1066` - Mergeable "if" statements should be combined |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 13-15 |
| Tags | clumsy |

**💻 Codice attuale:**
```python
     97: 
     98:         if not api_key or "obf:" in api_key:
 >>> 99:              if not api_key:
     100:                  return "Errore: Chiave API Chat non configurata."
     101: 
```

**❓ Perché è un problema:**

Nested code - blocks of code inside blocks of code - is eventually necessary, but increases complexity. This is why keeping the code as flat as
possible, by avoiding unnecessary nesting, is considered a good practice.

Merging `if` statements when possible will decrease the nesting of the code and improve its readability.

Code like

```
if condition1:
 if condition2: # Noncompliant
 # ...
```

Will be more readable as

```
if condition1 and condition2: # Compliant
 # ...
```

**✅ Come risolvere:**

If merging the conditions seems to result in a more complex code, extracting the condition or part of it in a named function or variable is a
better approach to fix readability.

##### Noncompliant code example

```
if file.isValid():
 if file.isfile() or file.isdir(): # Noncompliant
 # ...
```

##### Compliant solution

```
def isFileOrDirectory(File file):
 return file.isFile() or file.isDirectory()

if file.isValid() and isFileOrDirectory(file): # Compliant
 # ...
```

---

## 📄 `desktop_app/views/validation_view.py`
**3 issue(s)** | Effort: 21min

### Riga 139 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Database in sola lettura" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 40-66 |
| Tags | design |

**💻 Codice attuale:**
```python
     137:             self.validate_button.setEnabled(False)
     138:             self.delete_button.setEnabled(False)
 >>> 139:             self.edit_button.setToolTip("Database in sola lettura")
     140:             self.validate_button.setToolTip("Database in sola lettura")
     141:             self.delete_button.setToolTip("Database in sola lettura")
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 172 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 13-19 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     170:                  if first_row &lt; len(self.df):
     171:                      return {'mode': 'reselect_by_id', 'id': self.df.iloc[first_row]['id'], 'fallback_row': first_row}
 >>> 172:              except:
     173:                  pass
     174: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 246 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 10min |
| Posizione | Colonne 8-23 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     244:         self._on_data_loaded([])
     245: 
 >>> 246:     def _on_data_loaded(self, data):
     247:         if not data:
     248:             self.df = pd.DataFrame()
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `app/services/notification_service.py`
**3 issue(s)** | Effort: 35min

### Riga 37 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     35:         try:
     36:             self.image('desktop_app/assets/logo.png', 10, 8, 45)
 >>> 37:         except:
     38:             pass # Skip logo if missing to prevent crash
     39:         self.set_font('Arial', 'B', 15)
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 50 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 30 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 20min |
| Posizione | Colonne 4-33 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     48:         self.cell(0, 10, 'Pagina ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')
     49: 
 >>> 50: def generate_pdf_report_in_memory(expiring_visite, expiring_corsi, overdue_certificates, visite_threshold, corsi_threshold):
     51:     """Generates a professional, multi-table PDF report with pagination logic."""
     52:     try:
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 262 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 10min |
| Posizione | Colonne 4-19 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     260:         logging.error(f"Failed to send security alert: {e}")
     261: 
 >>> 262: def get_report_data(db: Session):
     263:     today = date.today()
     264:     expiring_visite = []
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/views/database_view.py`
**3 issue(s)** | Effort: 13min

### Riga 225 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 8-26 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     223:         self._update_button_states()
     224: 
 >>> 225:     def _update_table_view(self):
     226:         df = self.view_model.filtered_data
     227: 
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 230 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 12-18 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     228:         if self.table_view.model() and self.table_view.selectionModel():
     229:             try: self.table_view.selectionModel().selectionChanged.disconnect(self._update_button_states)
 >>> 230:             except: pass
     231: 
     232:         if not df.empty:
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 412 🟡 🟡 MAJOR

**🎯 Problema:** Add replacement fields or use a normal string instead of an f-string.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3457` - String formatting should be used correctly |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 62-93 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     410:             try:
     411:                 self.model._data.to_csv(path, index=False)
 >>> 412:                 ToastManager.success("Esportazione Riuscita", f"Dati esportati con successo.", self.window())
     413:             except Exception as e:
     414:                 self._show_error_message(f"Impossibile salvare il file: {e}")
```

**❓ Perché è un problema:**

A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are invalid.

Formatted string literals (also called "f-strings"; available since Python 3.6) are generally simpler to use, and any syntax mistake will cause a
failure at compile time. However, it is easy to...

**✅ Come risolvere:**

A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

##### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"} # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile") # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]" # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice") # Noncompliant. Add 1 missing argument.
```

##### Compliant solution

```
"Error %(message)s" % {"message": "something failed"}

"Error: User {} has not been able to access {}".format("Alice", "MyFile")

user = "Alice"
resource = "MyFile"
message = f"Error: User {user} has not been able to access {resource}"

import logging
logging.error("Error: User %s has not been able to access %s", "Alice", "MyFile")
```

**📚 Risorse:**

- [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

 - Python documentation - printf-style String
 Formatting 

 - [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

 - Python
 documentation - Using particular formatting styles throughout your application 

 - Python documentation - Formatted string
 literals

---

## 📄 `app/core/db_security.py`
**3 issue(s)** | Effort: 24min

### Riga 84 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 14min |
| Posizione | Colonne 8-37 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     82:         return base64.urlsafe_b64encode(digest)
     83: 
 >>> 84:     def _check_and_recover_stale_lock(self):
     85:         """
     86:         Detects if a lock file exists but belongs to a dead process.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 108 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     106:                 try:
     107:                     metadata = json.loads(data.decode('utf-8'))
 >>> 108:                 except:
     109:                     # Corrupt JSON -&gt; Force Clean
     110:                     should_remove = True
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 350 🟡 🟢 MINOR

**🎯 Problema:** Add logic to this except clause or eliminate it and rethrow the exception automatically.

| Campo | Valore |
|-------|--------|
| Regola | `python:S2737` - "except" clauses should do more than raise the same issue |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 16-21 |
| Tags | clumsy, error-handling, finding, unused |

**💻 Codice attuale:**
```python
     348:                 os.replace(swp_path, self.db_path)
     349:             except PermissionError:
 >>> 350:                 raise
     351:         else:
     352:             os.replace(swp_path, self.db_path)
```

**❓ Perché è un problema:**

An `except` clause that only rethrows the caught exception has the same effect as omitting the `except` altogether and
letting it bubble up automatically.

```
a = {}
try:
 a[5]
except KeyError:
 raise # Noncompliant
```

Such clauses should either be removed or populated with the appropriate logic.

```
a = {}
try:
 a[5]
except KeyError as e:
 logging.exception('error while accessing the dict')
 raise e
```

**📝 Descrizione:**

### Why is this an issue?

An `except` clause that only rethrows the caught exception has the same effect as omitting the `except` altogether and
letting it bubble up automatically.

```
a = {}
try:
 a[5]
except KeyError:
 raise # Noncompliant
```

Such clauses should either be removed or populated with the appropriate logic.

```
a = {}
try:
 a[5]
except KeyError as e:
 logging.exception('error while accessing the dict')
 raise e
```

---

## 📄 `desktop_app/main_window_ui.py`
**3 issue(s)** | Effort: 33min

### Riga 156 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 13min |
| Posizione | Colonne 8-16 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 261 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Scadenza Licenza" 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 43-61 |
| Tags | design |

**💻 Codice attuale:**
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

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 619 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 24 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 14min |
| Posizione | Colonne 8-35 |
| Tags | brain-overload |

**💻 Codice attuale:**
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

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/views/anagrafica_view.py`
**3 issue(s)** | Effort: 14min

### Riga 15 🟡 🟡 MAJOR

**🎯 Problema:** Add replacement fields or use a normal string instead of an f-string.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3457` - String formatting should be used correctly |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 27-11 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     13:     def __init__(self, title, value, color="#3B82F6", parent=None):
     14:         super().__init__(parent)
 >>> 15:         self.setStyleSheet(f"""
 >>> 16:             QFrame {{
 >>> 17:                 background-color: #FFFFFF;
 >>> 18:                 border: 1px solid #E5E7EB;
 >>> 19:                 border-radius: 8px;
 >>> 20:             }}
 >>> 21:         """)
     22:         layout = QVBoxLayout(self)
     23:         layout.setContentsMargins(15, 15, 15, 15)
```

**❓ Perché è un problema:**

A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are invalid.

Formatted string literals (also called "f-strings"; available since Python 3.6) are generally simpler to use, and any syntax mistake will cause a
failure at compile time. However, it is easy to...

**✅ Come risolvere:**

A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

##### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"} # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile") # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]" # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice") # Noncompliant. Add 1 missing argument.
```

##### Compliant solution

```
"Error %(message)s" % {"message": "something failed"}

"Error: User {} has not been able to access {}".format("Alice", "MyFile")

user = "Alice"
resource = "MyFile"
message = f"Error: User {user} has not been able to access {resource}"

import logging
logging.error("Error: User %s has not been able to access %s", "Alice", "MyFile")
```

**📚 Risorse:**

- [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

 - Python documentation - printf-style String
 Formatting 

 - [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

 - Python
 documentation - Using particular formatting styles throughout your application 

 - Python documentation - Formatted string
 literals

---

### Riga 60 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal """
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """ 3 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 33-11 |
| Tags | design |

**💻 Codice attuale:**
```python
     58:         left_panel = QFrame()
     59:         left_panel.setFixedWidth(300)
 >>> 60:         left_panel.setStyleSheet("""
 >>> 61:             QFrame {
 >>> 62:                 background-color: #FFFFFF;
 >>> 63:                 border-radius: 12px;
 >>> 64:                 border: 1px solid #E5E7EB;
 >>> 65:             }
 >>> 66:         """)
     67:         left_layout = QVBoxLayout(left_panel)
     68:         left_layout.setContentsMargins(15, 15, 15, 15)
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 416 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 8-23 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     414:             QMessageBox.critical(self, "Errore", f"Impossibile caricare dettagli: {e}")
     415: 
 >>> 416:     def populate_detail(self, data):
     417:         # Header
     418:         full_name = f"{data['cognome']} {data['nome']}"
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `boot_loader.py`
**3 issue(s)** | Effort: 15min

### Riga 19 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     17:             # 0x10 = MB_ICONHAND (Error icon)
     18:             ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
 >>> 19:         except:
     20:             pass # Se fallisce anche questo, non possiamo farci nulla.
     21:     else:
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 48 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 4-10 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     46:         with open("CRASH_LOG.txt", "a", encoding="utf-8") as f:
     47:             f.write(log_content)
 >>> 48:     except: pass
     49: 
     50:     # 2. Scrivi sul Desktop dell'utente (per massima visibilità)
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

### Riga 57 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     55:                 with open(os.path.join(desktop, "INTELLEO_CRASH_LOG.txt"), "a", encoding="utf-8") as f:
     56:                     f.write(log_content)
 >>> 57:         except: pass
     58: 
     59: def main():
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

## 📄 `launcher.py`
**2 issue(s)** | Effort: 35min

### Riga 123 🟡 🔴 CRITICAL

**🎯 Problema:** Remove this "raise" statement or move it inside an "except" block.

| Campo | Valore |
|-------|--------|
| Regola | `python:S5747` - Bare "raise" statements should only be used in "except" blocks |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 10min |
| Posizione | Colonne 8-13 |
| Tags | confusing, error-handling, unpredictable |

**💻 Codice attuale:**
```python
     121:     # 4. Exit
     122:     if issubclass(exctype, SystemExit):
 >>> 123:         raise
     124:     sys.exit(1)
     125: 
```

**❓ Perché è un problema:**

A bare `raise` statement, i.e. a `raise` with no exception provided, will re-raise the last active exception in the current
scope:

```
def foo():
 try:
 ...
 except ValueError as e:
 raise # this will re-raise "e"
```

If the `raise` statement is not in an `except` or `finally` block, no exception is active and a
`RuntimeError` is raised instead.

If the bare `raise` statement is in a function called in an `except` block, the exception caught by the `except`
will be re-raised. However, this behavior is not reliable as nothing prevents a developer from calling the function from a different context.

Overall, having bare `raise` statements outside of `except` blocks is discouraged as it is hard to understand and
maintain.

#### Notes

In a `finally` block, an exception is still active only when it hasn’t been caught in a previous `except` clause or if it has
been raised in an `except` block. In both cases, it is better to let the exception propagate automatically than to re-raise it. Th...

**✅ Come risolvere:**

To fix this issue, make sure to specify which exception needs to be raised when outside of an `except` block.

##### Noncompliant code example

```
raise # Noncompliant: no active exception

def foo():
 raise # Noncompliant: no active exception
 try:
 raise # Noncompliant: no active exception
 except ValueError:
 handle_error()

def handle_error():
 raise # Noncompliant: this is not reliable
```

##### Compliant solution

```
raise ValueError()

def foo():
 raise ValueError()
 try:
 raise ValueError()
 except ValueError:
 raise
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The `raise` statement](https://docs.python.org/3/reference/simple_stmts.html#raise)

---

### Riga 383 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 35 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 25min |
| Posizione | Colonne 4-30 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     381: 
     382: 
 >>> 383: def check_and_recover_database(controller):
     384:     """
     385:     Checks database integrity and prompts user for recovery actions if needed.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/components/floating_chat_widget.py`
**2 issue(s)** | Effort: 24min

### Riga 130 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 33 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 23min |
| Posizione | Colonne 8-19 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     128:         self.expand_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
     129: 
 >>> 130:     def eventFilter(self, source, event):
     131:         if source == self.fab:
     132:             if event.type() == QEvent.Type.MouseButtonPress:
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 173 🟡 🟡 MAJOR

**🎯 Problema:** Remove this assignment to local variable 'align_flag'; the value is never used.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1854` - Unused assignments should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 8-47 |
| Tags | cwe, unused |

**💻 Codice attuale:**
```python
     171: 
     172:         target_x = 0
 >>> 173:         align_flag = Qt.AlignmentFlag.AlignLeft
     174: 
     175:         # Snap Right
```

**❓ Perché è un problema:**

Dead stores refer to assignments made to local variables that are subsequently never used or immediately overwritten. Such assignments are
unnecessary and don’t contribute to the functionality or clarity of the code. They may even negatively impact performance. Removing them enhances code
cleanliness and readability. Even if the unnecessary operations do not do any harm in terms of the program’s correctness, they are - at best - a waste
of computing resources.

#### Exceptions

This rule ignores initializations to `-1`, `0`, `1`, `None`, `True`, `False` and
`""`. No issue will be raised on unpacked variables.

**✅ Come risolvere:**

Remove the unnecessary assignment, then test the code to make sure that the right-hand side of a given assignment had no side effects (e.g. a
method that writes certain data to a file and returns the number of written bytes).

##### Noncompliant code example

```
def func(a, b, compute):
 i = a + b # Noncompliant; calculation result not used before value is overwritten
 i = compute()
 return i
```

##### Compliant solution

```
def func(a, b, compute):
 i = a + b
 i += compute()
 return i
```

**📚 Risorse:**

#### Standards

 - CWE - [CWE-563 - Assignment to Variable without Use ('Unused Variable')](https://cwe.mitre.org/data/definitions/563) 

#### Related rules

 - S1763 - All code should be reachable 

 - S3516 - Functions returns should not be invariant 

 - S3626 - Jump statements should not be redundant

---

## 📄 `tools/prepare_installer_assets.py`
**2 issue(s)** | Effort: 11min

### Riga 71 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 4-18 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     69:         draw_neural_network(painter, width, height)
     70: 
 >>> 71: def draw_tech_grid(painter, width, height, is_dark):
     72:     """Draws a subtle hexagonal grid."""
     73:     size = 45
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 210 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "app".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 4-7 |
| Tags | unused |

**💻 Codice attuale:**
```python
     208: 
     209: def create_assets():
 >>> 210:     app = QApplication(sys.argv)
     211:     base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
     212:     assets_dir = os.path.join(base_dir, "desktop_app", "assets")
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `tests/desktop_app/components/test_neural_3d.py`
**2 issue(s)** | Effort: 2min

### Riga 40 🟡 🟢 MINOR

**🎯 Problema:** Consider using "assertGreater" instead.

| Campo | Valore |
|-------|--------|
| Regola | `python:S5906` - The most specific "unittest" assertion should be used |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 1min |
| Posizione | Colonne 8-50 |
| Tags | tests, unittest |

**💻 Codice attuale:**
```python
     38: 
     39:         # Check assets generation
 >>> 40:         self.assertTrue(len(nn.star_textures) &gt; 0)
     41: 
     42:     def test_update_logic(self):
```

**❓ Perché è un problema:**

The `unittest` module provides assertion methods specific to common types and operations. Both versions will test the same things, but
the dedicated one will provide a better error message, simplifying the debugging process.

This rule reports an issue when an assertion can be simplified by using a more specific function. The array below gives a list of assertions on
which an issue will be raised, and which function should be used instead:

 
 
 
 
 
 
 Original
 Dedicated
 
 
 
 
 `assertTrue(x == y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x != y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x == y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x != y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x < y)`

 `assertLess(x, y)`

 
 
 `assertTrue(x <= y)`

 `assertLessEqual(x, y)`

 
 
 `assertTrue(x > y)`

 `assertGreater(x, y)`

 
 
 `assertTrue(x >= y)`

 `assertGreaterEqual(x, y)`

 
 
 `assertTrue(x is y)`

 `assertIs(x, y)`

 
 
 `assertTrue(x is not y)`

 `assertIsNot(x, y)`

 
 
 `ass...

**📝 Descrizione:**

### Why is this an issue?

The `unittest` module provides assertion methods specific to common types and operations. Both versions will test the same things, but
the dedicated one will provide a better error message, simplifying the debugging process.

This rule reports an issue when an assertion can be simplified by using a more specific function. The array below gives a list of assertions on
which an issue will be raised, and which function should be used instead:

 
 
 
 
 
 
 Original
 Dedicated
 
 
 
 
 `assertTrue(x == y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x != y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x == y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x != y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x < y)`

 `assertLess(x, y)`

 
 
 `assertTrue(x <= y)`

 `assertLessEqual(x, y)`

 
 
 `assertTrue(x > y)`

 `assertGreater(x, y)`

 
 
 `assertTrue(x >= y)`

 `assertGreaterEqual(x, y)`

 
 
 `assertTrue(x is y)`

 `assertIs(x, y)`

 
 
 `assertTrue(x is not y)`

 `as...

**📚 Risorse:**

Python documentation - the `unittest`
module

---

### Riga 71 🟡 🟢 MINOR

**🎯 Problema:** Consider using "assertGreater" instead.

| Campo | Valore |
|-------|--------|
| Regola | `python:S5906` - The most specific "unittest" assertion should be used |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 1min |
| Posizione | Colonne 8-43 |
| Tags | tests, unittest |

**💻 Codice attuale:**
```python
     69:                 nn.update(0, 0)
     70: 
 >>> 71:         self.assertTrue(len(nn.pulses) &gt; 0)
     72:         self.assertEqual(nn.pulses[0][0], 0) # Start idx
     73:         self.assertEqual(nn.pulses[0][1], 1) # End idx
```

**❓ Perché è un problema:**

The `unittest` module provides assertion methods specific to common types and operations. Both versions will test the same things, but
the dedicated one will provide a better error message, simplifying the debugging process.

This rule reports an issue when an assertion can be simplified by using a more specific function. The array below gives a list of assertions on
which an issue will be raised, and which function should be used instead:

 
 
 
 
 
 
 Original
 Dedicated
 
 
 
 
 `assertTrue(x == y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x != y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x == y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x != y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x < y)`

 `assertLess(x, y)`

 
 
 `assertTrue(x <= y)`

 `assertLessEqual(x, y)`

 
 
 `assertTrue(x > y)`

 `assertGreater(x, y)`

 
 
 `assertTrue(x >= y)`

 `assertGreaterEqual(x, y)`

 
 
 `assertTrue(x is y)`

 `assertIs(x, y)`

 
 
 `assertTrue(x is not y)`

 `assertIsNot(x, y)`

 
 
 `ass...

**📝 Descrizione:**

### Why is this an issue?

The `unittest` module provides assertion methods specific to common types and operations. Both versions will test the same things, but
the dedicated one will provide a better error message, simplifying the debugging process.

This rule reports an issue when an assertion can be simplified by using a more specific function. The array below gives a list of assertions on
which an issue will be raised, and which function should be used instead:

 
 
 
 
 
 
 Original
 Dedicated
 
 
 
 
 `assertTrue(x == y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x != y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x == y)`

 `assertNotEqual(x, y)`

 
 
 `assertFalse(x != y)`

 `assertEqual(x, y)`

 
 
 `assertTrue(x < y)`

 `assertLess(x, y)`

 
 
 `assertTrue(x <= y)`

 `assertLessEqual(x, y)`

 
 
 `assertTrue(x > y)`

 `assertGreater(x, y)`

 
 
 `assertTrue(x >= y)`

 `assertGreaterEqual(x, y)`

 
 
 `assertTrue(x is y)`

 `assertIs(x, y)`

 
 
 `assertTrue(x is not y)`

 `as...

**📚 Risorse:**

Python documentation - the `unittest`
module

---

## 📄 `desktop_app/components/custom_dialog.py`
**2 issue(s)** | Effort: 10min

### Riga 50 🟡 🟡 MAJOR

**🎯 Problema:** Extract this nested conditional expression into an independent statement.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3358` - Conditional expressions should not be nested |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 50-88 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     48:         # Title
     49:         self.title_label = QLabel(title)
 >>> 50:         title_color = "#DC2626" if is_error else ("#D97706" if is_warning else "#1F2937")
     51:         self.title_label.setStyleSheet(f"color: {title_color}; font-size: 18px; font-weight: 700;")
     52:         self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
```

**❓ Perché è un problema:**

Nested conditionals are hard to read and can make the order of operations complex to understand.

```
class Job:
 @property
 def readable_status(self):
 return "Running" if job.is_running else "Failed" if job.errors else "Succeeded" # Noncompliant
```

Instead, use another line to express the nested operation in a separate statement.

```
class Job:
 @property
 def readable_status(self):
 if job.is_running:
 return "Running"
 return "Failed" if job.errors else "Succeeded"
```

#### Exceptions

No issue is raised on conditional expressions in comprehensions.

```
job_statuses = ["Running" if job.is_running else "Failed" if job.errors else "Succeeded" for job in jobs] # Compliant by exception
```

**📝 Descrizione:**

### Why is this an issue?

Nested conditionals are hard to read and can make the order of operations complex to understand.

```
class Job:
 @property
 def readable_status(self):
 return "Running" if job.is_running else "Failed" if job.errors else "Succeeded" # Noncompliant
```

Instead, use another line to express the nested operation in a separate statement.

```
class Job:
 @property
 def readable_status(self):
 if job.is_running:
 return "Running"
 return "Failed" if job.errors else "Succeeded"
```

#### Exceptions

No issue is raised on conditional expressions in comprehensions.

```
job_statuses = ["Running" if job.is_running else "Failed" if job.errors else "Succeeded" for job in jobs] # Compliant by exception
```

---

### Riga 121 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "result".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-14 |
| Tags | unused |

**💻 Codice attuale:**
```python
     119:         """
     120:         dialog = CustomMessageDialog(title, message, parent=parent, is_question=True)
 >>> 121:         result = dialog.exec()
     122:         return dialog.result_value
     123: 
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `desktop_app/views/modern_guide_view.py`
**2 issue(s)** | Effort: 4min

### Riga 21 🟡 🟢 MINOR

**🎯 Problema:** Rename this parameter "lineNumber" to match the regular expression ^[_a-z][a-z0-9_]*$.

| Campo | Valore |
|-------|--------|
| Regola | `python:S117` - Local variable and function parameter names should comply with a naming convention |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 55-65 |
| Tags | convention |

**💻 Codice attuale:**
```python
     19: 
     20: class CustomWebEnginePage(QWebEnginePage):
 >>> 21:     def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
     22:         # Suppress specific router warnings that clutter the console
     23:         if "No routes matched location" in message:
```

**❓ Perché è un problema:**

A naming convention in software development is a set of guidelines for naming code elements like variables, functions, and classes.
 Local
variables and function parameters hold the meaning of the written code. Their names should be meaningful and follow a consistent and easily
recognizable pattern.
 Adhering to a consistent naming convention helps to make the code more readable and understandable, which makes it easier to
maintain and debug. It also ensures consistency in the code, especially when multiple developers are working on the same project.

This rule checks that local variable and function parameter names match a provided regular expression.

#### What is the potential impact?

Inconsistent naming of local variables and function parameters can lead to several issues in your code:

 - **Reduced Readability**: Inconsistent local variable and function parameter names make the code harder to read and understand;
 consequently, it is more difficult to identify the purpose of each...

**✅ Come risolvere:**

First, familiarize yourself with the particular naming convention of the project in question. Then, update the name to match the convention, as
well as all usages of the name. For many IDEs, you can use built-in renaming and refactoring features to update all usages at once.

##### Noncompliant code example

With the default regular expression `^[_a-z][a-z0-9_]*$`:

```
def print_something(IMPORTANT_PARAM): # Noncompliant
 localVariable = "" # Noncompliant
 print(IMPORTANT_PARAM + localVariable)
```

##### Compliant solution

```
def print_something(important_param):
 local_variable = ""
 print(important_param + local_variable)
```

**📚 Risorse:**

#### Documentation

 - Python Enhancement Proposals - [PEP8 - Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions) 

 - Wikipedia - [Naming Convention (programming)](https://en.wikipedia.org/wiki/Naming_convention_(programming)) 

#### Related rules

 - S100 - Method names should comply with a naming convention 

 - S101 - Class names should comply with a naming convention 

 - S116 - Field names should comply with a naming convention 

 - S1542 - Function names should comply with a naming convention 

 - S1578 - Module names should comply with a naming convention 

 - S27...

---

### Riga 21 🟡 🟢 MINOR

**🎯 Problema:** Rename this parameter "sourceID" to match the regular expression ^[_a-z][a-z0-9_]*$.

| Campo | Valore |
|-------|--------|
| Regola | `python:S117` - Local variable and function parameter names should comply with a naming convention |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 67-75 |
| Tags | convention |

**💻 Codice attuale:**
```python
     19: 
     20: class CustomWebEnginePage(QWebEnginePage):
 >>> 21:     def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
     22:         # Suppress specific router warnings that clutter the console
     23:         if "No routes matched location" in message:
```

**❓ Perché è un problema:**

A naming convention in software development is a set of guidelines for naming code elements like variables, functions, and classes.
 Local
variables and function parameters hold the meaning of the written code. Their names should be meaningful and follow a consistent and easily
recognizable pattern.
 Adhering to a consistent naming convention helps to make the code more readable and understandable, which makes it easier to
maintain and debug. It also ensures consistency in the code, especially when multiple developers are working on the same project.

This rule checks that local variable and function parameter names match a provided regular expression.

#### What is the potential impact?

Inconsistent naming of local variables and function parameters can lead to several issues in your code:

 - **Reduced Readability**: Inconsistent local variable and function parameter names make the code harder to read and understand;
 consequently, it is more difficult to identify the purpose of each...

**✅ Come risolvere:**

First, familiarize yourself with the particular naming convention of the project in question. Then, update the name to match the convention, as
well as all usages of the name. For many IDEs, you can use built-in renaming and refactoring features to update all usages at once.

##### Noncompliant code example

With the default regular expression `^[_a-z][a-z0-9_]*$`:

```
def print_something(IMPORTANT_PARAM): # Noncompliant
 localVariable = "" # Noncompliant
 print(IMPORTANT_PARAM + localVariable)
```

##### Compliant solution

```
def print_something(important_param):
 local_variable = ""
 print(important_param + local_variable)
```

**📚 Risorse:**

#### Documentation

 - Python Enhancement Proposals - [PEP8 - Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions) 

 - Wikipedia - [Naming Convention (programming)](https://en.wikipedia.org/wiki/Naming_convention_(programming)) 

#### Related rules

 - S100 - Method names should comply with a naming convention 

 - S101 - Class names should comply with a naming convention 

 - S116 - Field names should comply with a naming convention 

 - S1542 - Function names should comply with a naming convention 

 - S1578 - Module names should comply with a naming convention 

 - S27...

---

## 📄 `app/core/lock_manager.py`
**2 issue(s)** | Effort: 12min

### Riga 25 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 8-15 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     23:         self.current_metadata: Optional[Dict] = None
     24: 
 >>> 25:     def acquire(self, owner_metadata: Dict, retries: int = 3, delay: float = 0.5) -&gt; Tuple[bool, Optional[Dict]]:
     26:         """
     27:         Attempts to acquire an exclusive lock on the file with retry logic.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

### Riga 103 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 8-24 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     101:                 self._lock_handle = None
     102: 
 >>> 103:     def update_heartbeat(self) -&gt; bool:
     104:         """
     105:         Updates the timestamp in the lock file to prove we are still alive.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `app/api/routers/auth.py`
**2 issue(s)** | Effort: 7min

### Riga 38 🟡 🟢 MINOR

**🎯 Problema:** Remove this unneeded "pass".

| Campo | Valore |
|-------|--------|
| Regola | `python:S2772` - "pass" should not be used needlessly |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 2min |
| Posizione | Colonne 12-16 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     36:             # If it failed, it's likely already blacklisted or race condition.
     37:             # We treat it as success (idempotent).
 >>> 38:             pass
     39: 
     40:     # Force DB Sync and Cleanup on logout to ensure data persistence and lock release
```

**❓ Perché è un problema:**

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

**📝 Descrizione:**

This rule raises an issue when a `pass` statement is redundant.

### Why is this an issue?

The use of a `pass` statement where it is not required by the syntax is redundant. It makes the code less readable and its intent
confusing.

To fix this issue, remove `pass` statements that do not affect the behaviour of the program.

#### Code examples

##### Noncompliant code example

```
def foo(arg):
 print(arg)
 pass # Noncompliant: the `pass` statement is not needed as it does not change the behaviour of the program.
```

##### Compliant solution

```
def foo(arg):
 print(arg)
```

### Resources

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

**📚 Risorse:**

#### Documentation

 - Python Documentation - [The pass statement](https://docs.python.org/3/reference/simple_stmts.html#the-pass-statement)

---

### Riga 142 🟡 🔴 CRITICAL

**🎯 Problema:** Change this default value to "None" and initialize this parameter inside the function/method.

| Campo | Valore |
|-------|--------|
| Regola | `python:S5717` - Function parameters' default values should not be modified or assigned |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 4-60 |
| Tags | bad-practice, pitfall |

**💻 Codice attuale:**
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
def myfunction(param=foo()): # foo is called only once, when the function is defined.
 ...
```

For the same reason, it is also a bad idea to store mutable default values in another object (ex: as an attribute). Multiple instances will then
share the same value and modifying one object will modify all of them.

This rule raises an issue when:

 - a default value is either modified in the function or assigned to anything other than a variable and it has one of the following types:
 
 [collections](https://docs.python.org/3/library/collections.html) module: deque, UserList, ChainMap, Counter, OrderedDict,
 defaultdict, UserDict. 

 
 - an attribute of a ...

**✅ Come risolvere:**

When a parameter default value is meant to be a mutable object, it is best to keep the parameter optional and instantiate the mutable object in the
function’s body directly.

##### Noncompliant code example

In the following example, the parameter "param" has `list()` as a default value. This list is created only once and then reused in every
call. Thus when appending `'a'` to this list in the body of the function, the next call will have `['a']` as a default
value.

```
def myfunction(param=list()): # Noncompliant: param is a list that gets mutated
 param.append('a') # modification of the default value.
 return param

print(myfunction()) # returns ['a']
print(myfunction()) # returns ['a', 'a']
print(myfunction()) # returns ['a', 'a', 'a']
```

##### Compliant solution

```
def myfunction(param=None):
 if param is None:
 param = list()
 param.append('a')
 return param

print(myfunction()) # returns ['a']
print(myfunction()) # returns ['a']
print(myfunction()) # returns ['a']
```

**📚 Risorse:**

#### Documentation

 - Python documentation - [Function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions) 

#### External coding guidelines

 - The Hitchhiker’s Guide to Python - [Common Gotchas](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)

---

## 📄 `app/utils/file_security.py`
**2 issue(s)** | Effort: 10min

### Riga 18 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "text".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 12-16 |
| Tags | unused |

**💻 Codice attuale:**
```python
     16:             # Try to decode as UTF-8 (or other common encodings if needed)
     17:             # If it fails, it's likely binary
 >>> 18:             text = file_content.decode('utf-8')
     19:         except UnicodeDecodeError:
     20:             try:
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

### Riga 25 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     23:                 try:
     24:                      text = file_content.decode('latin-1')
 >>> 25:                 except:
     26:                      return False
     27: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

## 📄 `app/schemas/schemas.py`
**2 issue(s)** | Effort: 16min

### Riga 76 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal '%d/%m/%Y' 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 33-43 |
| Tags | design |

**💻 Codice attuale:**
```python
     74:             raise ValueError("La data di rilascio non può essere vuota.")
     75:         try:
 >>> 76:             datetime.strptime(v, '%d/%m/%Y')
     77:         except ValueError:
     78:             raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

### Riga 78 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "Formato data non valido. Usare DD/MM/YYYY." 4 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 8min |
| Posizione | Colonne 29-73 |
| Tags | design |

**💻 Codice attuale:**
```python
     76:             datetime.strptime(v, '%d/%m/%Y')
     77:         except ValueError:
 >>> 78:             raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
     79:         return v
     80: 
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

## 📄 `desktop_app/views/edit_dialog.py`
**2 issue(s)** | Effort: 17min

### Riga 39 🟡 🟢 MINOR

**🎯 Problema:** Remove this redundant call.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7508` - Redundant collection functions should be avoided |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 35-39 |

**💻 Codice attuale:**
```python
     37:         self.categoria_edit = QComboBox()
     38: 
 >>> 39:         unique_categories = sorted(list(set(categories)))
     40:         self.categoria_edit.addItems(unique_categories)
     41: 
```

**❓ Perché è un problema:**

Python’s built-in functions for processing iterables such as `list()`, `tuple()`, `set()`, `sorted()`,
and `reversed()` are designed to accept any iterable as input. When these functions are unnecessarily nested within each other, it creates
redundant operations that add unnecessary computational overhead by creating intermediate data structures, decrease code readability and make the
intention less clear, and waste memory by duplicating data structures temporarily.

**✅ Come risolvere:**

When the outer function is given a collection but could have been given an iterable, the unnecessary conversion should be removed. For example, in
`sorted(list(iterable))`, the outer `sorted()` function can accept an iterable directly, so the inner `list()` call
is redundant and should be removed.

When the function `sorted()` is wrapped with `list()`, remove this conversion operation, since `sorted()` already
returns a list.

##### Noncompliant code example

```
iterable = (3, 1, 4, 1)

sorted_of_list = list(sorted(iterable)) # Noncompliant
```

##### Compliant solution

```
iterable = (3, 1, 4, 1)

sorted_of_list = sorted(iterable)
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [list](https://docs.python.org/3/library/stdtypes.html#list) 

 - Python Documentation - [tuple](https://docs.python.org/3/library/stdtypes.html#tuple) 

 - Python Documentation - [set](https://docs.python.org/3/library/stdtypes.html#set) 

 - Python Documentation - [sorted](https://docs.python.org/3/library/functions.html#sorted) 

 - Python Documentation - [reversed](https://docs.python.org/3/library/functions.html#reversed)

---

### Riga 49 🟡 🔴 CRITICAL

**🎯 Problema:** Define a constant instead of duplicating this literal "dd/MM/yyyy" 6 times.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1192` - String literals should not be duplicated |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 12min |
| Posizione | Colonne 49-61 |
| Tags | design |

**💻 Codice attuale:**
```python
     47: 
     48:         self.data_rilascio_edit = QDateEdit()
 >>> 49:         self.data_rilascio_edit.setDisplayFormat("dd/MM/yyyy")
     50:         rilascio_date = QDate.fromString(data['data_rilascio'], "dd/MM/yyyy")
     51:         self.data_rilascio_edit.setDate(rilascio_date if rilascio_date.isValid() else QDate.currentDate())
```

**❓ Perché è un problema:**

Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

#### Exceptions

No issue will be raised on:

 - duplicated string in decorators 

 - strings with less than 5 characters 

 - strings with only letters, numbers and underscores

**✅ Come risolvere:**

Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

##### Noncompliant code example

With the default threshold of 3:

```
def run():
 prepare("action1") # Noncompliant - "action1" is duplicated 3 times
 execute("action1")
 release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
 pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT']) # Compliant - strings inside decorators are ignored
def projects():
 pass
```

##### Compliant solution

```
ACTION_1 = "action1"

def run():
 prepare(ACTION_1)
 execute(ACTION_1)
 release(ACTION_1)
```

---

## 📄 `app/core/config.py`
**1 issue(s)** | Effort: 1min

### Riga 200 🟡 🟡 MAJOR

**🎯 Problema:** Fix the syntax of this issue suppression comment.

| Campo | Valore |
|-------|--------|
| Regola | `python:S7632` - Issue suppression comment should have the correct format |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 1min |
| Posizione | Colonne 4-76 |

**💻 Codice attuale:**
```python
     198: 
     199:     # Convenience properties to access mutable settings directly
 >>> 200:     # NOSONAR: UPPER_CASE naming is intentional for configuration properties
     201:     @property
     202:     def LICENSE_GITHUB_TOKEN(self): # NOSONAR
```

**❓ Perché è un problema:**

Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

#### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are suppressed might still
be reported, while malformed syntax might cause the analyzer to ignore more issues than intended. This creates confusion during code review and
reduces confidence in the analysis ...

**✅ Come risolvere:**

Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

 - Use `# NOSONAR` alone to suppress all issues on the line 

 - Use `# NOSONAR()` with empty parentheses to suppress all issues 

 - Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

 - Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

 - The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

 - Close all parentheses properly 

For `# noqa`:

 - Use `# noqa` alone to suppress all issues on the line 

 - Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

 - Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

 - Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

##### Noncompliant code example

```
def example():
 x = 1 # NOSONAR( # Noncompliant
 y = 2 # NOSONAR(a,) # Noncompliant
 z = 3 # NOSONAR)( # Noncompliant
 a = 4 # NOSONAR(python:S7632) # Noncompliant
 b = 5 # noqa: ,rule1 # Noncompliant
 c = 6 # noqa- rule1,rule2 # Noncompliant
```

##### Compliant solution

```
def example():
 x = 1 # NOSONAR
 y = 2 # NOSONAR(a)
 z = 3 # NOSONAR
 a = 4 # NOSONAR(S7632)
 b = 5 # noqa: rule1
 c = 6 # noqa: rule1,rule2
```

**📚 Risorse:**

#### Documentation

 - SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

 - Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

## 📄 `app/services/file_maintenance.py`
**1 issue(s)** | Effort: 22min

### Riga 16 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 32 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 22min |
| Posizione | Colonne 4-28 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     14: logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
     15: 
 >>> 16: def scan_and_archive_orphans(db: Session, database_path: str):
     17:     """
     18:     Bug 8 Fix: Identify files in 'DOCUMENTI DIPENDENTI' that are NOT in the database.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `app/services/certificate_logic.py`
**1 issue(s)** | Effort: 19min

### Riga 72 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 19min |
| Posizione | Colonne 4-33 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     70:     return "archiviato" if newer_cert_exists else "scaduto"
     71: 
 >>> 72: def get_bulk_certificate_statuses(db: Session, certificati: List[Certificato]) -&gt; Dict[int, str]:
     73:     """
     74:     Calcola lo stato per una lista di certificati in modo efficiente (bulk).
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/workers/file_scanner_worker.py`
**1 issue(s)** | Effort: 13min

### Riga 11 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 13min |
| Posizione | Colonne 8-11 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     9:         self.urls = urls
     10: 
 >>> 11:     def run(self):
     12:         files_to_process = []
     13:         for url in self.urls:
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/components/notification_center.py`
**1 issue(s)** | Effort: 5min

### Riga 85 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 12-18 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     83:                 elif isinstance(ts_str, datetime):
     84:                     time_str = ts_str.strftime("%H:%M")
 >>> 85:             except:
     86:                 pass
     87: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

## 📄 `desktop_app/components/toast.py`
**1 issue(s)** | Effort: 7min

### Riga 191 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 7min |
| Posizione | Colonne 8-24 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     189: 
     190:     @pyqtSlot(object, str, str, str, int)
 >>> 191:     def _show_toast_slot(self, parent, type, title, message, duration):
     192:         # Add to history
     193:         self.add_to_history(type, title, message)
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/chat/chat_controller.py`
**1 issue(s)** | Effort: 5min

### Riga 233 🟡 🔴 CRITICAL

**🎯 Problema:** Add a nested comment explaining why this method is empty, or complete the implementation.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1186` - Functions and methods should not be empty |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 8-26 |
| Tags | suspicious |

**💻 Codice attuale:**
```python
     231:         self.response_ready.emit(f"Errore: {error_msg}")
     232: 
 >>> 233:     def _on_worker_cleanup(self):
     234:         pass
     235: 
```

**❓ Perché è un problema:**

An empty method is generally considered bad practice and can lead to confusion, readability, and maintenance issues. Empty methods bring no
functionality and are misleading to others as they might think the method implementation fulfills a specific and identified requirement.

There are several reasons for a method not to have a body:

 - It is an unintentional omission, and should be fixed to prevent an unexpected behavior in production. 

 - It is not yet, or never will be, supported. In this case an exception should be thrown. 

 - The method is an intentionally-blank override. In this case a nested comment should explain the reason for the blank override. 

#### Exceptions

No issue will be raised when the empty method is abstract and meant to be overridden in a subclass, i.e. it is decorated with
`abc.abstractmethod`, `abc.abstractstaticmethod`, `abc.abstractclassmethod` or `abc.abstractproperty`.
Note however that these methods should normally have a docstring explaining how subc...

**✅ Come risolvere:**

##### Noncompliant code example

```
def shouldNotBeEmpty(): # Noncompliant - method is empty
 pass

def notImplemented(): # Noncompliant - method is empty
 pass

def emptyOnPurpose(): # Noncompliant - method is empty
 pass
```

##### Compliant solution

```
def shouldNotBeEmpty():
 doSomething()

def notImplemented():
 raise NotImplementedError("notImplemented() cannot be performed because ...")

def emptyOnPurpose():
 pass # comment explaining why the method is empty

def emptyOnPurposeBis():
 """
 Docstring explaining why this function is empty.
 """
```

---

## 📄 `desktop_app/workers/chat_worker.py`
**1 issue(s)** | Effort: 5min

### Riga 104 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     102:                         status_emoji = "⚠️" if expiry &lt;= today else "📅"
     103:                         results.append(f"{status_emoji} {c.get('nome')} - {c.get('nome_corso')}: Scade il {expiry_str}")
 >>> 104:                 except:
     105:                     continue
     106:             return results[:30]
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

## 📄 `desktop_app/services/voice_service.py`
**1 issue(s)** | Effort: 5min

### Riga 140 🟡 🔴 CRITICAL

**🎯 Problema:** Specify an exception class to catch or reraise the exception

| Campo | Valore |
|-------|--------|
| Regola | `python:S5754` - "SystemExit" should be re-raised |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 5min |
| Posizione | Colonne 12-18 |
| Tags | bad-practice, error-handling, suspicious |

**💻 Codice attuale:**
```python
     138:             try:
     139:                 os.remove(self._current_file)
 >>> 140:             except:
     141:                 pass
     142: 
```

**❓ Perché è un problema:**

A [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) exception is raised when [`sys.exit()`](https://docs.python.org/3/library/sys.html#sys.exit) is called. This exception is used to signal the interpreter to
exit. The exception is expected to propagate up until the program stops. It is possible to catch this exception in order to perform, for example,
clean-up tasks. It should, however, be raised again to allow the interpreter to exit as expected. Not re-raising such exception could lead to
undesired behaviour.

A [bare `except:` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement), i.e. an
`except` block without any exception class, is equivalent to [`except BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException). Both statements will catch every
exceptions, including `SystemExit`. It is recommended to catch instead a more specific exception. If it is not possible, the exception
should be raised again...

**✅ Come risolvere:**

Re-raise `SystemExit`, `BaseException` and any exceptions caught in a bare `except` clause.

##### Noncompliant code example

```
try:
 ...
except SystemExit: # Noncompliant: the SystemExit exception is not re-raised.
 pass

try:
 ...
except BaseException: # Noncompliant: BaseExceptions encompass SystemExit exceptions and should be re-raised.
 pass

try:
 ...
except: # Noncompliant: exceptions caught by this statement should be re-raised or a more specific exception should be caught.
 pass
```

##### Compliant solution

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

#### Documentation

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#id5) 

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html) 

 - Python Documentation - [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
 

 - CWE - [CWE-391, Unchecked Error Condition](https://cwe.mitre.org/data/definitions/391)

---

## 📄 `app/api/routers/stats.py`
**1 issue(s)** | Effort: 5min

### Riga 39 🟡 🟡 MAJOR

**🎯 Problema:** Remove this commented out code.

| Campo | Valore |
|-------|--------|
| Regola | `python:S125` - Sections of code should not be commented out |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-48 |
| Tags | unused |

**💻 Codice attuale:**
```python
     37:     compliance = 0
     38:     if total_certificati &gt; 0:
 >>> 39:         # Compliance = (Total - Scaduti) / Total
     40:         compliance = int(((total_certificati - scaduti) / total_certificati) * 100)
     41: 
```

**❓ Perché è un problema:**

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

**📝 Descrizione:**

### Why is this an issue?

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

## 📄 `desktop_app/views/stats_view.py`
**1 issue(s)** | Effort: 5min

### Riga 44 🟡 🟡 MAJOR

**🎯 Problema:** Extract this nested conditional expression into an independent statement.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3358` - Conditional expressions should not be nested |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 113-160 |
| Tags | confusing |

**💻 Codice attuale:**
```python
     42:         header.addStretch()
     43:         lbl_val = QLabel(f"{compliance_pct}%")
 >>> 44:         lbl_val.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {'#10B981' if compliance_pct &gt; 80 else '#F59E0B' if compliance_pct &gt; 50 else '#EF4444'};")
     45:         header.addWidget(lbl_val)
     46:         layout.addLayout(header)
```

**❓ Perché è un problema:**

Nested conditionals are hard to read and can make the order of operations complex to understand.

```
class Job:
 @property
 def readable_status(self):
 return "Running" if job.is_running else "Failed" if job.errors else "Succeeded" # Noncompliant
```

Instead, use another line to express the nested operation in a separate statement.

```
class Job:
 @property
 def readable_status(self):
 if job.is_running:
 return "Running"
 return "Failed" if job.errors else "Succeeded"
```

#### Exceptions

No issue is raised on conditional expressions in comprehensions.

```
job_statuses = ["Running" if job.is_running else "Failed" if job.errors else "Succeeded" for job in jobs] # Compliant by exception
```

**📝 Descrizione:**

### Why is this an issue?

Nested conditionals are hard to read and can make the order of operations complex to understand.

```
class Job:
 @property
 def readable_status(self):
 return "Running" if job.is_running else "Failed" if job.errors else "Succeeded" # Noncompliant
```

Instead, use another line to express the nested operation in a separate statement.

```
class Job:
 @property
 def readable_status(self):
 if job.is_running:
 return "Running"
 return "Failed" if job.errors else "Succeeded"
```

#### Exceptions

No issue is raised on conditional expressions in comprehensions.

```
job_statuses = ["Running" if job.is_running else "Failed" if job.errors else "Succeeded" for job in jobs] # Compliant by exception
```

---

## 📄 `desktop_app/api_client.py`
**1 issue(s)** | Effort: 20min

### Riga 91 🟡 🟡 MAJOR

**🎯 Problema:** Replace this generic exception class with a more specific one.

| Campo | Valore |
|-------|--------|
| Regola | `python:S112` - "Exception" and "BaseException" should not be raised |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 20min |
| Posizione | Colonne 18-88 |
| Tags | cwe, error-handling |

**💻 Codice attuale:**
```python
     89:             return response.json()
     90:         except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
 >>> 91:             raise Exception("Impossibile connettersi al server (Rete irraggiungibile).")
     92: 
     93:     def change_password(self, old_password, new_password):
```

**❓ Perché è un problema:**

Raising instances of [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception) and [`BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException) will have a negative impact on any code trying
to catch these exceptions.

From a consumer perspective, it is generally a best practice to only catch exceptions you intend to handle. Other exceptions should ideally not be
caught and let to propagate up the stack trace so that they can be dealt with appropriately. When a generic exception is thrown, it forces consumers
to catch exceptions they do not intend to handle, which they then have to re-raise.

Besides, when working with a generic type of exception, the only way to distinguish between multiple exceptions is to check their message, which is
error-prone and difficult to maintain. Legitimate exceptions may be unintentionally silenced and errors may be hidden.

For instance, if an exception such as `SystemExit` is caught and not re-raised, it will preve...

**✅ Come risolvere:**

To fix this issue, make sure to throw specific exceptions that are relevant to the context in which they arise. It is recommended to either:

 - Raise a specific [Built-in exception](https://docs.python.org/3/library/exceptions.html) when one matches. For example
 `TypeError` should be raised when the type of a parameter is not the one expected. 

 - Create a custom exception class deriving from `Exception` or one of its subclasses. 

##### Noncompliant code example

```
def check_value(value):
 if value &lt; 0:
 raise BaseException("Value cannot be negative") # Noncompliant: this will be difficult for consumers to handle
```

##### Compliant solution

```
def check_value(value):
 if value &lt; 0:
 raise ValueError("Value cannot be negative") # Compliant
```

**📚 Risorse:**

#### Documentation

 - Python Documentation - [Built-in exceptions](https://docs.python.org/3/library/exceptions.html#BaseException) 

 - PEP 352 - [Required Superclass for Exceptions](https://www.python.org/dev/peps/pep-0352/#exception-hierarchy-changes)

---

## 📄 `desktop_app/components/visuals.py`
**1 issue(s)** | Effort: 5min

### Riga 43 🟡 🟡 MAJOR

**🎯 Problema:** Remove this commented out code.

| Campo | Valore |
|-------|--------|
| Regola | `python:S125` - Sections of code should not be commented out |
| Categoria | MAINTAINABILITY |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 12-31 |
| Tags | unused |

**💻 Codice attuale:**
```python
     41:                 p['life'] = 0 # Arrived
     42:                 
 >>> 43:             # p['life'] -= 0.01
     44:             
     45:         self.particles = [p for p in self.particles if p['life'] &gt; 0]
```

**❓ Perché è un problema:**

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

**📝 Descrizione:**

### Why is this an issue?

Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never
executed, it quickly becomes out of date and invalid.

Commented-out code should be deleted and can be retrieved from source control history if required.

---

## 📄 `desktop_app/views/splash_screen.py`
**1 issue(s)** | Effort: 6min

### Riga 329 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 8-21 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     327:             self.detail_timer.stop()
     328: 
 >>> 329:     def update_status(self, message, progress=None):
     330:         clean_message = message.rstrip('.')
     331: 
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `app/services/document_locator.py`
**1 issue(s)** | Effort: 9min

### Riga 5 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 9min |
| Posizione | Colonne 4-17 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     3: from app.utils.file_security import sanitize_filename
     4: 
 >>> 5: def find_document(database_path: str, cert_data: dict) -&gt; str | None:
     6:     """
     7:     Locates the certificate PDF within the database directory structure.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---

## 📄 `desktop_app/services/time_service.py`
**1 issue(s)** | Effort: 5min

### Riga 75 🟡 🟢 MINOR

**🎯 Problema:** Replace the unused local variable "address" with "_".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 14-21 |
| Tags | unused |

**💻 Codice attuale:**
```python
     73:         data = b'\x1b' + 47 * b'\0'
     74:         client.sendto(data, (NTP_SERVER, 123))
 >>> 75:         data, address = client.recvfrom(1024)
     76:         if data:
     77:             t = struct.unpack('!12I', data)[10]
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `admin/offusca/rthook_pyqt6.py`
**1 issue(s)** | Effort: 5min

### Riga 16 🟡 🟢 MINOR

**🎯 Problema:** Remove the unused local variable "e".

| Campo | Valore |
|-------|--------|
| Regola | `python:S1481` - Unused local variables should be removed |
| Categoria | MAINTAINABILITY |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 26-27 |
| Tags | unused |

**💻 Codice attuale:**
```python
     14:         import PyQt6.QtNetwork
     15:         import PyQt6.QtPrintSupport
 >>> 16:     except ImportError as e:
     17:         # Ignora errori in fase di hook, verranno gestiti dal main se bloccanti
     18:         pass
```

**❓ Perché è un problema:**

An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

#### What is the potential impact?

Having unused local variables in your code can lead to several issues:

 - **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
 can distract from the main logic of the code. 

 - **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
 to confusion and misinterpretation of the code’s intent. 

 - **Potential for Bugs**: If a variable is declared but not used, it might indicate a bug or incomplete code. For example, if you
 declared a variable intending to use it in a calculation, but then ...

**✅ Come risolvere:**

The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

##### Noncompliant code example

```
def hello(name):
 message = "Hello " + name # Noncompliant - message is unused
 print(name)
for i in range(10): # Noncompliant - i is unused
 foo()
```

##### Compliant solution

```
def hello(name):
 message = "Hello " + name
 print(message)
for _ in range(10):
 foo()
```

---

## 📄 `app/utils/audit.py`
**1 issue(s)** | Effort: 6min

### Riga 8 🟡 🔴 CRITICAL

**🎯 Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

| Campo | Valore |
|-------|--------|
| Regola | `python:S3776` - Cognitive Complexity of functions should not be too high |
| Categoria | MAINTAINABILITY |
| Severità | CRITICAL |
| Effort | 6min |
| Posizione | Colonne 4-23 |
| Tags | brain-overload |

**💻 Codice attuale:**
```python
     6: from app.services.geo_service import GeoLocationService
     7: 
 >>> 8: def log_security_action(db: Session, user: Optional[User], action: str, details: str = None, category: str = None, request: Request = None, severity: str = "LOW", changes: str = None, device_id: str = None):
     9:     """
     10:     Logs a security-critical action to the database.
```

**❓ Perché è un problema:**

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

#### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

 - **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
 loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

 - **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
 becomes to keep the context in mind. 

 - **Method calls are free**
 A well-picked method name is a summary of multiple lines of code. A reader can first explore a
 high-level view of what the code is performing then go...

**✅ Come risolvere:**

Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

 - **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
 condition in a new function with an appropriate name will reduce cognitive load. 

 - **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
 things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

 - **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
 early. 

**Extraction of a complex condition in a new function.**

##### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if ((user.is_active and # +1 (if) +1 (nested) +1 (multiple conditions)
 user.has_profile) or # +1 (mixed operator)
 user.age &gt; 18 ):
 user.process()
```

##### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code of the
`process_eligible_users` function, which now only has a cognitive cost of 3.

```
def process_eligible_users(users):
 for user in users: # +1 (for)
 if is_eligible_user(user): # +1 (if) +1 (nested)
 user.process()

def is_eligible_user(user):
 return ((user.is_active and user.has_p...

**📚 Risorse:**

#### Documentation

 - Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

#### Articles & blog posts

 - Sonar Blog - 5 Clean Code Tips for Reducing
 Cognitive Complexity

---
