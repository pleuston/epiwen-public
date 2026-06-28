# Premodern Sources — register, epigraphers, concordance

Data for the Epiwen app's *References → Premodern Sources* section: a register of premodern
Chinese epigraphy works (金石學), the epigraphers who authored them, and an inscription
concordance. READ-ONLY on all sources.

## Sources

- **`kuhn-stahl-dryrun/`** (obsidian-vault) — Kuhn & Stahl 1991, annotated bibliography of
  **石刻史料新編 (SKSLXB)**: `entries.json` (verified `series.volume:page` locators) +
  `ks-concordance.json` (clean CJK titles).
- **vault epigraphy work pages** (`knowledge base/Texts/Epigraphy 金石學/*《*》*.md`) — broader
  work canon (so the register is not limited to SKSLXB).
- **`edep_sino/data-pkg/data/registers/`** — the curated predecessor app:
  - `works.xml` (1,099 works + 2,257 editions) — author→person links, editions, work relations.
  - `persons.xml` (203) + `people/*.xml` (6 canonical) — epigrapher person records.
  - `jinshi.xml` (260) — curated inscription↔work attestation concordance.
- **`skslxb-tei-md-dryrun/`** (obsidian-vault) — broad per-work 目錄 (17,619 entries / 22
  deep-parsed catalogues).

## Build

1. `python3 build_premodern.py` — assembles the register (K&S spine + vault works), then
   **merges `works.xml` by Chinese title** (work_id, author_id, editions, relations) and
   builds the **epigrapher register** (`persons.json`) with each person's authored works.
   → `premodern.json`, `persons.json`, `skslxb-toc.json`
2. `python3 build_concordance.py` — `jinshi.xml` → `inscriptions.json` (curated layer);
   `skslxb-tei-md-dryrun` → `toc/<work_id>.json` (broad per-work 目錄); back-fills
   `premodern.json` with `recorded_count` + `toc_count` per work.

All outputs are copied into the app repo (`pleuston/epiwen`) for relative, no-auth fetch.

## Outputs / counts

- `premodern.json` — 1,789 works (953 in SKSLXB, 534 precise locators; 1,044 merged with
  works.xml → 526 author→person links, 2,157 editions).
- `persons.json` — 203 epigraphers (152 with ≥1 authored work; deep bio/字號 for the 6 canonical).
- `inscriptions.json` — 260 curated inscriptions, 1,759 attestation links.
- `toc/*.json` — 22 per-work 目錄 (17,619 entries).

## Caveats / joins

- Precise SKSLXB locators come ONLY from the K&S data (works.xml has none) — 534/953.
- works.xml↔register join is by normalised Chinese title (all 1,038 works.xml titles are
  present in the register; shared vault provenance).
- 21/22 dry-run catalogues map to a works.xml work_id; 1 is keyed by title slug.
- No paratexts (序/跋/四庫提要). K&S dry-run is 第一–三輯 (no 第四輯).
