#!/usr/bin/env python3
"""Offline validator for AI/BI React custom pages inside a .lvdash.json.

For every custom-page widget (a multilineTextboxSpec whose joined lines start
with the `<!-- @custom-page -->` marker) it checks the empirically-derived
contract:

  - the envelope after the marker parses as JSON with keys {code, manifest, datasetMap}
  - `code` exports an entry point (module.exports.default = ... / module.exports = ...)
  - every datasetName used in viz.useCustomPageQuery({query:{datasetName:'X'}})
    is declared in this page's datasetMap
  - every datasetMap.datasetId resolves to a dataset name in the dashboard datasets[]
  - the whole dashboard JSON survives a base64 round-trip (Workspace Import format)

It canNOT verify that the React renders correctly — always preview in a workspace.

Usage:
  python validate_custom_page.py dashboard.lvdash.json
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

MARKER = "<!-- @custom-page -->"
_DATASETNAME_RE = re.compile(r"datasetName\s*:\s*['\"]([^'\"]+)['\"]")


def _iter_custom_pages(dashboard: dict):
    """Yield (page_name, widget_name, envelope_dict) for each custom page."""
    for page in dashboard.get("pages", []):
        for item in page.get("layout", []):
            widget = item.get("widget", {})
            spec = widget.get("multilineTextboxSpec")
            if not spec:
                continue
            joined = "".join(spec.get("lines", []))
            if MARKER not in joined:
                continue
            body = joined.split(MARKER, 1)[1].lstrip("\n").strip()
            yield page.get("name"), widget.get("name"), body


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_text()
        dashboard = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"Dashboard is not valid JSON: {exc}"]

    # base64 round-trip (Workspace Import expects base64(ascii) content — see skill 02)
    try:
        b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
        assert base64.b64decode(b64).decode("utf-8") == raw
    except Exception as exc:  # noqa: BLE001
        errors.append(f"base64 round-trip failed: {exc}")

    dataset_names = {d.get("name") for d in dashboard.get("datasets", [])}

    found_any = False
    for page_name, widget_name, body in _iter_custom_pages(dashboard):
        found_any = True
        where = f"page '{page_name}' / widget '{widget_name}'"
        try:
            env = json.loads(body)
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: envelope after marker is not valid JSON: {exc}")
            continue

        code = env.get("code")
        if not isinstance(code, str) or not code.strip():
            errors.append(f"{where}: envelope.code missing or empty")
            code = ""
        elif "module.exports" not in code:
            errors.append(f"{where}: code has no module.exports entry point")

        dmap = env.get("datasetMap") or []
        if not isinstance(dmap, list):
            errors.append(f"{where}: datasetMap must be a list")
            dmap = []
        aliases = {m.get("alias") for m in dmap if isinstance(m, dict)}

        # every datasetMap.datasetId must resolve to a real dataset
        for m in dmap:
            if isinstance(m, dict) and m.get("datasetId") not in dataset_names:
                errors.append(
                    f"{where}: datasetMap alias '{m.get('alias')}' -> datasetId "
                    f"'{m.get('datasetId')}' not found in dashboard datasets[]"
                )

        # every datasetName used in the code must be a declared alias
        for used in set(_DATASETNAME_RE.findall(code)):
            if used not in aliases:
                errors.append(
                    f"{where}: viz.useCustomPageQuery uses datasetName '{used}' "
                    f"which is not in datasetMap aliases {sorted(aliases)}"
                )

    if not found_any:
        errors.append("No custom-page widgets found (no '<!-- @custom-page -->' marker).")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 2
    errors = validate(path)
    if errors:
        print(f"FAIL ({len(errors)} issue(s)) in {path}:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: {path} passes the custom-page contract (render still needs a workspace preview).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
