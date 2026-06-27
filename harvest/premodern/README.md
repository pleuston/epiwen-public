# Premodern Sources register

A register of **premodern Chinese epigraphy works** (金石學) for the Epiwen app's
*References → Premodern Sources* page.

## Source

Built (READ-ONLY) from the finished obsidian-vault work:

- `projects/AI responses/kuhn-stahl-dryrun/`
  - `entries.json` — 1,008 works from **Kuhn & Stahl 1991**, an annotated bibliography of
    **石刻史料新編 (SKSLXB)**; carries the *verified* SKSLXB locators (`series.volume:page`),
    juan, period covered, author dates, and catalogue concordances (HY/LC/UC/FZ/SKTBSY).
  - `ks-concordance.json` — clean CJK titles + the matched vault work-page (→ author).
- `knowledge base/Texts/Epigraphy 金石學/*《*》*.md` — the broader epigraphy work canon
  (clean 撰者 + 著作 from the filename), so the register is **not limited to SKSLXB**.

## Join

Clean titles come from `ks-concordance.json`; the precise SKSLXB locator comes from
`entries.json`, attached by **per-K&S-page positional alignment** (both list a page's works
top-to-bottom). The alignment is taken only where a page's two counts agree, so a wrong
locator is never emitted — works on mismatched pages keep their **series (輯)** instead.

## Output

- `premodern.json` — the register (1,789 works; 953 in SKSLXB, 534 with a precise locator).
- `skslxb-toc.json` — SKSLXB contents grouped by series (輯), for `skslxb.html`.

Both are copied into the app repo (`pleuston/epiwen`) for relative, no-auth fetch.

## Caveats

- Precise locators resolve for 534/953 SKSLXB works; the rest show the series only.
- Authors fill where the K&S entry matched a vault work page, or the work-page filename
  carries one; otherwise blank.
- The K&S dryrun covers 第一–三輯 (series 1–3); 第四輯 is not yet present.
- **No paratexts** (序/跋/四庫提要) and **no inscription 目錄** — works/bibliography only.

Regenerate: `python3 build_premodern.py`
