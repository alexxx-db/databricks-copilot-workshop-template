---
name: genie-discover-ontology
description: Contract and guardrails for authoring the Genie Ontology in Databricks Discover — domains, subdomains, Pages, and a Question→Metric View Routing Page. Use when modeling a Discover domain, drafting Pages for measures, or writing a routing Page for a Genie Accelerator track (deck Exercises 4 and 5). This is a REFERENCE + DRAFTING-CONTRACT skill, not an automation skill: Pages have NO public create/update API, so Genie Code DRAFTS content inside the Discover UI editor and a human publishes. Codifies the Beta limits, Manage Discovery permission, the chunk-safe sentence rule, the domain ID-vs-name gotcha, and what a good Domain / Page / Routing Page contains. Points back to the Step 11–13 prompt templates rather than duplicating them; hands off to genie-space-patterns for the Space itself.
clients: [ide_cli, genie_code]
bundle_resource: none
deploy_verb: none
deploy_note: "No public create/update API for Pages (Beta) — nothing to bundle-deploy. Domains/subdomains and Pages are authored in the Discover UI (Catalog → Discover); Genie Code drafts field contents and the user publishes. Needs Manage Discovery on the domain. Pages currently ground Genie One citations; Genie Agent / Genie Code integration is roadmap."
coverage: full
metadata:
  author: prashanth subrahmanyam
  version: "0.1"
  domain: semantic-layer
  role: worker
  pipeline_stage: 6
  pipeline_stage_name: semantic-layer
  called_by:
    - semantic-layer-setup
  standalone: true
  last_verified: "2026-09-13"
  volatility: high
---

# Genie Discover Ontology (Domains, Pages, Routing)

## Overview

The **Genie Ontology** lives in **Databricks Discover** (Catalog → Discover): a **domain** with
3–5 **subdomains**, one or more **Pages** (business definitions for measures/terms), and a
**Routing Page** that maps how people phrase questions to the governed Metric View + measure that
should answer them. It is deck **Exercise 4** (Domain + Pages) and **Exercise 5** (Routing Page) of
the Genie Accelerator track.

**Core principle — this skill does not automate; it makes drafts consistent.** Genie Code already
owns the mechanics (drafting Page fields, proposing synonyms, mapping terms). This skill exists so
those drafts land the same way every time — chunk-safe, formula-anchored, governed-source-linked —
and so the Beta limits and permissions are stated once. **If Genie Code + the Discover UI can do it
natively, describe the contract; do not re-implement it.**

---

## When to Use This Skill

Use this skill when:
- Modeling a Discover **domain + subdomains** for a Genie Accelerator track (Step 11).
- Drafting **Pages** for the signed-off measures (Step 12).
- Writing the **Question → Metric View Routing Page** (Step 13).
- Explaining, in the app's "how it works," what Discover/ontology is and its Beta limits.

Do **not** use this skill for the Genie Space itself (instructions, data assets, benchmarks,
optimize loop) — that is `03-genie-space-patterns`. See the hand-off table below.

---

## Hard limits — state these before you touch Discover

| Fact | Consequence for the workflow |
|---|---|
| **Pages is Beta.** | Expect UI/behaviour changes; keep the "how it works" caveat visible. |
| **No public create/update API for Pages.** | Genie Code cannot create Pages headlessly. It **drafts the field contents; a human pastes/publishes** in the Discover UI Page editor. Never claim a Page was "created" via API/CLI. |
| **Needs `Manage Discovery` permission on the domain.** | Without it, bulk-import and Page publish silently fail. Check first. |
| **Pages currently ground *Genie One* (citations), not Genie Agents / Genie Code yet.** | Set expectations: authoring Pages improves Genie One answers now; Agent/GC consumption is roadmap. Do not promise the Genie Space will read Pages. |
| **Domains/subdomains ARE quick to create in the UI.** | UI-first is the *preferred* path (a few clicks, easy to see). Genie Code assist is a fallback, not the default. |

---

## Step 11 — Domain + subdomains (UI-first)

**Preferred: create it in the Discover UI** — Catalog → Discover → New domain → add 3–5 subdomains
covering the PRD scope. **If the workshop pre-created a domain, use it** — skip creation, just open
it and capture the IDs.

- **Capture the domain ID and every subdomain ID to `.vibecoding-state.md`.** Later steps
  (Pages, bulk import) need the internal **ID**, not the display **name**.
- Genie Code's role here is *read-only assist*: show the IDs, confirm the taxonomy matches the PRD.
- **Gate:** a domain with 3–5 subdomains exists (new or pre-created); IDs saved to state.

