# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 45 issues
**Tempo:** 3h

---

## 📄 `guide_frontend/src/pages/Glossary.jsx`

### Riga 3 🟡 🟢
**Problema:** Remove this unused import of 'Note'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     1: import React from 'react';
     2: import GuideCard from '../components/ui/GuideCard';
 >>> 3: import Note from '../components/ui/Note';
     4: import { Book, Tag, Hash, FileQuestion } from 'lucide-react';
     5: 
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'Tag'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Book, Tag, Hash, FileQuestion } from 'lucide-react';
     5: 
     6: const Glossary = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'Hash'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Book, Tag, Hash, FileQuestion } from 'lucide-react';
     5: 
     6: const Glossary = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'FileQuestion'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Book, Tag, Hash, FileQuestion } from 'lucide-react';
     5: 
     6: const Glossary = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 53 🟡 🟡
**Problema:** Do not use Array index in keys
**Regola:** `javascript:S6479` - JSX list components should not use array indexes as key

```jsx
     51:       &lt;div className="grid grid-cols-1 gap-6"&gt;
     52:         {terms.map((item, idx) =&gt; (
 >>> 53:             &lt;GuideCard key={idx} className="hover:border-blue-300 transition-colors group"&gt;
     54:                 &lt;h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2 group-hover:text-blue-700"&gt;
     55:                     &lt;Book size={18} className="text-gray-400 group-hover:text-blue-500"/&gt;
```

**❓ Perché è un problema:**
To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. Avoid array indexes since the order of the items may change, which will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

```
function Blog(props) {
  return (
    &lt;ul&gt;
      {props.posts.map((post, index) =&gt;
        &lt;li key={index}&gt; &lt;!-- Noncompliant: When 'posts' are reordered, React will need to recreate the list DOM --&gt;
          {post.title}
        &lt;/li&gt;
      )}
    &lt;/ul&gt;
  );
}
```

