# 🔥 Security Hotspots

**Totale:** 13

## Statistiche

| Rischio | Count |
|---------|-------|
| 🔴 HIGH | 4 |
| 🟡 MEDIUM | 8 |
| 🟢 LOW | 1 |

---

## 📁 WEAK-CRYPTOGRAPHY (7)
**Crittografia debole - random non sicuro**

### 🟡 `desktop_app/components/neural_3d.py:163`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     160:         # Or keep them for effect? Let's keep them but maybe less chance if warping
     161:         chance = 0.05 if self.warp_active else 0.15
     162: 
 >>> 163:         if self.connections and random.random() &lt; chance:
     164:             conn = random.choice(self.connections)
     165:             speed = random.uniform(0.05, 0.1) if self.warp_active else random.uniform(0.02, 0.05)
     166:             self.pulses.append([conn[0], conn[1], 0.0, speed])
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `desktop_app/components/neural_3d.py:164`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     161:         chance = 0.05 if self.warp_active else 0.15
     162: 
     163:         if self.connections and random.random() &lt; chance:
 >>> 164:             conn = random.choice(self.connections)
     165:             speed = random.uniform(0.05, 0.1) if self.warp_active else random.uniform(0.02, 0.05)
     166:             self.pulses.append([conn[0], conn[1], 0.0, speed])
     167: 
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `desktop_app/components/visuals.py:49`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     46:         self.update()
     47: 
     48:     def _emit_particles(self):
 >>> 49:         if random.random() &lt; 0.5:
     50:             self.particles.append({
     51:                 'x': 55, 
     52:                 'y': 20 + self.scan_line_y,
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `desktop_app/components/visuals.py:54`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     51:                 'x': 55, 
     52:                 'y': 20 + self.scan_line_y,
     53:                 'life': 1.0,
 >>> 54:                 'text': random.choice(["NOME", "DATA", "CF", "DOC"])
     55:             })
     56: 
     57:     def paintEvent(self, event):
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `desktop_app/views/splash_screen.py:108`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     105:              tip_x = self.width() * ratio
     106:              tip_y = self.height() / 2 + random.uniform(-5, 5)
     107:              
 >>> 108:              if random.random() &lt; 0.4:
     109:                  self.particles.append(Particle(tip_x, tip_y))
     110: 
     111:         self.particles = [p for p in self.particles if p.update()]
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `tools/prepare_installer_assets.py:52`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     49:             x = random.uniform(0, width)
     50:             y = random.uniform(0, height)
     51:             s = random.uniform(0.5, 2.5)
 >>> 52:             opacity = random.randint(100, 255)
     53:             # Some stars are blueish, some white
     54:             if random.random() &gt; 0.8:
     55:                 painter.setBrush(QColor(147, 197, 253, opacity))
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

### 🟡 `tools/prepare_installer_assets.py:54`

**Problema:** Make sure that using this pseudorandom number generator is safe here.

```python
     51:             s = random.uniform(0.5, 2.5)
     52:             opacity = random.randint(100, 255)
     53:             # Some stars are blueish, some white
 >>> 54:             if random.random() &gt; 0.8:
     55:                 painter.setBrush(QColor(147, 197, 253, opacity))
     56:             else:
     57:                 painter.setBrush(QColor(255, 255, 255, opacity))
```

**❓ Rischio:**
PRNGs are algorithms that produce sequences of numbers that only approximate true randomness. While they are suitable for applications like
simulations or modeling, they are not appropriate for security-sensitive contexts because their outputs can be predictable if the internal state is
known.

In contrast, cryptographically secure pseudorandom number generators (CSPRNGs) are designed to be secure against prediction attacks. CSPRNGs use
cryptographic algorithms to ensure that the generated seque

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Only use random number generators which are recommended by
  OWASP or any other trusted organization. 

  -  Use the generated random values only once. 

  -  You should not expose the generated random value. If you have to store it, make sure that the database or file is secure. 

### Sensitive Code Example

