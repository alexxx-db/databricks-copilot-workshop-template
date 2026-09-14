# Step 0 — PRD  (Run A)

- **Date / operator:** 2026-09-13 / prashanth.subrahmanyam
- **Type:** A (app-generated / faithful FM-API mimic of `apps_lakebase/prompts/sections/03-prd_generation.md`)
- **Schema:** `samples.tpch`
- **BYO file:** none

## Session open (`vibecoding-state` resolve_root)

Resolved on live Genie Code:

| Field | Value |
|---|---|
| client_context | `genie_code` |
| artifact_root | `/Workspace/Users/prashanth.subrahmanyam@databricks.com/vibe-coding-workshop` |
| skills_install_root | `/Workspace/Users/prashanth.subrahmanyam@databricks.com/.assistant/skills/vibe-coding-workshop` |
| skill_ref_root | `skills/vibe-coding-workshop` |
| cli_channel | `runDatabricksCli` |
| detected_via | `runDatabricksCli` |

`.git` confirmed at artifact root (bundles will be recognized). `genie_code_manifest_loaded: true`.
State file created at `<ARTIFACT_ROOT>/.vibecoding-state.md` with Environment Capabilities populated;
Workshop Choices / Global Variables / spec sections left `<pending>` for bootstrap.

## Prompt used (verbatim)

The Step-0 PRD prompt from the runbook (Retail · Order & Revenue Analytics), produced by applying the
real `03-prd_generation.md` `## System Prompt` to the use case. Saved as the app-generated artifact.
(See `../../2026-09-13-genie-accelerator-phase1-prompts.md` Step 0 for the full text.)

## Genie Code transcript (summary)

> "I'll resolve `<ARTIFACT_ROOT>` from the prior session state and create the PRD at the correct path.
> artifact_root = /Workspace/Users/prashanth.subrahmanyam@databricks.com/vibe-coding-workshop.
> PRD saved to `<ARTIFACT_ROOT>/docs/design_prd.md`."

Product = **RevenueScope**, an Order & Revenue Analytics experience with three personas (Revenue
Analyst, Sales Operations Manager, Finance Business Partner), three Happy-Path user journeys, ten
functional requirements, five-milestone release plan (Foundation → GA). No table definitions,
schemas, APIs, or implementation details.

## Artifact(s) produced

- `docs/design_prd.md` (RevenueScope PRD)

## Gate result

- [x] `docs/design_prd.md` exists with User Journeys + High-Level Data Entities.
- [x] Distinct Finance / Sales-Ops personas named — the *organic* seed for later conflict discovery
      (PRD states no metric definition, so it doesn't inject the conflict).
- [x] App-generated PRD prompt saved separately (this file / runbook Step 0).

## Notes

- Resolved ARTIFACT_ROOT correctly to the git-cloned user project (not the `.assistant/skills` copy,
  not the page CWD) — the artifact-placement rule held on live Genie Code.
