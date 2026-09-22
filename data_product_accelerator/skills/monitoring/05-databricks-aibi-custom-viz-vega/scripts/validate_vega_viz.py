#!/usr/bin/env python3
"""Offline validator for AI/BI Vega-Lite custom visualizations.

Two modes (auto-detected):

1. Bare Vega-Lite spec (a .json spec). Checks:
   - valid JSON
   - data bound to the reserved source  {"name": "databricks_query"}
   - width/height are "container"
   - referenced fields are covered by --fields (optional)
   - any cross-filter param uses the reserved name + point selection

2. Full dashboard (.lvdash.json). For every `custom-vega-viz` widget checks the
   whole field-alignment chain:
   - spec.jsonSpec.spec is a STRING that parses as Vega-Lite JSON
   - inner spec binds data to "databricks_query" and uses container sizing
   - spec.data.queryName matches a queries[].name
   - spec.encodings.fields[].fieldName == queries[].query.fields[].name
   - every field the Vega spec references is declared in encodings.fields

Runtime rendering still requires a workspace preview; this only catches the
structural mistakes that account for most "blank chart / no fields" failures.

Usage:
  python validate_vega_viz.py spec.json --fields categoryName salesValue
  python validate_vega_viz.py spec.json            # skip field-coverage check
  python validate_vega_viz.py dashboard.lvdash.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _collect_fields(node, found: set[str]) -> None:
    """Walk the spec collecting every referenced field/column name."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "field" and isinstance(value, str):
                found.add(value)
            if key in ("calculate", "expr", "filter") and isinstance(value, str):
                # datum.foo  and  datum["foo"] / datum['foo']
                found.update(re.findall(r"datum\.([A-Za-z_]\w*)", value))
                found.update(re.findall(r"datum\[[\"']([^\"']+)[\"']\]", value))
            _collect_fields(value, found)
    elif isinstance(node, list):
        for item in node:
            _collect_fields(item, found)


