# 🔴 SonarCloud RELIABILITY Issues - Fix Guide

**Progetto:** gianky00_formazione_coemi
**Data:** 2025-12-07 19:28
**Totale RELIABILITY:** 42
**Tempo stimato:** 3h 30min

## Descrizione

**RELIABILITY**: Bug che possono causare crash o comportamenti errati

## Istruzioni per Jules

Correggi i **42 issues di RELIABILITY**. Per ogni issue:
1. 📍 Vai al **file e riga** indicati
2. 💻 Leggi il **codice attuale** (righe con `>>>` = problema)
3. ❓ Comprendi **perché è un problema**
4. ✅ Applica la **correzione suggerita**
5. 🧪 **Verifica** che il codice funzioni

---

## 📄 `guide_frontend/src/components/DashboardSimulator.jsx`
**10 issue(s)** | Effort: 50min

### Riga 97 🟡 MAJOR

**🎯 Problema:** Avoid non-native interactive elements. If using native HTML is not possible, add an appropriate role and support for tabbing, mouse, keyboard, and touch inputs to an interactive content element.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6848` - Non-interactive DOM elements should not have an interactive handler |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-112 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     95:       {/* Table Header */}
     96:       &lt;div className="grid grid-cols-5 bg-gray-100 p-3 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200"&gt;
 >>> 97:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('dipendente')}&gt;
     98:             Dipendente {getSortIcon('dipendente')}
     99:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance `<div>`,
`<span>`, and `<footer>`, etc. They are typically used to structure content and do not have built-in interactivity
or keyboard accessibility.

Interactive handlers, on the other hand, are event handlers that respond to user interactions. These include handlers like `onClick`,
`onKeyDown`, `onMouseUp`, and more. When these handlers are added to an HTML element, they make the element respond to the
specified user interaction.

When non-interactive elements have interactive handlers, it can lead to several problems:

 - Unexpected behavior: Non-interactive elements are not designed to be interactive, so adding interactive handlers can cause unexpected behavior.
 For ex...

**✅ Come risolvere:**

The simplest and most recommended way is to replace the non-interactive elements with interactive ones. If for some reason you can’t replace the
non-interactive element, you can add an interactive `role` attribute to it and manually manage its keyboard event handlers and focus.
Common interactive roles include `button`, `link`, `checkbox`, `menuitem`, `menuitemcheckbox`,
`menuitemradio`, `option`, `radio`, `searchbox`, `switch`, and `textbox`.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;; // Noncompliant
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} role="button" /&gt;;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [no-static-element-interactions](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/no-static-element-interactions.md) 

 - WCAG - [Name, Role, Value](https://www.w3.org/WAI/WCAG21/Understanding/name-role-value) 

 - MDN web docs - [WAI-ARIA Roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

---

### Riga 97 🟢 MINOR

**🎯 Problema:** Visible, non-interactive elements with click handlers must have at least one keyboard listener.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1082` - Mouse events should have corresponding keyboard events |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-112 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     95:       {/* Table Header */}
     96:       &lt;div className="grid grid-cols-5 bg-gray-100 p-3 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200"&gt;
 >>> 97:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('dipendente')}&gt;
     98:             Dipendente {getSortIcon('dipendente')}
     99:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Offering the same experience with the mouse and the keyboard allow users to pick their preferred devices.

Additionally, users of assistive technology will also be able to browse the site even if they cannot use the mouse.

This rules detects the following issues:

 - when `onClick` is not accompanied by at least one of the following: `onKeyUp`, `onKeyDown`,
 `onKeyPress`. 

 - when `onmouseover`/`onmouseout` are not paired by `onfocus`/`onblur`.

**✅ Come risolvere:**

Add at least one of the following event handlers `onKeyUp`, `onKeyDown`, `onKeyPress` to the element when using
`onClick` event handler. Add corresponding event handlers `onfocus`/`onblur` to the element when using
`onmouseover`/`onmouseout` event handlers.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;

&lt;div onMouseOver={ () =&gt; {}} } /&gt;
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} onKeyDown={this.handleKeyDown} /&gt;

&lt;div onMouseOver={ () =&gt; {} } onFocus={ () =&gt; {} } /&gt;
```

### Exceptions

This does not apply for interactive or hidden elements, eg. when using `aria-hidden="true"` attribute.

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [mouse-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/mouse-events-have-key-events.md)
 

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [click-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/click-events-have-key-events.md)
 

 - SCR2 - [Using red...

---

### Riga 100 🟡 MAJOR

**🎯 Problema:** Avoid non-native interactive elements. If using native HTML is not possible, add an appropriate role and support for tabbing, mouse, keyboard, and touch inputs to an interactive content element.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6848` - Non-interactive DOM elements should not have an interactive handler |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-107 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     98:             Dipendente {getSortIcon('dipendente')}
     99:         &lt;/div&gt;
 >>> 100:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('corso')}&gt;
     101:             Documento {getSortIcon('corso')}
     102:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance `<div>`,
`<span>`, and `<footer>`, etc. They are typically used to structure content and do not have built-in interactivity
or keyboard accessibility.