*Optional Genie Code assist (fallback only — prefer the UI above):*

```
Read docs/design_prd.md and .vibecoding-state.md first — the domain scope follows the PRD.

If a domain called <domain> already exists, use it — just show me its domain and subdomain IDs.
Otherwise create a domain called <domain> with these subdomains: <subdomain_1>, <subdomain_2>,
<subdomain_3>, covering <one sentence describing scope> for <function>.

Either way, show me the domain and subdomain IDs and save them to .vibecoding-state.md.
```

---

## Step 12 — Page authoring contract

A Page is drafted by Genie Code in the Discover UI Page editor, then published by a human. Every
Page for a measure MUST contain:

1. **Definition** — one paragraph, plain business language.
2. **Exact formula** — naming the **governed Metric View** (`<write_catalog>.<write_schema>.<metric_view>`)
   and the measure, not the raw tables.
3. **Synonyms** — every way someone asks: the formal name, the acronym, the informal phrasing, and
   any legacy name from an old system.
4. **≥1 negative rule** — an explicit "never do this" (e.g. "never average AOV across periods").
5. **Related asset** — the governed Metric View linked.

### The one rule that actually matters: chunk-safe sentences

**Write every rule sentence so it names its table/measure inside the sentence itself.** Pages are
**split into chunks before retrieval**, so a sentence that leans on the Page title or a heading
arrives orphaned and loses its meaning.

- ❌ "Never average this across periods." *(orphaned — "this" is lost after chunking)*
- ✅ "Never average `order_revenue_metrics.average_order_value` across periods — AOV is non-additive."

**Gate:** two published Pages, each with the five elements above, chunk-safe sentences, drafts
reviewed before publish, published Page IDs recorded to `.vibecoding-state.md`.

Prompt templates (author + optional glossary bulk-import): **Step 12** in the phase1 prompts doc.

---

## Step 13 — Routing Page (highest-return exercise)

One Page, "Question to Metric View Routing," that maps phrasings → (Metric View, measure) for
**every measure in the signed-off inventory** (`docs/genie_brief.md`).

- A **flat table**: for each measure list 4–5 phrasings (formal, acronym, informal, legacy) → the
  governed Metric View + exact measure.
- A short intro: this Page routes questions to governed sources and should be checked before
  querying raw tables.
- Link the Metric View as a related asset; **name an owner**.
- **Gate:** one Routing Page covering every inventory measure, published, with a named owner; Page
  ID + owner recorded to `.vibecoding-state.md`.

Why it wins: it replaces Genie's table-inference with a lookup a person already got right.

Prompt template: **Step 13** in the phase1 prompts doc.

---

## Gotchas

- **ID vs name.** Bulk-import and Page creation take the internal **domain ID**, not the display
  name. Most bulk-import misses are a name passed where an ID was needed — pull the ID from
  `.vibecoding-state.md` (captured in Step 11).
- **Missing `Manage Discovery`.** The other common bulk-import/publish failure. Verify the
  permission before drafting a batch.
- **"Created via API" is wrong.** There is no public Pages create/update API. Frame every result as
  "drafted → reviewed → published in the Discover UI."
- **Don't promise Space consumption.** Pages ground Genie One today; do not tell users the Genie
  Space/Agent will read them yet.

---

## 🔀 Hand-off table

| User Says / Task Involves | Load Instead |
|---|---|
| Genie **Space** instructions, data assets, benchmarks | `03-genie-space-patterns` |
| Genie Space **optimize / curation loop** (5-mode, append-only) | `03-genie-space-patterns` (Rule 17) |
| Deploy a Space from JSON, export/import, CI/CD | `04-genie-space-export-import-api` |
| **Metric View** authoring, synonyms, MEASURE() | `01-metric-views-patterns` |

**This skill** covers the *ontology* around the data (Discover domains, Pages, routing). The Space
skills cover the *agent* that answers questions. Pages ground Genie One; the Space serves Genie
Agent / Genie Code.

---

## Gate checklist (record results in `.vibecoding-state.md`)

- [ ] Domain + 3–5 subdomains exist (new or pre-created); **domain ID + subdomain IDs** saved.
- [ ] `Manage Discovery` permission confirmed on the domain.
- [ ] ≥2 measure Pages published, each: definition, formula naming the Metric View, synonyms
      (formal/acronym/informal/legacy), ≥1 negative rule, related asset; **chunk-safe sentences**.
- [ ] Routing Page published, covering **every** inventory measure, with a named owner.
- [ ] All Page IDs + owner recorded to state; drafts were reviewed before publish.
