# Theming & Cross-filtering — Vega-Lite Custom Viz

## Theme signals

Custom visualizations inherit the dashboard theme automatically (fonts, gridline color, transparent
background). Your spec's `config` block overrides inherited defaults. Inside Vega expressions
(`{ "expr": "..." }`) you may reference:

| Signal | Description | `[mode]` index |
|--------|-------------|----------------|
| `colors` | Pre-resolved color tokens for the active mode: `colors.textPrimary.default`, `colors.gridColor`, `colors.markHighlightColor` | **Never** — already resolved |
| `mode` | Active mode: `'light'` or `'dark'`; used to index per-mode `dashboardTheme` fields | n/a |
| `dashboardTheme` | Full owner theme: `resolvedFontSettings`, `visualizationColors[]`, `gridLineColor` | **Required** for per-mode fields |

```json
{ "expr": "dashboardTheme.resolvedFontSettings.fieldValue.fontFamily" }
{ "expr": "dashboardTheme.resolvedFontSettings.fieldTitle.fontColor[mode]" }
{ "expr": "dashboardTheme.visualizationColors[0]" }
{ "expr": "colors.markHighlightColor" }
```

Rule of thumb: use `colors.*` first (no `[mode]`); use `dashboardTheme.*[mode]` only for fonts, the
full categorical palette, or values `colors` doesn't expose.

## Cross-filtering

Add a point selection parameter named **exactly** `databricks_mark_selection`:

```json
"params": [
  { "name": "databricks_mark_selection", "select": { "type": "point", "fields": ["categoryName"] } }
]
```

Mandatory requirements:

- Name must be exactly `databricks_mark_selection` (any other name = plain parameter, no cross-filter).
- `select.type` must be `point` (interval/brush not supported as a source).
- `select.fields` = the **Field Names** from the Fields section (not raw columns).
- List only **dimension** fields; aggregated measures cannot drive a cross-filter.
- Multiple fields: `"fields": ["categoryName", "regionName"]`.

### Highlight selected marks (fill marks: bar/arc/rect)

Keep `color` bound to your field; add themed `stroke`/`strokeWidth` on selection and dim unselected
marks via `fillOpacity`:

```json
"encoding": {
  "color": { "field": "categoryName", "type": "nominal" },
  "fillOpacity": { "condition": { "param": "databricks_mark_selection", "value": 1 }, "value": 0.3 },
  "stroke": {
    "condition": { "param": "databricks_mark_selection", "empty": false, "value": { "expr": "colors.markHighlightColor" } },
    "value": null
  },
  "strokeWidth": { "condition": { "param": "databricks_mark_selection", "empty": false, "value": 2 }, "value": 0 }
}
```
