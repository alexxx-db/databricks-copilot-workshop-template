# React Authoring Patterns for Custom Pages

> Empirical patterns from the exemplar. `R = require('react')`; `viz` is an injected global.

## Module skeleton

```js
var R = require('react');

// --- module-scope helpers (theme, formatting) ---
function toneFg(kind, isDark) {
  if (kind === 'green') return isDark ? '#4ade80' : '#137333';
  if (kind === 'yellow') return isDark ? '#fbbf24' : '#8a5a00';
  if (kind === 'red') return isDark ? '#f87171' : '#c5221f';
  return isDark ? '#9aa0a6' : '#6b7280';
}
function toneBg(kind, isDark) {
  if (isDark) return kind === 'green' ? 'rgba(74,222,128,0.16)'
    : kind === 'yellow' ? 'rgba(251,191,36,0.16)'
    : kind === 'red' ? 'rgba(248,113,113,0.18)' : 'rgba(255,255,255,0.08)';
  return kind === 'green' ? '#e6f4ea' : kind === 'yellow' ? '#fdecc8'
    : kind === 'red' ? '#fde2e1' : '#eef0f2';
}
function money(v) {
  if (v == null || isNaN(Number(v))) return '\u2014';
  var n = Number(v);
  if (Math.abs(n) >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
  if (Math.abs(n) >= 1e3) return '$' + (n / 1e3).toFixed(1) + 'K';
  return '$' + Math.round(n);
}

// --- data-driven section ---
function Section(props) {
  var isDark = props.theme === 'dark';
  var res = viz.useCustomPageQuery({
    query: { datasetName: 'main', fields: [
      { fieldName: 'label', expression: '`label`' },
      { fieldName: 'value', expression: '`value`' }
    ] }
  });
  if (!(res && res.rows && res.rows.length)) {
    return R.createElement(Skeleton, { theme: props.theme, height: 120 });
  }
  var rows = res.rows;
  return R.createElement('div', { style: { display: 'flex', gap: 12 } },
    rows.map(function (r, i) {
      return R.createElement('div', {
        key: i,
        style: {
          flex: 1, padding: 16, borderRadius: 8,
          background: toneBg('grey', isDark),
          color: toneFg('grey', isDark)
        }
      },
        R.createElement('div', { style: { fontSize: 12, opacity: 0.7 } }, r.label),
        R.createElement('div', { style: { fontSize: 22, fontWeight: 700 } }, money(r.value)));
    }));
}

function App(props) {
  var isDark = props.theme === 'dark';
  return R.createElement('div', {
    style: { padding: 24, fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif',
             color: isDark ? '#f5f5f5' : '#1b1b1b' }
  },
    R.createElement('h1', { style: { margin: '0 0 14px', fontSize: 24, fontWeight: 700 } }, 'Title'),
    R.createElement(Section, props));
}

module.exports.default = App;
```

## Loading skeleton (inject keyframes once)

```js
function Skeleton(props) {
  var isDark = props.theme === 'dark';
  R.useEffect(function () {
    if (document.getElementById('cp-skeleton-kf')) return;
    var st = document.createElement('style');
    st.id = 'cp-skeleton-kf';
    st.textContent = '@keyframes cpSkeleton{0%{background-position:-200% 0}100%{background-position:200% 0}}';
    document.head.appendChild(st);
  }, []);
  var base = isDark ? '#2a2a2a' : '#e9ecef';
  var hi = isDark ? '#3a3a3a' : '#f5f7fa';
  return R.createElement('div', { style: {
    height: props.height || 80, borderRadius: 8,
    background: 'linear-gradient(90deg,' + base + ' 25%,' + hi + ' 50%,' + base + ' 75%)',
    backgroundSize: '200% 100%', animation: 'cpSkeleton 1.4s ease-in-out infinite'
  } });
}
```

## Rules of thumb

- **Guard every query**: `if (!(res && res.rows && res.rows.length)) return <skeleton/empty>;`.
- **Theme everything** off `props.theme`; never hardcode a single-mode color.
- **Pass `props` down** to child components so `theme`/`height` propagate.
- **`datasetName` is the alias** from `datasetMap`, not the underlying dataset name.
- Keep helpers at **module scope** (outside components) so they aren't re-created each render.
- Optional `'data-cp-element-id': 'cp_<uuid>'` on elements aids the visual editor; harmless if omitted.