def _collect_derived(node, derived: set[str]) -> None:
    """Collect fields CREATED by transforms (`as` outputs) so they aren't flagged
    as undeclared. `as` may be a string (window/aggregate/calculate) or a list (fold)."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "as":
                if isinstance(value, str):
                    derived.add(value)
                elif isinstance(value, list):
                    derived.update(v for v in value if isinstance(v, str))
            _collect_derived(value, derived)
    elif isinstance(node, list):
        for item in node:
            _collect_derived(item, derived)


def _collect_inline_data_fields(node, inline: set[str]) -> None:
    """Collect object keys from inline layer data (`data.values: [{...}]`). These are
    local to an annotation/reference layer and are NOT dataset (databricks_query) fields."""
    if isinstance(node, dict):
        data = node.get("data")
        if isinstance(data, dict) and isinstance(data.get("values"), list):
            for row in data["values"]:
                if isinstance(row, dict):
                    inline.update(k for k in row.keys() if isinstance(k, str))
        for value in node.values():
            _collect_inline_data_fields(value, inline)
    elif isinstance(node, list):
        for item in node:
            _collect_inline_data_fields(item, inline)


def _find_mark_selection(node):
    """Return the databricks_mark_selection param dict if present."""
    if isinstance(node, dict):
        if node.get("name") == "databricks_mark_selection":
            return node
        for value in node.values():
            hit = _find_mark_selection(value)
            if hit:
                return hit
    elif isinstance(node, list):
        for item in node:
            hit = _find_mark_selection(item)
            if hit:
                return hit
    return None


def _validate_vega_spec(spec: dict, declared_fields: list[str] | None, where: str = "") -> list[str]:
    """Validate a parsed Vega-Lite spec object against the databricks_query contract."""
    errors: list[str] = []
    prefix = f"{where}: " if where else ""

    data = spec.get("data")
    if not (isinstance(data, dict) and data.get("name") == "databricks_query"):
        errors.append(prefix + 'data must be {"name": "databricks_query"}')
    if spec.get("width") != "container":
        errors.append(prefix + 'width should be "container" so the chart fills the tile')
    if spec.get("height") != "container":
        errors.append(prefix + 'height should be "container" so the chart fills the tile')

    referenced: set[str] = set()
    _collect_fields(spec, referenced)
    referenced -= {"mode", "colors", "dashboardTheme", "datum", "width", "height"}
    # fields created by transforms (window/aggregate/calculate/fold "as") are not dataset fields
    derived: set[str] = set()
    _collect_derived(spec, derived)
    referenced -= derived
    # fields from inline annotation/reference layers (data.values) are local, not dataset fields
    inline: set[str] = set()
    _collect_inline_data_fields(spec, inline)
    referenced -= inline

    if declared_fields is not None:
        missing = sorted(referenced - set(declared_fields))
        if missing:
            errors.append(
                prefix
                + "Referenced field(s) not declared: "
                + ", ".join(missing)
                + " (add to the Fields section / encodings.fields)."
            )

    sel = _find_mark_selection(spec)
    if sel is not None:
        select = sel.get("select", {})
        if select.get("type") != "point":
            errors.append(prefix + "databricks_mark_selection must use select.type = 'point'")
        if not select.get("fields"):
            errors.append(prefix + "databricks_mark_selection.select.fields must list dimension Field Names")

    return errors


def _validate_lvdash(dashboard: dict) -> list[str]:
    """Validate every custom-vega-viz widget in a .lvdash.json."""
    errors: list[str] = []
    found = 0
    for page in dashboard.get("pages", []):
        for item in page.get("layout", []):
            widget = item.get("widget", {})
            spec = widget.get("spec", {})
            if spec.get("widgetType") != "custom-vega-viz":
                continue
            found += 1
            where = f"page '{page.get('name')}' / widget '{widget.get('name')}'"

            queries = widget.get("queries") or []
            query = (queries[0].get("query", {}) if queries else {})
            query_fields = {f.get("name") for f in query.get("fields", [])}
            query_names = {q.get("name") for q in queries}

            data_ref = spec.get("data", {})
            if data_ref.get("queryName") not in query_names:
                errors.append(
                    f"{where}: spec.data.queryName '{data_ref.get('queryName')}' "
                    f"does not match a queries[].name {sorted(query_names)}"
                )

            enc_fields = {f.get("fieldName") for f in spec.get("encodings", {}).get("fields", [])}
            missing_in_query = sorted(enc_fields - query_fields)
            if missing_in_query:
                errors.append(
                    f"{where}: encodings.fields not in the query: {', '.join(missing_in_query)}"
                )

            json_spec = spec.get("jsonSpec", {})
            raw = json_spec.get("spec")
            if json_spec.get("type") != "vega-lite":
                errors.append(f"{where}: jsonSpec.type should be 'vega-lite'")
            if not isinstance(raw, str):
                errors.append(f"{where}: jsonSpec.spec must be a STRING (serialize with json.dumps)")
                continue
            try:
                vega = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{where}: jsonSpec.spec is not valid JSON: {exc}")
                continue
            # inner spec must reference only declared encodings.fields
            errors.extend(_validate_vega_spec(vega, sorted(enc_fields), where))

    if found == 0:
        errors.append("No custom-vega-viz widgets found in this dashboard.")
    return errors


def validate(spec_path: Path, declared_fields: list[str] | None) -> list[str]:
    try:
        spec = json.loads(spec_path.read_text())
    except json.JSONDecodeError as exc:
        return [f"File is not valid JSON: {exc}"]

    # dashboard file?
    if isinstance(spec, dict) and "pages" in spec and "datasets" in spec:
        return _validate_lvdash(spec)

    # otherwise treat as a bare Vega-Lite spec
    return _validate_vega_spec(spec, declared_fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AI/BI Vega-Lite custom viz spec.")
    parser.add_argument("spec", type=Path, help="Path to the Vega-Lite JSON spec")
    parser.add_argument(
        "--fields",
        nargs="*",
        default=None,
        help="Field Names declared in the widget's Fields section (enables coverage check)",
    )
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"ERROR: {args.spec} not found", file=sys.stderr)
        return 2

    errors = validate(args.spec, args.fields)
    if errors:
        print(f"FAIL ({len(errors)} issue(s)) in {args.spec}:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: {args.spec} passes the documented custom-viz contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