Interactive handlers, on the other hand, are event handlers that respond to user interactions. These include handlers like `onClick`,
`onKeyDown`, `onMouseUp`, and more. When these handlers are added to an HTML element, they make the element respond to the
specified user interaction.

When non-interactive elements have interactive handlers, it can lead to several problems:

 - Unexpected behavior: Non-interactive elements are not designed to be interactive, so adding interactive handlers can cause unexpected behavior.
 For ex...

**✅ Come risolvere:**

The simplest and most recommended way is to replace the non-interactive elements with interactive ones. If for some reason you can’t replace the
non-interactive element, you can add an interactive `role` attribute to it and manually manage its keyboard event handlers and focus.
Common interactive roles include `button`, `link`, `checkbox`, `menuitem`, `menuitemcheckbox`,
`menuitemradio`, `option`, `radio`, `searchbox`, `switch`, and `textbox`.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;; // Noncompliant
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} role="button" /&gt;;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [no-static-element-interactions](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/no-static-element-interactions.md) 

 - WCAG - [Name, Role, Value](https://www.w3.org/WAI/WCAG21/Understanding/name-role-value) 

 - MDN web docs - [WAI-ARIA Roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

---

### Riga 100 🟢 MINOR

**🎯 Problema:** Visible, non-interactive elements with click handlers must have at least one keyboard listener.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1082` - Mouse events should have corresponding keyboard events |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-107 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     98:             Dipendente {getSortIcon('dipendente')}
     99:         &lt;/div&gt;
 >>> 100:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('corso')}&gt;
     101:             Documento {getSortIcon('corso')}
     102:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Offering the same experience with the mouse and the keyboard allow users to pick their preferred devices.

Additionally, users of assistive technology will also be able to browse the site even if they cannot use the mouse.

This rules detects the following issues:

 - when `onClick` is not accompanied by at least one of the following: `onKeyUp`, `onKeyDown`,
 `onKeyPress`. 

 - when `onmouseover`/`onmouseout` are not paired by `onfocus`/`onblur`.

**✅ Come risolvere:**

Add at least one of the following event handlers `onKeyUp`, `onKeyDown`, `onKeyPress` to the element when using
`onClick` event handler. Add corresponding event handlers `onfocus`/`onblur` to the element when using
`onmouseover`/`onmouseout` event handlers.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;

&lt;div onMouseOver={ () =&gt; {}} } /&gt;
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} onKeyDown={this.handleKeyDown} /&gt;

&lt;div onMouseOver={ () =&gt; {} } onFocus={ () =&gt; {} } /&gt;
```

### Exceptions

This does not apply for interactive or hidden elements, eg. when using `aria-hidden="true"` attribute.

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [mouse-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/mouse-events-have-key-events.md)
 

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [click-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/click-events-have-key-events.md)
 

 - SCR2 - [Using red...

---

### Riga 103 🟡 MAJOR

**🎯 Problema:** Avoid non-native interactive elements. If using native HTML is not possible, add an appropriate role and support for tabbing, mouse, keyboard, and touch inputs to an interactive content element.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6848` - Non-interactive DOM elements should not have an interactive handler |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-106 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     101:             Documento {getSortIcon('corso')}
     102:         &lt;/div&gt;
 >>> 103:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('data')}&gt;
     104:             Data Ril. {getSortIcon('data')}
     105:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance `<div>`,
`<span>`, and `<footer>`, etc. They are typically used to structure content and do not have built-in interactivity
or keyboard accessibility.

Interactive handlers, on the other hand, are event handlers that respond to user interactions. These include handlers like `onClick`,
`onKeyDown`, `onMouseUp`, and more. When these handlers are added to an HTML element, they make the element respond to the
specified user interaction.

When non-interactive elements have interactive handlers, it can lead to several problems:

 - Unexpected behavior: Non-interactive elements are not designed to be interactive, so adding interactive handlers can cause unexpected behavior.
 For ex...

**✅ Come risolvere:**

The simplest and most recommended way is to replace the non-interactive elements with interactive ones. If for some reason you can’t replace the
non-interactive element, you can add an interactive `role` attribute to it and manually manage its keyboard event handlers and focus.
Common interactive roles include `button`, `link`, `checkbox`, `menuitem`, `menuitemcheckbox`,
`menuitemradio`, `option`, `radio`, `searchbox`, `switch`, and `textbox`.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;; // Noncompliant
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} role="button" /&gt;;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [no-static-element-interactions](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/no-static-element-interactions.md) 

 - WCAG - [Name, Role, Value](https://www.w3.org/WAI/WCAG21/Understanding/name-role-value) 

 - MDN web docs - [WAI-ARIA Roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

---

### Riga 103 🟢 MINOR

**🎯 Problema:** Visible, non-interactive elements with click handlers must have at least one keyboard listener.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1082` - Mouse events should have corresponding keyboard events |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-106 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     101:             Documento {getSortIcon('corso')}
     102:         &lt;/div&gt;
 >>> 103:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('data')}&gt;
     104:             Data Ril. {getSortIcon('data')}
     105:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Offering the same experience with the mouse and the keyboard allow users to pick their preferred devices.

Additionally, users of assistive technology will also be able to browse the site even if they cannot use the mouse.

This rules detects the following issues:

 - when `onClick` is not accompanied by at least one of the following: `onKeyUp`, `onKeyDown`,
 `onKeyPress`. 

 - when `onmouseover`/`onmouseout` are not paired by `onfocus`/`onblur`.

**✅ Come risolvere:**

Add at least one of the following event handlers `onKeyUp`, `onKeyDown`, `onKeyPress` to the element when using
`onClick` event handler. Add corresponding event handlers `onfocus`/`onblur` to the element when using
`onmouseover`/`onmouseout` event handlers.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;

&lt;div onMouseOver={ () =&gt; {}} } /&gt;
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} onKeyDown={this.handleKeyDown} /&gt;

