# Custom-Page Envelope — Exact Contract

> Reverse-engineered from a deployed `.lvdash.json` exemplar (2026-09-21). Not official Databricks
> documentation. Verify in your workspace.

## Where it lives

A custom page is one widget on a `PAGE_TYPE_CANVAS` page:

```json
{
  "widget": {
    "name": "<widget-id>",
    "multilineTextboxSpec": {
      "lines": [
        "<!-- @custom-page -->\n",
        "{ ...envelope JSON as a string... }"
      ]
    }
  },
  "position": { "x": 0, "y": 0, "width": 6, "height": 20 }
}
```

- The `lines` array is **joined** (concatenated) by the renderer. The joined text is:
  a first line `<!-- @custom-page -->` (the marker), then the **envelope JSON as text**.
- The custom page owns the whole page, so it is a single wide/tall widget (`width: 6`).

## The envelope

The text after the marker parses to:

```json
{
  "code": "<CommonJS React source, as a JSON string>",
  "manifest": {},
  "datasetMap": [
    { "alias": "commit", "datasetId": "commit_burn_detail" }
  ]
}
```

| Key | Meaning |
|-----|---------|
| `code` | CommonJS React source. `var R = require('react'); ... module.exports.default = App;`. Uses `R.createElement` (no JSX observed). |
| `manifest` | Observed empty (`{}`). Reserved — leave `{}` unless a verified use appears. |
| `datasetMap` | Array of `{alias, datasetId}`. `datasetId` must equal a dataset `name` in the dashboard's top-level `datasets[]`. `alias` is what the React code passes to `viz.useCustomPageQuery({query:{datasetName: alias}})`. |

## Triple-nesting / escaping

The `code` string is nested three levels deep:

1. JS source →
2. a JSON string value of `code` →
3. a string element inside `multilineTextboxSpec.lines`.

**Never hand-escape.** Build the envelope programmatically so `json.dumps` handles both encodings.

### Reference builder

```python
import json

def build_custom_page_widget(widget_name, react_code, dataset_map, position=None):
    """dataset_map: list of {"alias":..., "datasetId":...}"""
    envelope = {"code": react_code, "manifest": {}, "datasetMap": dataset_map}
    envelope_text = json.dumps(envelope)          # encodes the JS code once
    return {
        "widget": {
            "name": widget_name,
            "multilineTextboxSpec": {
                "lines": ["<!-- @custom-page -->\n", envelope_text],
            },
        },
        "position": position or {"x": 0, "y": 0, "width": 6, "height": 20},
    }

# When this widget is placed into the dashboard dict and the whole dashboard is
# json.dumps'd (then base64-encoded for Workspace Import per skill 02), the code
# string is correctly double-encoded. Do not manually add backslashes.
```

Deployment is otherwise identical to `02-databricks-aibi-dashboards` (base64 Workspace Import with
`overwrite=true`, or `bundle deploy`).
