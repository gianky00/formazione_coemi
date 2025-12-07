# 🔴 RELIABILITY Issues

**Totale:** 1
**Tempo:** 5min

---

## 📄 `desktop_app/components/neural_3d.py` (1)

### Riga 13 🟡
**Problema:** Provide a seed for this random generator.

```python
     11: 
     12:         # Use new Generator API
 >>> 13:         self.rng = np.random.default_rng()
     14: 
     15:         # --- 3D State (Vectorized) ---
```

**❓ Perché:**
Data science and machine learning tasks make extensive use of random number generation. It may, for example, be used for:

  -  Model initialization
    
       Randomness is used to initialize the parameters of machine learning models. Initializing parameters with random values helps to break
      symmetry and prevents models from getting stuck in local optima during training. By providing a random starting point, the model can explore
      different regions of the parameter space and potentially find better solutions. 

      
  -  Regularization techniques
    
       Randomness is used t

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

  -

---