&lt;div onMouseOver={ () =&gt; {} } onFocus={ () =&gt; {} } /&gt;
```

### Exceptions

This does not apply for interactive or hidden elements, eg. when using `aria-hidden="true"` attribute.

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [mouse-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/mouse-events-have-key-events.md)
 

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [click-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/click-events-have-key-events.md)
 

 - SCR2 - [Using red...

---

### Riga 106 🟡 MAJOR

**🎯 Problema:** Avoid non-native interactive elements. If using native HTML is not possible, add an appropriate role and support for tabbing, mouse, keyboard, and touch inputs to an interactive content element.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6848` - Non-interactive DOM elements should not have an interactive handler |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 8-110 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     104:             Data Ril. {getSortIcon('data')}
     105:         &lt;/div&gt;
 >>> 106:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('scadenza')}&gt;
     107:             Scadenza {getSortIcon('scadenza')}
     108:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance `<div>`,
`<span>`, and `<footer>`, etc. They are typically used to structure content and do not have built-in interactivity
or keyboard accessibility.

Interactive handlers, on the other hand, are event handlers that respond to user interactions. These include handlers like `onClick`,
`onKeyDown`, `onMouseUp`, and more. When these handlers are added to an HTML element, they make the element respond to the
specified user interaction.

When non-interactive elements have interactive handlers, it can lead to several problems:

 - Unexpected behavior: Non-interactive elements are not designed to be interactive, so adding interactive handlers can cause unexpected behavior.
 For ex...

**✅ Come risolvere:**

The simplest and most recommended way is to replace the non-interactive elements with interactive ones. If for some reason you can’t replace the
non-interactive element, you can add an interactive `role` attribute to it and manually manage its keyboard event handlers and focus.
Common interactive roles include `button`, `link`, `checkbox`, `menuitem`, `menuitemcheckbox`,
`menuitemradio`, `option`, `radio`, `searchbox`, `switch`, and `textbox`.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;; // Noncompliant
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} role="button" /&gt;;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [no-static-element-interactions](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/no-static-element-interactions.md) 

 - WCAG - [Name, Role, Value](https://www.w3.org/WAI/WCAG21/Understanding/name-role-value) 

 - MDN web docs - [WAI-ARIA Roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

---

### Riga 106 🟢 MINOR

**🎯 Problema:** Visible, non-interactive elements with click handlers must have at least one keyboard listener.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1082` - Mouse events should have corresponding keyboard events |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 8-110 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     104:             Data Ril. {getSortIcon('data')}
     105:         &lt;/div&gt;
 >>> 106:         &lt;div className="col-span-1 cursor-pointer hover:text-gray-700" onClick={() =&gt; handleSort('scadenza')}&gt;
     107:             Scadenza {getSortIcon('scadenza')}
     108:         &lt;/div&gt;
```

**❓ Perché è un problema:**

Offering the same experience with the mouse and the keyboard allow users to pick their preferred devices.

Additionally, users of assistive technology will also be able to browse the site even if they cannot use the mouse.

This rules detects the following issues:

 - when `onClick` is not accompanied by at least one of the following: `onKeyUp`, `onKeyDown`,
 `onKeyPress`. 

 - when `onmouseover`/`onmouseout` are not paired by `onfocus`/`onblur`.

**✅ Come risolvere:**

Add at least one of the following event handlers `onKeyUp`, `onKeyDown`, `onKeyPress` to the element when using
`onClick` event handler. Add corresponding event handlers `onfocus`/`onblur` to the element when using
`onmouseover`/`onmouseout` event handlers.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;

&lt;div onMouseOver={ () =&gt; {}} } /&gt;
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} onKeyDown={this.handleKeyDown} /&gt;

&lt;div onMouseOver={ () =&gt; {} } onFocus={ () =&gt; {} } /&gt;
```

### Exceptions

This does not apply for interactive or hidden elements, eg. when using `aria-hidden="true"` attribute.

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [mouse-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/mouse-events-have-key-events.md)
 

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [click-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/click-events-have-key-events.md)
 

 - SCR2 - [Using red...

---

### Riga 152 🟡 MAJOR

**🎯 Problema:** Ambiguous spacing before next element span

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6772` - Spacing between inline elements should be explicit |
| Severità | MAJOR |
| Effort | 5min |
| Tags | react |