```
import random

random.getrandbits(1) # Sensitive
random.randint(0,9) # Sensitive
random.random()  # Sensitive

# the following functions are sadly used to generate salt by selecting characters in a string ex: "abcdefghijk"...
random.sample

---

## 📁 AUTH (4)
**Autenticazione - Password/API key hardcoded**

### 🔴 `admin/call_list_IA.py:5`

**Problema:** "api_key" detected here, make sure this is not a hard-coded secret.

```python
     2: 
     3: # --- CONFIGURAZIONE ---
     4: # Incolla la tua API Key qui sotto tra le virgolette
 >>> 5: api_key = "INSERISCI_API_KEY"
     6: 
     7: genai.configure(api_key=api_key)
     8: 
```

**❓ Rischio:**
Because it is easy to extract strings from an application source code or binary, secrets should not be hard-coded. This is particularly true for
applications that are distributed or that are open-source.

In the past, it has led to the following vulnerabilities:

  -  [CVE-2022-25510](https://www.cve.org/CVERecord?id=CVE-2022-25510) 

  -  [CVE-2021-42635](https://www.cve.org/CVERecord?id=CVE-2021-42635) 

Secrets should be stored outside of the source code in a configuration file or a managemen

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Store the secret in a configuration file that is not pushed to the code repository. 

  -  Use your cloud provider’s service for managing secrets. 

  -  If a secret has been disclosed through the source code: revoke it and create a new one. 

### Sensitive Code Example

```
import requests

API_KEY = "1234567890abcdef"  # Hard-coded secret (bad practice)

