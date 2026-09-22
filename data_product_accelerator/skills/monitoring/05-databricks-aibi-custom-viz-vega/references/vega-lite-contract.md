# Vega-Lite Custom Visualization — Contract

Authoritative source: https://docs.databricks.com/aws/en/dashboards/manage/visualizations/custom-visualizations
(Public Preview, last verified 2026-09-21). This file is a distilled, machine-usable copy.

## The authoring flow

1. Select a dashboard **dataset** (a standard `queryLines` dataset — see `02-databricks-aibi-dashboards`).
2. Add a widget → **Custom Viz** under **Advanced visualization**.
3. **Fields** section: add each field you will reference. Each field has a unique **Name**. The spec
   references data by that Name, not by the raw SQL column.
4. Paste the **Vega-Lite JSON** into the spec editor.

## Data binding

The widget's query result is exposed to the spec under a reserved data name:

```json
"data": { "name": "databricks_query" }
```

Only the columns you added in the **Fields** section are projected into `databricks_query`, keyed by
their **Name**.

## Referencing columns

| Context | Syntax |
|---------|--------|
| Encoding | `"field": "{FieldName}"` |
| Expression / transform | `datum["{FieldName}"]` or `datum.{FieldName}` |

Example:

```json
"encoding": { "x": { "field": "xField", "type": "quantitative" } }
```
```json
{ "calculate": "datum.r * cos(datum.angle)", "as": "x" }
```

## Container sizing (always include)

```json
"width": "container",
"height": "container",
"config": { "autosize": { "type": "fit", "contains": "padding" } }
```

## Minimal skeleton

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": { "name": "databricks_query" },
  "width": "container",
  "height": "container",
  "config": { "autosize": { "type": "fit", "contains": "padding" } },
  "mark": { "type": "bar" },
  "encoding": {
    "x": { "field": "categoryName", "type": "nominal" },
    "y": { "field": "salesValue", "type": "quantitative" }
  }
}
```

## Supported / unsupported

- Vega-Lite v5 and v6 schemas are used in the official examples.
- **Treemaps are not supported** (Vega-Lite has no treemap mark).
- Network/tree layouts must be **pre-computed in SQL** (emit x/y coordinates per point); Vega-Lite
  plots the points you provide, it does not run a force layout. The official phylogenetic-tree example
  emits `record_type` rows (`path` / `node` / `label`) rendered as separate `layer`s.

## `.lvdash.json` embedding — the `custom-vega-viz` widget

The official docs describe the UI flow and the Vega-Lite spec but not the JSON representation. The
shape below is confirmed empirically from 28 `custom-vega-viz` widgets across two deployed dashboards
(2026-09-21). The feature is Public Preview, so re-confirm by previewing after deploy.

```json
{
  "widget": {
    "name": "<widget-id>",
    "queries": [
      {
        "name": "main_query",
        "query": {
          "datasetName": "<dataset name from datasets[]>",
          "fields": [
            { "name": "colA", "expression": "`colA`" },
            { "name": "colB", "expression": "`colB`" }
          ],
          "disaggregated": true
        }
      }
    ],
    "spec": {
      "version": 1,
      "widgetType": "custom-vega-viz",
      "frame": { "showTitle": true, "title": "…", "showDescription": true, "description": "…" },
      "data": { "queryName": "main_query" },
      "encodings": { "fields": [ { "fieldName": "colA" }, { "fieldName": "colB" } ] },
      "jsonSpec": { "type": "vega-lite", "spec": "<vega-lite spec serialized as a JSON string>" }
    }
  },
  "position": { "x": 0, "y": 0, "width": 7, "height": 5 }
}
```

Invariants:

- `spec.widgetType = "custom-vega-viz"`, `spec.version = 1`.
- `spec.jsonSpec = { "type": "vega-lite", "spec": "<string>" }` — the Vega-Lite spec is a **string**.
- `spec.data.queryName` = a `queries[].name`.
- `spec.encodings.fields[].fieldName` ⊆ `queries[].query.fields[].name`; those Names are what the Vega
  spec references. Inside the spec, data binds to `{"name": "databricks_query"}`.
- `disaggregated: true` (stream raw rows; aggregate in the Vega `transform`).

### Builder (do not hand-escape)

```python
import json

def custom_vega_widget(name, dataset_name, fields, vega_spec, title, description="",
                       position=None):
    """fields: list[str] of column names used by the chart.
       vega_spec: dict (a Vega-Lite spec with data={"name":"databricks_query"})."""
    return {
        "widget": {
            "name": name,
            "queries": [{
                "name": "main_query",
                "query": {
                    "datasetName": dataset_name,
                    "fields": [{"name": f, "expression": f"`{f}`"} for f in fields],
                    "disaggregated": True,
                },
            }],
            "spec": {
                "version": 1,
                "widgetType": "custom-vega-viz",
                "frame": {"showTitle": True, "title": title,
                          "showDescription": bool(description), "description": description},
                "data": {"queryName": "main_query"},
                "encodings": {"fields": [{"fieldName": f} for f in fields]},
                # jsonSpec.spec MUST be a string — json.dumps handles the escaping:
                "jsonSpec": {"type": "vega-lite", "spec": json.dumps(vega_spec)},
            },
        },
        "position": position or {"x": 0, "y": 0, "width": 6, "height": 5},
    }
```

Deploy the containing dashboard exactly as in `02-databricks-aibi-dashboards` (base64 Workspace Import
or `bundle deploy`).