**💻 Codice attuale:**
```jsx
     150:           &lt;div className="flex gap-2"&gt;
     151:              &lt;span className="w-2 h-2 rounded-full bg-green-500 inline-block"&gt;&lt;/span&gt; Attivo
 >>> 152:              &lt;span className="w-2 h-2 rounded-full bg-yellow-500 inline-block"&gt;&lt;/span&gt; In Scadenza
     153:              &lt;span className="w-2 h-2 rounded-full bg-red-500 inline-block"&gt;&lt;/span&gt; Scaduto
     154:           &lt;/div&gt;
```

**❓ Perché è un problema:**

React JSX differs from the HTML standard in the way it handles newline characters and surrounding whitespace. HTML collapses multiple whitespace
characters (including newlines) into a single whitespace, but JSX removes such sequences completely, leaving no space between inline elements
separated by the line break. This difference in behavior can be confusing and may result in unintended layout, for example, missing whitespace between
the link content and the surrounding text.

To avoid such issues, you should never rely on newline characters in JSX, and explicitly specify whether you want whitespace between inline
elements separated by a line break.

```
&lt;div&gt;{/* Noncompliant: ambiguous spacing */}
 Here is some
 &lt;a&gt;space&lt;/a&gt;
&lt;/div&gt;

&lt;div&gt;{/* Noncompliant: amb...

**📝 Descrizione:**

### Why is this an issue?

React JSX differs from the HTML standard in the way it handles newline characters and surrounding whitespace. HTML collapses multiple whitespace
characters (including newlines) into a single whitespace, but JSX removes such sequences completely, leaving no space between inline elements
separated by the line break. This difference in behavior can be confusing and may result in unintended layout, for example, missing whitespace between
the link content and the surrounding text.

To avoid such issues, you should never rely on newline characters in JSX, and explicitly specify whether you want whitespace between inline
elements separated by a line break.

```
&lt;div&gt;{/* Noncompliant: ambiguous spacing */}
 Here is some
 &lt;a&gt;space&lt;/a&gt;
&lt;/div&gt;