def send_api_request(data):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    return requests.post("https://api.example.com", headers=headers, data=data)
```

### Compliant S

---

### 🔴 `app/api/routers/users.py:45`

**Problema:** "password" detected here, review this potentially hard-coded credential.

```python
     42:         )
     43: 
     44:     # Force default password to "primoaccesso"
 >>> 45:     default_password = "primoaccesso"
     46: 
     47:     user = UserModel(
     48:         username=user_in.username,
```

**❓ Rischio:**
Because it is easy to extract strings from an application source code or binary, credentials should not be hard-coded. This is particularly true
for applications that are distributed or that are open-source.

In the past, it has led to the following vulnerabilities:

  -  [CVE-2019-13466](https://www.cve.org/CVERecord?id=CVE-2019-13466) 

  -  [CVE-2018-15389](https://www.cve.org/CVERecord?id=CVE-2018-15389) 

Credentials should be stored outside of the code in a configuration file, a database, 

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Store the credentials in a configuration file that is not pushed to the code repository. 

  -  Store the credentials in a database. 

  -  Use your cloud provider’s service for managing secrets. 

  -  If a password has been disclosed through the source code: change it. 

### Sensitive Code Example

```
username = 'admin'
password = 'admin' # Sensitive
usernamePassword = 'user=admin&amp;password=admin' # Sensitive
```

### Compliant Solution

```
import os

username = os.getenv("username") # Compliant
password = os.getenv("password") # Compliant
u

---

### 🔴 `app/core/config.py:120`

**Problema:** "password" detected here, review this potentially hard-coded credential.

```python
     117: 
     118:         self._defaults = {
     119:             "DATABASE_PATH": None,
 >>> 120:             "FIRST_RUN_ADMIN_PASSWORD": "prova",
     121:             # Default key is also obfuscated to avoid scanners.
     122:             "GEMINI_API_KEY_ANALYSIS": "obf:TUFxc2Y0TkVlQHRhY015Z0NwOFk1VDRCLnl6YUlB",
     123:             # Default dummy key for chat, obfuscated.
```

**❓ Rischio:**
Because it is easy to extract strings from an application source code or binary, credentials should not be hard-coded. This is particularly true
for applications that are distributed or that are open-source.

In the past, it has led to the following vulnerabilities:

  -  [CVE-2019-13466](https://www.cve.org/CVERecord?id=CVE-2019-13466) 

  -  [CVE-2018-15389](https://www.cve.org/CVERecord?id=CVE-2018-15389) 

Credentials should be stored outside of the code in a configuration file, a database, 

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Store the credentials in a configuration file that is not pushed to the code repository. 

  -  Store the credentials in a database. 

  -  Use your cloud provider’s service for managing secrets. 

  -  If a password has been disclosed through the source code: change it. 

### Sensitive Code Example

```
username = 'admin'
password = 'admin' # Sensitive
usernamePassword = 'user=admin&amp;password=admin' # Sensitive
```

### Compliant Solution

```
import os

username = os.getenv("username") # Compliant
password = os.getenv("password") # Compliant
u

---

### 🔴 `app/core/config.py:129`

**Problema:** "password" detected here, review this potentially hard-coded credential.

```python
     126:             "SMTP_HOST": "smtps.aruba.it",
     127:             "SMTP_PORT": 465,
     128:             "SMTP_USER": "giancarlo.allegretti@coemi.it",
 >>> 129:             "SMTP_PASSWORD": "Coemi@2025!!@Gianca",
     130:             "EMAIL_RECIPIENTS_TO": "gianky.allegretti@gmail.com",
     131:             "EMAIL_RECIPIENTS_CC": "gianky.allegretti@gmail.com",
     132:             "ALERT_THRESHOLD_DAYS": 60,
```

**❓ Rischio:**
Because it is easy to extract strings from an application source code or binary, credentials should not be hard-coded. This is particularly true
for applications that are distributed or that are open-source.

In the past, it has led to the following vulnerabilities:

  -  [CVE-2019-13466](https://www.cve.org/CVERecord?id=CVE-2019-13466) 

  -  [CVE-2018-15389](https://www.cve.org/CVERecord?id=CVE-2018-15389) 

Credentials should be stored outside of the code in a configuration file, a database, 

**✅ Come risolvere:**
### Recommended Secure Coding Practices

  -  Store the credentials in a configuration file that is not pushed to the code repository. 

  -  Store the credentials in a database. 

  -  Use your cloud provider’s service for managing secrets. 

  -  If a password has been disclosed through the source code: change it. 

### Sensitive Code Example

```
username = 'admin'
password = 'admin' # Sensitive
usernamePassword = 'user=admin&amp;password=admin' # Sensitive
```

### Compliant Solution

```
import os

username = os.getenv("username") # Compliant
password = os.getenv("password") # Compliant
u

---

## 📁 DOS (1)
**Denial of Service - Regex vulnerabile (ReDoS)**

### 🟡 `app/services/ai_extraction.py:187`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     184:     text = text.strip()
     185:     
     186:     # Fast path: checks if wrapped in markdown
 >>> 187:     match = re.search(r'```json\s*(.*?)```', text, re.DOTALL)
     188:     if match:
     189:         text = match.group(1).strip()
     190:     
```

**❓ Rischio:**
Most of the regular expression engines use `backtracking` to try all possible execution paths of the regular expression when evaluating
an input, in some cases it can cause performance issues, called `catastrophic backtracking` situations. In the worst case, the complexity
of the regular expression is exponential in the size of the input, this means that a small carefully-crafted input (like 20 chars) can trigger
`catastrophic backtracking` and cause a denial of service of the application. Super

**✅ Come risolvere:**
### Recommended Secure Coding Practices

To avoid `catastrophic backtracking` situations, make sure that none of the following conditions apply to your regular expression.

In all of the following cases, catastrophic backtracking can only happen if the problematic part of the regex is followed by a pattern that can
fail, causing the backtracking to actually happen. Note that when performing a full match (e.g. using `re.fullmatch`), the end of the regex
counts as a pattern that can fail because it will only succeed when the end of the string is reached.

  -  If you have a non-possessive repeti

---

## 📁 OTHERS (1)
**Altri problemi di sicurezza**

### 🟢 `.github/workflows/main_ci.yml:96`

**Problema:** Use full commit SHA hash for this dependency.

```yaml
     93:           fi
     94: 
     95:       - name: SonarCloud Scan
 >>> 96:         uses: SonarSource/sonarqube-scan-action@v5.0.0
     97:         env:
     98:           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     99:           SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**❓ Rischio:**
GitHub Actions workflows can leverage actions and reusable workflows created by others. These external actions can be used to perform various
tasks, such as checking out code, building applications, and deploying artifacts. If your workflow uses a third-party action or a workflow without
referencing to a specific commit hash, you are at risk of pulling in code that you have not reviewed.

**✅ Come risolvere:**
### Recommended Secure Coding Practices

It is recommended to use the complete commit hash to pin the version when using third-party actions and workflows. This is the only way to ensure
that the code you are pulling into your action is the one you have reviewed.

### Sensitive Code Example

```
name: Example

on:
  pull_request:

jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: docs/example-action@main  # Sensitive
```

### Compliant Solution

Use the full commit hash as a reference to pin the version.

```
name: Example

on:
  pull_request:

jobs:
  example:
    runs-on: 

---