To fix it, use a string or a number that uniquely identifies the list item. The key must be unique am

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [no-array-index-key](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/no-array-index-key.md) 

  -  React Documentation - [Rendering lists](https://react.dev/learn/rendering-lists#rules-of-keys) 

  -  React Documentation - [Recursing On Children](https://reactjs.org/docs/reconciliation.html#recursing-on-children) 

  -  MDN web docs - [Crypto: randomUUID() method](https:

---

## 📄 `guide_frontend/src/components/DashboardSimulator.jsx`

### Riga 109 🟡 🟡
**Problema:** Use <input type="button">, <input type="image">, <input type="reset">, <input type="submit">, or <button> instead of the "button" role to ensure accessibility across all devices.
**Regola:** `javascript:S6819` - Prefer tag over ARIA role

```jsx
     107:       {/* Table Header */}
     108:       &lt;div className="grid grid-cols-5 bg-gray-100 p-3 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200"&gt;
 >>> 109:         &lt;div
 >>> 110:             className="col-span-1 cursor-pointer hover:text-gray-700"
 >>> 111:             onClick={() =&gt; handleSort('dipendente')}
 >>> 112:             onKeyDown={(e) =&gt; handleKeyDown(e, 'dipendente')}
 >>> 113:             role="button"
 >>> 114:             tabIndex={0}
 >>> 115:         &gt;
     116:             Dipendente {getSortIcon('dipendente')}
     117:         &lt;/div&gt;
```

**❓ Perché è un problema:**
ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like `span` or `div`) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

For example, instead of using a div element with a button role (`<div role="button">Click me</div>`), you should just use a
button element (`<button>Click me</button>`).

Semantic HTML tags are generally preferred over ARIA roles for accessibility due to their built-in functionality, universal support by browsers and
assistive technologies, simplicity, and maintainability. They come with inherent behaviors and keyboard interactions, reducing the need for additional
JavaScript.

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [prefer-tag-over-role](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/prefer-tag-over-role.md) 

  -  MDN web docs - Using ARIA: Roles, states, and
  properties 

  -  MDN web docs - [ARIA roles (Reference)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles) 

### Standards

  -  W3C - [Accessible Rich Internet Applications (WAI-ARIA) 1.2](h

---

### Riga 118 🟡 🟡
**Problema:** Use <input type="button">, <input type="image">, <input type="reset">, <input type="submit">, or <button> instead of the "button" role to ensure accessibility across all devices.
**Regola:** `javascript:S6819` - Prefer tag over ARIA role

```jsx
     116:             Dipendente {getSortIcon('dipendente')}
     117:         &lt;/div&gt;
 >>> 118:         &lt;div
 >>> 119:             className="col-span-1 cursor-pointer hover:text-gray-700"
 >>> 120:             onClick={() =&gt; handleSort('corso')}
 >>> 121:             onKeyDown={(e) =&gt; handleKeyDown(e, 'corso')}
 >>> 122:             role="button"
 >>> 123:             tabIndex={0}
 >>> 124:         &gt;
     125:             Documento {getSortIcon('corso')}
     126:         &lt;/div&gt;
```

**❓ Perché è un problema:**
ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like `span` or `div`) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

For example, instead of using a div element with a button role (`<div role="button">Click me</div>`), you should just use a
button element (`<button>Click me</button>`).

Semantic HTML tags are generally preferred over ARIA roles for accessibility due to their built-in functionality, universal support by browsers and
assistive technologies, simplicity, and maintainability. They come with inherent behaviors and keyboard interactions, reducing the need for additional
JavaScript.

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [prefer-tag-over-role](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/prefer-tag-over-role.md) 

  -  MDN web docs - Using ARIA: Roles, states, and
  properties 

  -  MDN web docs - [ARIA roles (Reference)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles) 

### Standards

  -  W3C - [Accessible Rich Internet Applications (WAI-ARIA) 1.2](h

---

### Riga 127 🟡 🟡
**Problema:** Use <input type="button">, <input type="image">, <input type="reset">, <input type="submit">, or <button> instead of the "button" role to ensure accessibility across all devices.
**Regola:** `javascript:S6819` - Prefer tag over ARIA role

```jsx
     125:             Documento {getSortIcon('corso')}
     126:         &lt;/div&gt;
 >>> 127:         &lt;div
 >>> 128:             className="col-span-1 cursor-pointer hover:text-gray-700"
 >>> 129:             onClick={() =&gt; handleSort('data')}
 >>> 130:             onKeyDown={(e) =&gt; handleKeyDown(e, 'data')}
 >>> 131:             role="button"
 >>> 132:             tabIndex={0}
 >>> 133:         &gt;
     134:             Data Ril. {getSortIcon('data')}
     135:         &lt;/div&gt;
```

**❓ Perché è un problema:**
ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like `span` or `div`) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

For example, instead of using a div element with a button role (`<div role="button">Click me</div>`), you should just use a
button element (`<button>Click me</button>`).

Semantic HTML tags are generally preferred over ARIA roles for accessibility due to their built-in functionality, universal support by browsers and
assistive technologies, simplicity, and maintainability. They come with inherent behaviors and keyboard interactions, reducing the need for additional
JavaScript.

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [prefer-tag-over-role](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/prefer-tag-over-role.md) 

  -  MDN web docs - Using ARIA: Roles, states, and
  properties 

  -  MDN web docs - [ARIA roles (Reference)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles) 

### Standards

  -  W3C - [Accessible Rich Internet Applications (WAI-ARIA) 1.2](h

---

### Riga 136 🟡 🟡
**Problema:** Use <input type="button">, <input type="image">, <input type="reset">, <input type="submit">, or <button> instead of the "button" role to ensure accessibility across all devices.
**Regola:** `javascript:S6819` - Prefer tag over ARIA role

```jsx
     134:             Data Ril. {getSortIcon('data')}
     135:         &lt;/div&gt;
 >>> 136:         &lt;div
 >>> 137:             className="col-span-1 cursor-pointer hover:text-gray-700"
 >>> 138:             onClick={() =&gt; handleSort('scadenza')}
 >>> 139:             onKeyDown={(e) =&gt; handleKeyDown(e, 'scadenza')}
 >>> 140:             role="button"
 >>> 141:             tabIndex={0}
 >>> 142:         &gt;
     143:             Scadenza {getSortIcon('scadenza')}
     144:         &lt;/div&gt;
```

**❓ Perché è un problema:**
ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like `span` or `div`) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

For example, instead of using a div element with a button role (`<div role="button">Click me</div>`), you should just use a
button element (`<button>Click me</button>`).

Semantic HTML tags are generally preferred over ARIA roles for accessibility due to their built-in functionality, universal support by browsers and
assistive technologies, simplicity, and maintainability. They come with inherent behaviors and keyboard interactions, reducing the need for additional
JavaScript.

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [prefer-tag-over-role](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/prefer-tag-over-role.md) 

  -  MDN web docs - Using ARIA: Roles, states, and
  properties 

  -  MDN web docs - [ARIA roles (Reference)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles) 

### Standards

  -  W3C - [Accessible Rich Internet Applications (WAI-ARIA) 1.2](h

---

## 📄 `guide_frontend/src/pages/ImportGuide.jsx`

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'Step'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import Step from '../components/ui/Step';
     5: import ImportSimulator from '../components/ImportSimulator';
     6: import { UploadCloud, FolderOpen, AlertTriangle } from 'lucide-react';
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 6 🟡 🟢
**Problema:** Remove this unused import of 'AlertTriangle'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     4: import Step from '../components/ui/Step';
     5: import ImportSimulator from '../components/ImportSimulator';
 >>> 6: import { UploadCloud, FolderOpen, AlertTriangle } from 'lucide-react';
     7: 
     8: const ImportGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 6 🟡 🟢
**Problema:** 'lucide-react' imported multiple times.
**Regola:** `javascript:S3863` - Imports from the same module should be merged

```jsx
     4: import Step from '../components/ui/Step';
     5: import ImportSimulator from '../components/ImportSimulator';
 >>> 6: import { UploadCloud, FolderOpen, AlertTriangle } from 'lucide-react';
     7: 
     8: const ImportGuide = () =&gt; {
```

**❓ Perché è un problema:**
Having the same module imported multiple times can affect code readability and maintainability. It makes hard to identify which modules are being
used.

```
import { B1 } from 'b';
import { B2 } from 'b'; // Noncompliant: there is already an import from module 'b'.
```

Instead, one should consolidate the imports from the same module into a single statement. By consolidating all imports from the same module in a
single `import` statement, the code becomes more concise and easier to read, as there is only one import statement to keep track of.
Additionally, it can make it easier to identify which modules are used in the code.

```
import { B1, B2 } from 'b';
```

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-import](https://github.com/import-js/eslint-plugin-import) - Rule [no-duplicates](https://github.com/import-js/eslint-plugin-import/blob/HEAD/docs/rules/no-duplicates.md) 

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

  -  MDN web docs - [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

---

### Riga 89 🟡 🟢
**Problema:** 'lucide-react' imported multiple times.
**Regola:** `javascript:S3863` - Imports from the same module should be merged

```jsx
     87: };
     88: 
 >>> 89: import { FileText } from 'lucide-react'; // Fix missing import for icon used in GuideCard
     90: export default ImportGuide;
     91: 
```

**❓ Perché è un problema:**
Having the same module imported multiple times can affect code readability and maintainability. It makes hard to identify which modules are being
used.

```
import { B1 } from 'b';
import { B2 } from 'b'; // Noncompliant: there is already an import from module 'b'.
```

Instead, one should consolidate the imports from the same module into a single statement. By consolidating all imports from the same module in a
single `import` statement, the code becomes more concise and easier to read, as there is only one import statement to keep track of.
Additionally, it can make it easier to identify which modules are used in the code.

```
import { B1, B2 } from 'b';
```

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-import](https://github.com/import-js/eslint-plugin-import) - Rule [no-duplicates](https://github.com/import-js/eslint-plugin-import/blob/HEAD/docs/rules/no-duplicates.md) 

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

  -  MDN web docs - [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

---

## 📄 `guide_frontend/src/pages/SecurityGuide.jsx`

### Riga 4 🟡 🟢
**Problema:** 'lucide-react' imported multiple times.
**Regola:** `javascript:S3863` - Imports from the same module should be merged

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Shield, Lock, Eye, Key, FileWarning, Fingerprint } from 'lucide-react';
     5: 
     6: const SecurityGuide = () =&gt; {
```

**❓ Perché è un problema:**
Having the same module imported multiple times can affect code readability and maintainability. It makes hard to identify which modules are being
used.

```
import { B1 } from 'b';
import { B2 } from 'b'; // Noncompliant: there is already an import from module 'b'.
```

Instead, one should consolidate the imports from the same module into a single statement. By consolidating all imports from the same module in a
single `import` statement, the code becomes more concise and easier to read, as there is only one import statement to keep track of.
Additionally, it can make it easier to identify which modules are used in the code.

```
import { B1, B2 } from 'b';
```

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-import](https://github.com/import-js/eslint-plugin-import) - Rule [no-duplicates](https://github.com/import-js/eslint-plugin-import/blob/HEAD/docs/rules/no-duplicates.md) 

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

  -  MDN web docs - [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

---

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'Shield'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Shield, Lock, Eye, Key, FileWarning, Fingerprint } from 'lucide-react';
     5: 
     6: const SecurityGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 4 🟡 🟢
**Problema:** Remove this unused import of 'Fingerprint'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
 >>> 4: import { Shield, Lock, Eye, Key, FileWarning, Fingerprint } from 'lucide-react';
     5: 
     6: const SecurityGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 92 🟡 🟢
**Problema:** 'lucide-react' imported multiple times.
**Regola:** `javascript:S3863` - Imports from the same module should be merged

```jsx
     90: };
     91: 
 >>> 92: import { Zap } from 'lucide-react'; // Fix missing import
     93: export default SecurityGuide;
     94: 
```

**❓ Perché è un problema:**
Having the same module imported multiple times can affect code readability and maintainability. It makes hard to identify which modules are being
used.

```
import { B1 } from 'b';
import { B2 } from 'b'; // Noncompliant: there is already an import from module 'b'.
```

Instead, one should consolidate the imports from the same module into a single statement. By consolidating all imports from the same module in a
single `import` statement, the code becomes more concise and easier to read, as there is only one import statement to keep track of.
Additionally, it can make it easier to identify which modules are used in the code.

```
import { B1, B2 } from 'b';
```

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-import](https://github.com/import-js/eslint-plugin-import) - Rule [no-duplicates](https://github.com/import-js/eslint-plugin-import/blob/HEAD/docs/rules/no-duplicates.md) 

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

  -  MDN web docs - [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

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

### Riga 573 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 22 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     571: 
     572: @router.put("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 573: def update_certificato(
     574:     certificato_id: int,
     575:     certificato: CertificatoAggiornamentoSchema,
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

### Riga 702 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     700: 
     701: @router.post("/dipendenti/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
 >>> 702: async def import_dipendenti_csv(
     703:     file: UploadFile = File(...),
     704:     db: Session = Depends(get_db),
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

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 72 🟡 🟢
**Problema:** Prefer `globalThis` over `window`.
**Regola:** `javascript:S7764` - Use "globalThis" instead of "window", "self", or "global"

```jsx
     70:   useEffect(() =&gt; {
     71:     // Prefer globalThis over window for environment agnosticism (e.g. server-side rendering support, though not used here)
 >>> 72:     const globalContext = globalThis || window;
     73: 
     74:     if (globalContext.qt &amp;&amp; globalContext.qt.webChannelTransport) {
```

**❓ Perché è un problema:**
`globalThis` is the standardized way to access the global object across all JavaScript environments. Before `globalThis`,
developers had to use different global references depending on the environment:

  -  `window` in browsers 

  -  `global` in Node.js 

  -  `self` in Web Workers 

This created compatibility issues when code needed to run in multiple environments. Using environment-specific globals makes code less portable and
harder to maintain.

`globalThis` was introduced in ES2020 as a unified solution that works consistently across all JavaScript environments. It provides the
same global object reference regardless of whether your code runs in a browser, Node.js, or Web Worker.

Using `globalThis` makes your code more future-proof and eliminates the need for environment detection 

---

### Riga 74 🟡 🟡
**Problema:** Prefer using an optional chain expression instead, as it's more concise and easier to read.
**Regola:** `javascript:S6582` - Optional chaining should be preferred

```jsx
     72:     const globalContext = globalThis || window;
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
 >>> 77:       const channel = new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(channel) {
     78:         if (channel?.objects?.bridge) {
     79:             setBridge(channel.objects.bridge);
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

## 📄 `guide_frontend/src/pages/ValidationGuide.jsx`

### Riga 2 🟡 🟢
**Problema:** Remove this unused import of 'GuideCard'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     1: import React from 'react';
 >>> 2: import GuideCard from '../components/ui/GuideCard';
     3: import Note from '../components/ui/Note';
     4: import Step from '../components/ui/Step';
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 6 🟡 🟢
**Problema:** Remove this unused import of 'Database'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     4: import Step from '../components/ui/Step';
     5: import ValidationSimulator from '../components/ValidationSimulator';
 >>> 6: import { Database, CheckCircle, AlertOctagon } from 'lucide-react';
     7: 
     8: const ValidationGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 6 🟡 🟢
**Problema:** Remove this unused import of 'AlertOctagon'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     4: import Step from '../components/ui/Step';
     5: import ValidationSimulator from '../components/ValidationSimulator';
 >>> 6: import { Database, CheckCircle, AlertOctagon } from 'lucide-react';
     7: 
     8: const ValidationGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

## 📄 `guide_frontend/src/components/Layout.jsx`

### Riga 8 🟡 🟢
**Problema:** Remove the declaration of the unused 'location' variable.
**Regola:** `javascript:S1481` - Unused local variables and functions should be removed

```jsx
     6: 
     7: const Layout = () =&gt; {
 >>> 8:   const location = useLocation();
     9: 
     10:   return (
```

**❓ Perché è un problema:**
If a local variable or a local function is declared but not used, it is dead code and should be removed. Doing so will improve maintainability
because developers will not wonder what the variable or function is used for.

### What is the potential impact?

### Dead code

An unused variable or local function usually occurs because some logic is no longer required after a code change. In that case, such code becomes
unused and never executed.

Also, if you are writing code for the front-end, every unused variable or function remaining in your codebase is just extra bytes you have to send
over the wire to your users. Unused code bloats your codebase unnecessarily and impacts the performance of your application.

### Wrong logic

It could happen that due to a bad copy-paste or autocompletion, 

**✅ Come risolvere:**
Usually, the fix for this issue is straightforward, you just need to remove the unused variable declaration, or its name from the declaration
statement if it is declared along with other variables.

### Noncompliant code example

```
function numberOfMinutes(hours) {
  var seconds = 0;   // seconds is never used
  return hours * 60;
}
```

### Compliant solution

```
function numberOfMinutes(hours) {
  return hours * 60;
}
```

### Noncompliant code example

When an array destructuring is used and some element of the array is never referenced, one might simply remove it from the destructuring.

```
const [_, params] = url.split(path);
```

### Compliant solution

```
const [, params] = url.split(path);
```

**📚 Risorse:**
### Documentation

  -  MDN web docs - [Destructuring assignment / Ignoring some values](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment#ignoring_some_returned_values) 

### Articles & blog posts

  -  Phil Nash, Common TypeScript
  Issues Nº 3: unused local variables and functions 

  -   David Glasser, An interesting kind of JavaScript
  memory leak

---

### Riga 8 🟡 🟡
**Problema:** Remove this useless assignment to variable "location".
**Regola:** `javascript:S1854` - Unused assignments should be removed

```jsx
     6: 
     7: const Layout = () =&gt; {
 >>> 8:   const location = useLocation();
     9: 
     10:   return (
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

## 📄 `guide_frontend/src/pages/EmployeesGuide.jsx`

### Riga 5 🟡 🟢
**Problema:** Remove this unused import of 'Users'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     3: import Note from '../components/ui/Note';
     4: import Step from '../components/ui/Step';
 >>> 5: import { Users, FileSpreadsheet, UserPlus, Link } from 'lucide-react';
     6: 
     7: const EmployeesGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

### Riga 5 🟡 🟢
**Problema:** Remove this unused import of 'FileSpreadsheet'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     3: import Note from '../components/ui/Note';
     4: import Step from '../components/ui/Step';
 >>> 5: import { Users, FileSpreadsheet, UserPlus, Link } from 'lucide-react';
     6: 
     7: const EmployeesGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

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

## 📄 `guide_frontend/src/components/ImportSimulator.jsx`

### Riga 95 🟡 🟡
**Problema:** Use <input type="button">, <input type="image">, <input type="reset">, <input type="submit">, or <button> instead of the "button" role to ensure accessibility across all devices.
**Regola:** `javascript:S6819` - Prefer tag over ARIA role

```jsx
     93:               className="text-center w-full max-w-md"
     94:             &gt;
 >>> 95:               &lt;div
 >>> 96:                 onClick={simulateProcess}
 >>> 97:                 onKeyDown={handleKeyDown}
 >>> 98:                 role="button"
 >>> 99:                 tabIndex={0}
 >>> 100:                 className="border-2 border-dashed border-blue-300 rounded-xl p-10 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-500 transition-all cursor-pointer group"
 >>> 101:               &gt;
     102:                 &lt;UploadCloud size={48} className="mx-auto text-blue-400 group-hover:text-blue-600 mb-4 transition-colors" /&gt;
     103:                 &lt;h3 className="text-lg font-bold text-gray-700 mb-2"&gt;Trascina qui i tuoi file PDF&lt;/h3&gt;
```

**❓ Perché è un problema:**
ARIA (Accessible Rich Internet Applications) roles are used to make web content and web applications more accessible to people with disabilities.
However, you should not use an ARIA role on a generic element (like `span` or `div`) if there is a semantic HTML tag with
similar functionality, just use that tag instead.

For example, instead of using a div element with a button role (`<div role="button">Click me</div>`), you should just use a
button element (`<button>Click me</button>`).

Semantic HTML tags are generally preferred over ARIA roles for accessibility due to their built-in functionality, universal support by browsers and
assistive technologies, simplicity, and maintainability. They come with inherent behaviors and keyboard interactions, reducing the need for additional
JavaScript.

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [prefer-tag-over-role](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/prefer-tag-over-role.md) 

  -  MDN web docs - Using ARIA: Roles, states, and
  properties 

  -  MDN web docs - [ARIA roles (Reference)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles) 

### Standards

  -  W3C - [Accessible Rich Internet Applications (WAI-ARIA) 1.2](h

---

## 📄 `guide_frontend/src/components/ui/Accordion.jsx`

### Riga 58 🟡 🟡
**Problema:** Do not use Array index in keys
**Regola:** `javascript:S6479` - JSX list components should not use array indexes as key

```jsx
     56:       {items.map((item, index) =&gt; (
     57:         &lt;AccordionItem
 >>> 58:           key={`accordion-item-${index}`}
     59:           title={item.title}
     60:           isOpen={openIndex === index}
```

**❓ Perché è un problema:**
To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. Avoid array indexes since the order of the items may change, which will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

```
function Blog(props) {
  return (
    &lt;ul&gt;
      {props.posts.map((post, index) =&gt;
        &lt;li key={index}&gt; &lt;!-- Noncompliant: When 'posts' are reordered, React will need to recreate the list DOM --&gt;
          {post.title}
        &lt;/li&gt;
      )}
    &lt;/ul&gt;
  );
}
```

To fix it, use a string or a number that uniquely identifies the list item. The key must be unique am

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [no-array-index-key](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/no-array-index-key.md) 

  -  React Documentation - [Rendering lists](https://react.dev/learn/rendering-lists#rules-of-keys) 

  -  React Documentation - [Recursing On Children](https://reactjs.org/docs/reconciliation.html#recursing-on-children) 

  -  MDN web docs - [Crypto: randomUUID() method](https:

---

## 📄 `guide_frontend/src/pages/ShortcutsGuide.jsx`

### Riga 11 🟡 🟡
**Problema:** Do not use Array index in keys
**Regola:** `javascript:S6479` - JSX list components should not use array indexes as key

```jsx
     9:       &lt;div className="flex gap-1"&gt;
     10:           {keys.map((k, i) =&gt; (
 >>> 11:               &lt;span key={`key-${i}`} className="kbd"&gt;{k}&lt;/span&gt;
     12:           ))}
     13:       &lt;/div&gt;
```

**❓ Perché è un problema:**
To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. Avoid array indexes since the order of the items may change, which will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

```
function Blog(props) {
  return (
    &lt;ul&gt;
      {props.posts.map((post, index) =&gt;
        &lt;li key={index}&gt; &lt;!-- Noncompliant: When 'posts' are reordered, React will need to recreate the list DOM --&gt;
          {post.title}
        &lt;/li&gt;
      )}
    &lt;/ul&gt;
  );
}
```

To fix it, use a string or a number that uniquely identifies the list item. The key must be unique am

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [no-array-index-key](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/no-array-index-key.md) 

  -  React Documentation - [Rendering lists](https://react.dev/learn/rendering-lists#rules-of-keys) 

  -  React Documentation - [Recursing On Children](https://reactjs.org/docs/reconciliation.html#recursing-on-children) 

  -  MDN web docs - [Crypto: randomUUID() method](https:

---

## 📄 `desktop_app/views/import_view.py`

### Riga 268 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     266:         return certs_to_process
     267: 
 >>> 268:     def process_pdf(self, file_path):
     269:         original_filename = os.path.basename(file_path)
     270:         self.current_file_path = file_path # Store for fallback
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

## 📄 `guide_frontend/src/components/FeedbackFooter.jsx`

### Riga 26 🟡 🟢
**Problema:** Unexpected negated condition.
**Regola:** `javascript:S7735` - Negated conditions should be avoided when an else clause is present

```jsx
     24: 
     25:         &lt;AnimatePresence mode="wait"&gt;
 >>> 26:           {!voted ? (
     27:             &lt;motion.div
     28:               key="voting"
```

**❓ Perché è un problema:**
Negated conditions in if-else statements can make code harder to read and understand. When you see `if (!condition)`, your brain has to
process the negation, which adds cognitive load.

Positive conditions are generally easier to understand because they describe what **is** true rather than what **is not**
true. When you have both an if and else branch, you can usually invert the condition and swap the branches to make the code more readable.

For example, `if (!user.isActive)` requires you to think "if the user is NOT active", while `if (user.isActive)` is more
direct: "if the user is active".

This pattern is especially problematic with:

  -  Boolean negation using the `!` operator 

  -  Inequality comparisons like `!==` and `!=` 

  -  Complex expressions where the negation makes the 

---

## 📄 `guide_frontend/src/components/Header.jsx`

### Riga 93 🟡 🟡
**Problema:** Do not use Array index in keys
**Regola:** `javascript:S6479` - JSX list components should not use array indexes as key

```jsx
     91:                 results.map((result, index) =&gt; (
     92:                   &lt;button
 >>> 93:                     key={index}
     94:                     onClick={() =&gt; selectResult(result.path)}
     95:                     className="w-full text-left px-4 py-2.5 hover:bg-blue-50 flex items-center gap-3 transition-colors group"
```

**❓ Perché è un problema:**
To optimize the rendering of React list components, a unique identifier (UID) is required for each list item. This UID lets React identify the item
throughout its lifetime. Avoid array indexes since the order of the items may change, which will cause keys to not match up between renders,
recreating the DOM. It can negatively impact performance and may cause issues with the component state.

```
function Blog(props) {
  return (
    &lt;ul&gt;
      {props.posts.map((post, index) =&gt;
        &lt;li key={index}&gt; &lt;!-- Noncompliant: When 'posts' are reordered, React will need to recreate the list DOM --&gt;
          {post.title}
        &lt;/li&gt;
      )}
    &lt;/ul&gt;
  );
}
```

To fix it, use a string or a number that uniquely identifies the list item. The key must be unique am

**📚 Risorse:**
### Documentation

  -  [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [no-array-index-key](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/no-array-index-key.md) 

  -  React Documentation - [Rendering lists](https://react.dev/learn/rendering-lists#rules-of-keys) 

  -  React Documentation - [Recursing On Children](https://reactjs.org/docs/reconciliation.html#recursing-on-children) 

  -  MDN web docs - [Crypto: randomUUID() method](https:

---

## 📄 `guide_frontend/src/components/ValidationSimulator.jsx`

### Riga 102 🟡 🟢
**Problema:** Prefer `globalThis` over `window`.
**Regola:** `javascript:S7764` - Use "globalThis" instead of "window", "self", or "global"

```jsx
     100:                 &lt;Check size={48} className="mb-4 text-green-200" /&gt;
     101:                 &lt;p&gt;Tutto fatto! Nessun documento in attesa.&lt;/p&gt;
 >>> 102:                 &lt;button onClick={() =&gt; window.location.reload()} className="mt-4 text-xs text-blue-500 underline"&gt;
     103:                     Ricarica simulazione
     104:                 &lt;/button&gt;
```

**❓ Perché è un problema:**
`globalThis` is the standardized way to access the global object across all JavaScript environments. Before `globalThis`,
developers had to use different global references depending on the environment:

  -  `window` in browsers 

  -  `global` in Node.js 

  -  `self` in Web Workers 

This created compatibility issues when code needed to run in multiple environments. Using environment-specific globals makes code less portable and
harder to maintain.

`globalThis` was introduced in ES2020 as a unified solution that works consistently across all JavaScript environments. It provides the
same global object reference regardless of whether your code runs in a browser, Node.js, or Web Worker.

Using `globalThis` makes your code more future-proof and eliminates the need for environment detection 

---

## 📄 `guide_frontend/src/hooks/useSearch.js`

### Riga 1 🟡 🟢
**Problema:** Remove this unused import of 'useMemo'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```javascript
 >>> 1: import { useState, useEffect, useMemo } from 'react';
     2: import { useNavigate } from 'react-router-dom';
     3: 
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

## 📄 `guide_frontend/src/pages/MaintenanceGuide.jsx`

### Riga 5 🟡 🟢
**Problema:** Remove this unused import of 'HardDrive'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     3: import Note from '../components/ui/Note';
     4: import Step from '../components/ui/Step';
 >>> 5: import { Archive, HardDrive, RefreshCw } from 'lucide-react';
     6: 
     7: const MaintenanceGuide = () =&gt; {
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

---

## 📄 `guide_frontend/src/pages/TroubleshootingGuide.jsx`

### Riga 3 🟡 🟢
**Problema:** Remove this unused import of 'Note'.
**Regola:** `javascript:S1128` - Unnecessary imports should be removed

```jsx
     1: import React from 'react';
     2: import GuideCard from '../components/ui/GuideCard';
 >>> 3: import Note from '../components/ui/Note';
     4: import Accordion from '../components/ui/Accordion';
     5: import { HelpCircle, WifiOff, FileX, ShieldAlert } from 'lucide-react';
```

**❓ Perché è un problema:**
Unnecessary imports refer to importing modules, libraries, or dependencies that are not used or referenced anywhere in the code. These imports do
not contribute to the functionality of the application and only add extra weight to the JavaScript bundle, leading to potential performance and
maintainability issues.

```
import A from 'a'; // Noncompliant: The imported symbol 'A' isn't used
import { B1 } from 'b';

console.log(B1);
```

To mitigate the problems associated with unnecessary imports, you should regularly review and remove any imports that are not being used. Modern
JavaScript build tools and bundlers often provide features like tree shaking, which eliminates unused code during the bundling process, resulting in a
more optimized bundle size.

```
import { B1 } from 'b';

console.l

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) 

### Related rules

  -  S1481 - Unused local variables and functions should be removed

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