&lt;d...

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [jsx-child-element-spacing](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/jsx-child-element-spacing.md) 

 - React Documentation - [Writing markup with JSX](https://react.dev/learn#writing-markup-with-jsx) 

 - MDN web docs - Spaces
 in between inline and inline-block elements

---

### Riga 153 🟡 MAJOR

**🎯 Problema:** Ambiguous spacing before next element span

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6772` - Spacing between inline elements should be explicit |
| Severità | MAJOR |
| Effort | 5min |
| Tags | react |

**💻 Codice attuale:**
```jsx
     151:              &lt;span className="w-2 h-2 rounded-full bg-green-500 inline-block"&gt;&lt;/span&gt; Attivo
     152:              &lt;span className="w-2 h-2 rounded-full bg-yellow-500 inline-block"&gt;&lt;/span&gt; In Scadenza
 >>> 153:              &lt;span className="w-2 h-2 rounded-full bg-red-500 inline-block"&gt;&lt;/span&gt; Scaduto
     154:           &lt;/div&gt;
     155:       &lt;/div&gt;
```

**❓ Perché è un problema:**

React JSX differs from the HTML standard in the way it handles newline characters and surrounding whitespace. HTML collapses multiple whitespace
characters (including newlines) into a single whitespace, but JSX removes such sequences completely, leaving no space between inline elements
separated by the line break. This difference in behavior can be confusing and may result in unintended layout, for example, missing whitespace between
the link content and the surrounding text.

To avoid such issues, you should never rely on newline characters in JSX, and explicitly specify whether you want whitespace between inline
elements separated by a line break.

```
&lt;div&gt;{/* Noncompliant: ambiguous spacing */}
 Here is some
 &lt;a&gt;space&lt;/a&gt;
&lt;/div&gt;

&lt;div&gt;{/* Noncompliant: amb...

**📝 Descrizione:**

### Why is this an issue?

React JSX differs from the HTML standard in the way it handles newline characters and surrounding whitespace. HTML collapses multiple whitespace
characters (including newlines) into a single whitespace, but JSX removes such sequences completely, leaving no space between inline elements
separated by the line break. This difference in behavior can be confusing and may result in unintended layout, for example, missing whitespace between
the link content and the surrounding text.

To avoid such issues, you should never rely on newline characters in JSX, and explicitly specify whether you want whitespace between inline
elements separated by a line break.

```
&lt;div&gt;{/* Noncompliant: ambiguous spacing */}
 Here is some
 &lt;a&gt;space&lt;/a&gt;
&lt;/div&gt;

&lt;d...

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [jsx-child-element-spacing](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/jsx-child-element-spacing.md) 

 - React Documentation - [Writing markup with JSX](https://react.dev/learn#writing-markup-with-jsx) 

 - MDN web docs - Spaces
 in between inline and inline-block elements

---

## 📄 `guide_frontend/src/components/ui/Accordion.jsx`
**6 issue(s)** | Effort: 30min

### Riga 6 🟡 MAJOR

**🎯 Problema:** 'title' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 25-30 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     4: import clsx from 'clsx';
     5: 
 >>> 6: const AccordionItem = ({ title, children, isOpen, onClick }) =&gt; {
     7:   return (
     8:     &lt;div className="border border-gray-200 rounded-lg bg-white overflow-hidden mb-3 shadow-sm hover:shadow-md transition-shadow"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 6 🟡 MAJOR

**🎯 Problema:** 'children' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 32-40 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     4: import clsx from 'clsx';
     5: 
 >>> 6: const AccordionItem = ({ title, children, isOpen, onClick }) =&gt; {
     7:   return (
     8:     &lt;div className="border border-gray-200 rounded-lg bg-white overflow-hidden mb-3 shadow-sm hover:shadow-md transition-shadow"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 6 🟡 MAJOR

**🎯 Problema:** 'isOpen' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 42-48 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     4: import clsx from 'clsx';
     5: 
 >>> 6: const AccordionItem = ({ title, children, isOpen, onClick }) =&gt; {
     7:   return (
     8:     &lt;div className="border border-gray-200 rounded-lg bg-white overflow-hidden mb-3 shadow-sm hover:shadow-md transition-shadow"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 6 🟡 MAJOR

**🎯 Problema:** 'onClick' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 50-57 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     4: import clsx from 'clsx';
     5: 
 >>> 6: const AccordionItem = ({ title, children, isOpen, onClick }) =&gt; {
     7:   return (
     8:     &lt;div className="border border-gray-200 rounded-lg bg-white overflow-hidden mb-3 shadow-sm hover:shadow-md transition-shadow"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 40 🟡 MAJOR

**🎯 Problema:** 'items' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-26 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     38: };
     39: 
 >>> 40: const Accordion = ({ items }) =&gt; {
     41:   const [openIndex, setOpenIndex] = useState(null);
     42: 
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 49 🟡 MAJOR

**🎯 Problema:** 'items.map' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 13-16 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     47:   return (
     48:     &lt;div className="w-full"&gt;
 >>> 49:       {items.map((item, index) =&gt; (
     50:         &lt;AccordionItem
     51:           key={index}
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/components/ui/GuideCard.jsx`
**5 issue(s)** | Effort: 25min

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'children' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 21-29 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) =&gt; {
     6:   return (
     7:     &lt;motion.div
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'className' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 31-40 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) =&gt; {
     6:   return (
     7:     &lt;motion.div
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'title' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 42-47 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) =&gt; {
     6:   return (
     7:     &lt;motion.div
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'icon' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 49-59 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) =&gt; {
     6:   return (
     7:     &lt;motion.div
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'delay' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 61-70 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) =&gt; {
     6:   return (
     7:     &lt;motion.div
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/components/Sidebar.jsx`
**5 issue(s)** | Effort: 25min

### Riga 23 🟡 MAJOR

**🎯 Problema:** 'icon' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 23-33 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     21: import clsx from 'clsx';
     22: 
 >>> 23: const SidebarItem = ({ icon: Icon, label, to, collapsed }) =&gt; {
     24:   const location = useLocation();
     25:   const isActive = location.pathname === to;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 23 🟡 MAJOR

**🎯 Problema:** 'label' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 35-40 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     21: import clsx from 'clsx';
     22: 
 >>> 23: const SidebarItem = ({ icon: Icon, label, to, collapsed }) =&gt; {
     24:   const location = useLocation();
     25:   const isActive = location.pathname === to;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 23 🟡 MAJOR

**🎯 Problema:** 'to' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 42-44 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     21: import clsx from 'clsx';
     22: 
 >>> 23: const SidebarItem = ({ icon: Icon, label, to, collapsed }) =&gt; {
     24:   const location = useLocation();
     25:   const isActive = location.pathname === to;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 23 🟡 MAJOR

**🎯 Problema:** 'collapsed' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 46-55 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     21: import clsx from 'clsx';
     22: 
 >>> 23: const SidebarItem = ({ icon: Icon, label, to, collapsed }) =&gt; {
     24:   const location = useLocation();
     25:   const isActive = location.pathname === to;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 64 🟡 MAJOR

**🎯 Problema:** Either remove this useless object instantiation of "window.QWebChannel" or use it.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1848` - Objects should not be created to be dropped immediately without being used |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 6-28 |

**💻 Codice attuale:**
```jsx
     62:   useEffect(() =&gt; {
     63:     if (window.qt &amp;&amp; window.qt.webChannelTransport) {
 >>> 64:       new window.QWebChannel(window.qt.webChannelTransport, function(channel) {
     65:         if (channel.objects.bridge) {
     66:             setBridge(channel.objects.bridge);
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

#### Excep...

**📝 Descrizione:**

### Why is this an issue?

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
let something = new MyCon...

**📚 Risorse:**

#### Documentation

 - MDN web docs - [`Object.prototype.constructor`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/constructor) 

 - MDN web docs - [constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor) 

 - MDN web docs - [`new` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/new)

---

## 📄 `guide_frontend/src/components/ui/Badge.jsx`
**3 issue(s)** | Effort: 15min

### Riga 4 🟡 MAJOR

**🎯 Problema:** 'className' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 48-57 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     2: import clsx from 'clsx';
     3: 
 >>> 4: const Badge = ({ children, variant = 'default', className }) =&gt; {
     5:   const styles = {
     6:     default: 'bg-gray-100 text-gray-800 border-gray-200',
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 4 🟡 MAJOR

**🎯 Problema:** 'children' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 17-25 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     2: import clsx from 'clsx';
     3: 
 >>> 4: const Badge = ({ children, variant = 'default', className }) =&gt; {
     5:   const styles = {
     6:     default: 'bg-gray-100 text-gray-800 border-gray-200',
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 4 🟡 MAJOR

**🎯 Problema:** 'variant' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 27-46 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     2: import clsx from 'clsx';
     3: 
 >>> 4: const Badge = ({ children, variant = 'default', className }) =&gt; {
     5:   const styles = {
     6:     default: 'bg-gray-100 text-gray-800 border-gray-200',
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/components/ui/Note.jsx`
**3 issue(s)** | Effort: 15min

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'children' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 31-39 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const Note = ({ type = 'info', children, title }) =&gt; {
     6:   const styles = {
     7:     info: {
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'type' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 16-29 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const Note = ({ type = 'info', children, title }) =&gt; {
     6:   const styles = {
     7:     info: {
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'title' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 41-46 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import clsx from 'clsx';
     4: 
 >>> 5: const Note = ({ type = 'info', children, title }) =&gt; {
     6:   const styles = {
     7:     info: {
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/components/ui/Step.jsx`
**3 issue(s)** | Effort: 15min

### Riga 3 🟡 MAJOR

**🎯 Problema:** 'number' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 16-22 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     1: import React from 'react';
     2: 
 >>> 3: const Step = ({ number, title, children }) =&gt; {
     4:   return (
     5:     &lt;div className="flex gap-4 mb-8 last:mb-0 relative"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 3 🟡 MAJOR

**🎯 Problema:** 'title' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 24-29 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     1: import React from 'react';
     2: 
 >>> 3: const Step = ({ number, title, children }) =&gt; {
     4:   return (
     5:     &lt;div className="flex gap-4 mb-8 last:mb-0 relative"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 3 🟡 MAJOR

**🎯 Problema:** 'children' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 31-39 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     1: import React from 'react';
     2: 
 >>> 3: const Step = ({ number, title, children }) =&gt; {
     4:   return (
     5:     &lt;div className="flex gap-4 mb-8 last:mb-0 relative"&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/pages/ShortcutsGuide.jsx`
**3 issue(s)** | Effort: 15min

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'keys' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 23-27 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import { Keyboard, Command } from 'lucide-react';
     4: 
 >>> 5: const ShortcutRow = ({ keys, desc }) =&gt; (
     6:   &lt;div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 px-2 rounded-lg transition-colors"&gt;
     7:       &lt;span className="text-gray-700 font-medium text-sm"&gt;{desc}&lt;/span&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 5 🟡 MAJOR

**🎯 Problema:** 'desc' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 29-33 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     3: import { Keyboard, Command } from 'lucide-react';
     4: 
 >>> 5: const ShortcutRow = ({ keys, desc }) =&gt; (
     6:   &lt;div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 px-2 rounded-lg transition-colors"&gt;
     7:       &lt;span className="text-gray-700 font-medium text-sm"&gt;{desc}&lt;/span&gt;
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

### Riga 9 🟡 MAJOR

**🎯 Problema:** 'keys.map' is missing in props validation

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6774` - React components should validate prop types |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 16-19 |
| Tags | react |

**💻 Codice attuale:**
```jsx
     7:       &lt;span className="text-gray-700 font-medium text-sm"&gt;{desc}&lt;/span&gt;
     8:       &lt;div className="flex gap-1"&gt;
 >>> 9:           {keys.map((k, i) =&gt; (
     10:               &lt;span key={i} className="kbd"&gt;{k}&lt;/span&gt;
     11:           ))}
```

**❓ Perché è un problema:**

In JavaScript, props are typically passed as plain objects, which can lead to errors and confusion when working with components that have specific
prop requirements. However, it lacks of type safety and clarity when passing props to components in a codebase.

By defining types for component props, developers can enforce type safety and provide clear documentation for the expected props of a component.
This helps catch potential errors at compile-time. It also improves code maintainability by making it easier to understand how components should be
used and what props they accept.

**✅ Come risolvere:**

##### Noncompliant code example

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;; // Noncompliant: 'lastname' type is missing
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
};
```

##### Compliant solution

```
import PropTypes from 'prop-types';

function Hello({ firstname, lastname }) {
 return &lt;div&gt;Hello {firstname} {lastname}&lt;/div&gt;;
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};

// Using legacy APIs

class Hello extends React.Component {
 render() {
 return &lt;div&gt;Hello {this.props.firstname} {this.props.lastname}&lt;/div&gt;;
 }
}
Hello.propTypes = {
 firstname: PropTypes.string.isRequired,
 lastname: PropTypes.string.isRequired,
};
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) - Rule [prop-types](https://github.com/jsx-eslint/eslint-plugin-react/blob/HEAD/docs/rules/prop-types.md) 

 - React Documentation - [static propTypes](https://react.dev/reference/react/Component#static-proptypes) 

 - Flow.js Documentation - [React](https://flow.org/en/docs/react/)

---

## 📄 `guide_frontend/src/components/ImportSimulator.jsx`
**2 issue(s)** | Effort: 10min

### Riga 82 🟡 MAJOR

**🎯 Problema:** Avoid non-native interactive elements. If using native HTML is not possible, add an appropriate role and support for tabbing, mouse, keyboard, and touch inputs to an interactive content element.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6848` - Non-interactive DOM elements should not have an interactive handler |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 14-15 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     80:               className="text-center w-full max-w-md"
     81:             &gt;
 >>> 82:               &lt;div
 >>> 83:                 onClick={simulateProcess}
 >>> 84:                 className="border-2 border-dashed border-blue-300 rounded-xl p-10 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-500 transition-all cursor-pointer group"
 >>> 85:               &gt;
     86:                 &lt;UploadCloud size={48} className="mx-auto text-blue-400 group-hover:text-blue-600 mb-4 transition-colors" /&gt;
     87:                 &lt;h3 className="text-lg font-bold text-gray-700 mb-2"&gt;Trascina qui i tuoi file PDF&lt;/h3&gt;
```

**❓ Perché è un problema:**

Non-interactive DOM elements are HTML elements that are not designed to be interacted with by the user, for instance `<div>`,
`<span>`, and `<footer>`, etc. They are typically used to structure content and do not have built-in interactivity
or keyboard accessibility.

Interactive handlers, on the other hand, are event handlers that respond to user interactions. These include handlers like `onClick`,
`onKeyDown`, `onMouseUp`, and more. When these handlers are added to an HTML element, they make the element respond to the
specified user interaction.

When non-interactive elements have interactive handlers, it can lead to several problems:

 - Unexpected behavior: Non-interactive elements are not designed to be interactive, so adding interactive handlers can cause unexpected behavior.
 For ex...

**✅ Come risolvere:**

The simplest and most recommended way is to replace the non-interactive elements with interactive ones. If for some reason you can’t replace the
non-interactive element, you can add an interactive `role` attribute to it and manually manage its keyboard event handlers and focus.
Common interactive roles include `button`, `link`, `checkbox`, `menuitem`, `menuitemcheckbox`,
`menuitemradio`, `option`, `radio`, `searchbox`, `switch`, and `textbox`.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;; // Noncompliant
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} role="button" /&gt;;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [no-static-element-interactions](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/no-static-element-interactions.md) 

 - WCAG - [Name, Role, Value](https://www.w3.org/WAI/WCAG21/Understanding/name-role-value) 

 - MDN web docs - [WAI-ARIA Roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

---

### Riga 82 🟢 MINOR

**🎯 Problema:** Visible, non-interactive elements with click handlers must have at least one keyboard listener.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S1082` - Mouse events should have corresponding keyboard events |
| Severità | MINOR |
| Effort | 5min |
| Posizione | Colonne 14-15 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     80:               className="text-center w-full max-w-md"
     81:             &gt;
 >>> 82:               &lt;div
 >>> 83:                 onClick={simulateProcess}
 >>> 84:                 className="border-2 border-dashed border-blue-300 rounded-xl p-10 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-500 transition-all cursor-pointer group"
 >>> 85:               &gt;
     86:                 &lt;UploadCloud size={48} className="mx-auto text-blue-400 group-hover:text-blue-600 mb-4 transition-colors" /&gt;
     87:                 &lt;h3 className="text-lg font-bold text-gray-700 mb-2"&gt;Trascina qui i tuoi file PDF&lt;/h3&gt;
```

**❓ Perché è un problema:**

Offering the same experience with the mouse and the keyboard allow users to pick their preferred devices.

Additionally, users of assistive technology will also be able to browse the site even if they cannot use the mouse.

This rules detects the following issues:

 - when `onClick` is not accompanied by at least one of the following: `onKeyUp`, `onKeyDown`,
 `onKeyPress`. 

 - when `onmouseover`/`onmouseout` are not paired by `onfocus`/`onblur`.

**✅ Come risolvere:**

Add at least one of the following event handlers `onKeyUp`, `onKeyDown`, `onKeyPress` to the element when using
`onClick` event handler. Add corresponding event handlers `onfocus`/`onblur` to the element when using
`onmouseover`/`onmouseout` event handlers.

##### Noncompliant code example

```
&lt;div onClick={() =&gt; {}} /&gt;

&lt;div onMouseOver={ () =&gt; {}} } /&gt;
```

##### Compliant solution

```
&lt;div onClick={() =&gt; {}} onKeyDown={this.handleKeyDown} /&gt;

&lt;div onMouseOver={ () =&gt; {} } onFocus={ () =&gt; {} } /&gt;
```

### Exceptions

This does not apply for interactive or hidden elements, eg. when using `aria-hidden="true"` attribute.

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [mouse-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/mouse-events-have-key-events.md)
 

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [click-events-have-key-events](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/click-events-have-key-events.md)
 

 - SCR2 - [Using red...

---

## 📄 `tests/desktop_app/views/test_scadenzario_logic.py`
**1 issue(s)** | Effort: 5min

### Riga 42 🟡 MAJOR

**🎯 Problema:** Do not perform equality checks with floating point values.

| Campo | Valore |
|-------|--------|
| Regola | `python:S1244` - Floating point numbers should not be tested for equality |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 11-46 |
| Tags | data-science, numpy, pytorch, suspicious |

**💻 Codice attuale:**
```python
     40:     assert scadenzario_view is not None
     41:     assert scadenzario_view.gantt_scene is not None
 >>> 42:     assert scadenzario_view.zoom_months == 3.0
     43: 
     44: def test_load_data_trigger(scadenzario_view):
```

**❓ Perché è un problema:**

Floating point math is imprecise because of the challenges of storing such values in a binary representation.

In base 10, the fraction `1/3` is represented as `0.333…​` which, for a given number of significant digit, will never exactly
be `1/3`. The same problem happens when trying to represent `1/10` in base 2, with leads to the infinitely repeating fraction
`0.0001100110011…​`. This makes floating point representations inherently imprecise.

Even worse, floating point math is not associative; push a `float` through a series of simple mathematical operations and the answer
will be different based on the order of those operation because of the rounding that takes place at each step.

Even simple floating point assignments are not simple, as can be vizualized using the `format` function to...

**✅ Come risolvere:**

Whenever attempting to compare float values, it is important to consider the inherent imprecision of floating-point arithmetic.

One common solution to this problem is to use a tolerance value (also called epsilon) to define an acceptable range of difference between two
floats. A tolerance value may be relative (based on the magnitude of the numbers being compared) or absolute. Note that comparing a value to 0 is a
special case: as it has no magnitude, it is important to use an absolute tolerance value.

The `math.isclose` function allows to compare floats with a relative and absolute tolerance. One should however be careful when
comparing values to 0, as by default, the absolute tolerance of `math.isclose` is `0.0` (this case is covered by rule
S6727) . Depending on the library you’re using, equivalent functions exist, with possibly different default tolerances (e.g
`numpy.isclose` or `torch.isclose` which are respectively designed to work with `numpy` arrays and
`pytorch` tensors).

If precise decimal arithmetic is needed, another option is to use the `Decimal` class of the `decimal` module, which allows
for exact decimal arithmetic.

##### Noncompliant code example

```
def foo(...

**📚 Risorse:**

#### Documentation

 - Python Documentation - Floating Point Arithmetic: Issues and
 Limitations 

 - Python Documentation - Decimal fixed point and floating point
 arithmetic 

 - NumPy Documentation - [numpy.isclose](https://numpy.org/doc/stable/reference/generated/numpy.isclose.html) 

 - PyTorch Documentation - [torch.isclose](https://pytorch.org/docs/stable/generated/torch.isclose.html) 

#### Related rules

 - S6727 - The `abs_tol` parameter should be provided when using `math.isclose` to ...

---

## 📄 `guide_frontend/src/pages/SettingsGuide.jsx`
**1 issue(s)** | Effort: 5min

### Riga 26 🟡 MAJOR

**🎯 Problema:** A form label must be associated with a control.

| Campo | Valore |
|-------|--------|
| Regola | `javascript:S6853` - Label elements should have a text label and an associated control |
| Severità | MAJOR |
| Effort | 5min |
| Posizione | Colonne 22-27 |
| Tags | accessibility, react |

**💻 Codice attuale:**
```jsx
     24:              &lt;div className="flex gap-4 mb-6"&gt;
     25:                  &lt;div className="flex-1"&gt;
 >>> 26:                      &lt;label className="block text-sm font-medium text-gray-700 mb-1"&gt;Preset Rapidi&lt;/label&gt;
     27:                      &lt;select className="w-full border-gray-300 rounded-md shadow-sm bg-gray-50 p-2 text-sm" disabled&gt;
     28:                          &lt;option&gt;Gmail (OAuth/App Password)&lt;/option&gt;
```

**❓ Perché è un problema:**

When a label element lacks a text label or an associated control, it can lead to several issues:

 - **Poor Accessibility**: Screen readers rely on correctly associated labels to describe the function of the form control. If the
 label is not properly associated with a control, it can make the form difficult or impossible for visually impaired users to understand or interact
 with. 

 - **Confusing User Interface**: Labels provide users with clear instructions about what information is required in a form control.
 Without a properly associated label, users might not understand what input is expected, leading to confusion and potential misuse of the form. 

 - **Code Maintainability**: Properly structured and labeled code is easier to read, understand, and maintain. When labels are not
 cor...

**✅ Come risolvere:**

If you have a pair of control and `<label>` elements, make sure that the `<label>` wraps the control element. If
you lack a control element, add one.

It is strongly recommended to avoid using generated `id`s since they must be deterministic.

##### Noncompliant code example

```
&lt;input type="text" /&gt;
&lt;label&gt;Favorite food&lt;/label&gt;
```

##### Compliant solution

```
&lt;label&gt;
 &lt;input type="text" /&gt;
 Favorite food
&lt;/label&gt;
```

##### Noncompliant code example

```
&lt;label&gt;Favorite food&lt;/label&gt;
```

##### Compliant solution

```
&lt;label&gt;
 &lt;MyCustomInput /&gt;
 Favorite food
&lt;/label&gt;
```

**📚 Risorse:**

#### Documentation

 - [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y) - Rule [label-has-associated-control](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/label-has-associated-control.md)
 

 - MDN web docs - [The Label element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label) 

 - W3C - [Info and Relationships](https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships) 

 - W3C - [Labels or Instructions](https:/...

---
