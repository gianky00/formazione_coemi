# 🔴 RELIABILITY Issues

**Totale:** 1
**Tempo:** 5min

---

## 📄 `guide_frontend/src/components/Sidebar.jsx` (1)

### Riga 75 🟡
**Problema:** Either remove this useless object instantiation of "globalContext.QWebChannel" or use it.

```jsx
     73: 
     74:     if (globalContext.qt?.webChannelTransport) {
 >>> 75:       new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     76:         if (c.objects?.bridge) {
     77:             setBridge(c.objects.bridge);
```

**❓ Perché:**
Creating an object without assigning it to a variable or using it in any function means the object is essentially created for no reason and may be
dropped immediately without being used. Most of the time, this is due to a missing piece of code and could lead to an unexpected behavior.

If it’s intended because the constructor has side effects, that side effect should be moved into a separate method and called directly. This can
help to improve the performance and readability of the code.

```
new MyConstructor(); // Noncompliant: object may be dropped
```

Determine if the objects are necessar

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`Object.prototype.constructor`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/constructor) 

  -  MDN web docs - [constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor) 

  -  MDN web docs - [`new` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference

---
