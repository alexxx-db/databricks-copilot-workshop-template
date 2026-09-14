# Import BI → governed UC Metric View (Genie Code `/importBI`)

How to turn a Tableau or Power BI file into a **governed Unity Catalog Metric View** a Genie Agent can
attach. This is the BYO lane for the Genie Accelerator track's Metric View step. The key fact:
**`/importBI` does not produce a UC Metric View directly** — it produces *local* (dashboard-scoped)
views you must **promote**.

> **Status: documented from the official docs; the live promote UI path is pending Run-B confirmation.**
> Facts below are from <https://docs.databricks.com/aws/en/dashboards/manage/import-bi> (retrieved
> 2026-09-13). Confirm the exact "Export to a Unity Catalog metric view" click-path during the Run-B
> live pass, then drop this status note.

## Prerequisite

**Partner-powered AI features must be enabled for both the account and the workspace.** Without it,
`/importBI` is unavailable. (This is an admin/account setting — verify before promising the lane in a
workshop.)

## What `/importBI` creates (all at once)

Uploading a BI file builds, in one migration run:

1. an **AI/BI dashboard** that replicates the source visualizations;
2. **local metric views** mirroring the file's measures/dimensions — **referenceable only inside that
   dashboard**, so **not reusable by a Genie Agent, notebook, or other dashboard**;
3. **dashboard relationships**, when the migration tooling detects them in the source file.

## Accepted files, size, and volume path

- Extensions: **`.twb`, `.twbx`, `.tds`, `.tdsx`** (Tableau), **`.pbit`** (Power BI).
- **Direct chat upload ≤ 100 MB.** For larger files, upload to a **Unity Catalog volume** first, then
  reference it inline:

  ```text
  /importBI
  @/Volumes/<catalog>/<schema>/<volume>/<workbook>.twb
  ```

- A `.twbx` can be unzipped and the extracted `.twb` uploaded instead (smaller payload).

## Two entry points

- **Dashboard list → Create → "Import a Power BI or Tableau report"** — creates a new dashboard + opens
  Genie Code to build it.
- **From a draft dashboard → Genie Code → New chat →** "Import from a BI tool" **or type `/importBI`**,
  then attach the file.
- **Data-model-only import:** start the import **from an empty Unity Catalog metric view** (skips the
  full dashboard replication when you only want the semantic model).

## Promote local → UC Metric View (the load-bearing step)

By default the views are **local**. To make them reusable + governed:

1. Review what the import produced (dashboard + local metric view(s)).
2. **Keep only** the view(s) that cover your signed-off measure inventory; drop the rest.
3. Use the **"Export to a Unity Catalog metric view"** action to promote the kept view into your write
   target (`<write_catalog>.<write_schema>`).

Promoted views become reusable across **dashboards, Genie Agents, and notebooks** and gain full UC
governance (**access controls, lineage, discoverability**). Databricks explicitly recommends promoting.

After promotion, treat it like any authored Metric View in this skill: run a `MEASURE()` query to prove
each approved measure returns, flag non-additive measures, and record the MV name + gate in
`.vibecoding-state.md`.

## Carry-overs into the track's next steps

- **Field aliases → synonyms.** Keep the imported field aliases; they become Metric View `synonyms:`
  (v1.1, ≤10 each) in the Synonyms step. "At least one synonym traces back to an imported alias" is the
  BYO-`/importBI` acceptance check.
- **Inventory discipline.** The promoted MV must match the signed-off brief — not the union of every
  measure the BI file happened to define.

## Gotchas

- **Local ≠ UC.** Skipping promotion is the #1 mistake — a Genie Agent cannot attach a local view.
- **Bulk-import misses** usually mean a domain/asset **name** was passed where the internal **ID** is
  required.
- **Keep the browser tab open** while the migration agent runs — navigating away interrupts it and
  leaves an unfinished result.
- **Provide a screenshot** of the source report; the agent validates layout/numbers against it and
  migrates far more accurately with one.

## Sources

- Import BI files using Genie Code — <https://docs.databricks.com/aws/en/dashboards/manage/import-bi>
- Genie Code §6c (native semantic-layer authoring) — `skills/genie-code-environment/SKILL.md`
