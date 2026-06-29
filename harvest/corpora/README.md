# Modern corpora — geographic register

Data for the Epiwen app's *References → Modern Corpora* page: a searchable register of
**modern (20th–21st c.) published epigraphic corpora of China**, organized geographically.
READ-ONLY on the source.

## Source

`obsidian-vault/projects/AI responses/AI epigraphic-corpora-topographic-inventory.md` — a
2026-06 geographic fan-out web search (deduplicated; library holdings checked per-work
against Harvard-Yenching, Staatsbibliothek zu Berlin, and K10plus). A bullet-list
inventory nested as:

```
## 全國 — national / multi-province series
## 省 — by province → ### region (華北…) → #### 北京 (23) → *省級:* / *府/市級:* / *縣級:* / *專題:* …
## 名山與重要遺址 → ### 五嶽 / 石窟 / 刻經 / 碑林 / 摩崖 → #### 泰山
## 補遺 — gap-fill additions (unplaced)
```

Each entry: `- [✚] **title 漢字** (Pinyin) · author · year · publisher · ≈scope · ISBN … — _holdings_`

## Build

`python3 build_corpora.py` → `corpora.json` (copied to the app as `modern-corpora.json`).
Parses the heading hierarchy into per-record geography (section / region / province / site /
admin level), splits the ` · `-delimited fields, extracts ISBNs and holdings markers, skips
the `Method & status` notes section, and drops exact-duplicate cross-listings.

## Output / counts

`modern-corpora.json` — **1,070 corpora**: 22 national · 857 by province · 191 by site,
across **519 distinct counties/localities**. 250 with a located holding, 33 gap-fill (✚).

Two sources are merged:
- the original topographic inventory (732, holdings-checked); plus
- **`fanout-counties.json`** — a 34-province multi-agent web fan-out (896 raw → 626 new after
  title-dedup vs the verified set) targeting county/prefecture-level works.

**Verification — library catalogues only.** Three workflow passes (`verify-results.json` +
`catalog-verify-results.json`): each fan-out row had to be confirmed in an **actual library
catalogue** — CiNii Books, **NDL**, WorldCat, K10plus/GVK, NLC (国图), 讀秀, or a university
OPAC. Booksellers (douban/kongfz), blogs, news, publisher pages, and scholarly bibliographies
do **not** count. **338 kept** (CiNii ~228, NDL ~72, plus WorldCat / K10plus / NLC / Shanghai
/ Fujian / Stanford OPACs); **288 dropped** as uncatalogued (mostly local 内部資料 / committee
publications); metadata corrected from the catalogues (publishers, years, ISBNs, editors).
`build_corpora.py` keeps a web row only if catalog-confirmed and stores the catalogue
(`web_catalog`) + record URL (shown as e.g. "NDL ✓ ↗"). Verified rows lose a title collision
to a holdings-checked row.

## Geography (region → province → county/locality → site)

- The five `## 補遺` "unplaced" gap-fills are filed into their proper geography via
  `PLACE_SUPP`, keeping the ✚ marker.
- The source `## 全國` section over-collected: only **22** entries are genuinely national
  (nationwide / by-dynasty / multi-region). The other ~29 are reclassified via `RECLASS` —
  to a province (廣西/陝西/山東/山西/河南/江蘇/四川/澳門/台灣…), a region (中國西北/西南地區 →
  region-wide), or a site (響堂山/龍門/房山/泰山/黃山). Each `RECLASS` entry is explicit, so the
  reassignment is exact.
- **County/prefecture level**: every place-specific entry gets a `locality` (邯鄲, 廊坊, 蘇州,
  桂林, 晉城…). Derived from the title's place prefix, gated by the source's admin sub-level
  (`省級`/`全國`/`專題` → province-wide, no county), with era/topic qualifiers and classical
  province-aliases (齊魯/三晉…) stripped. Province-section locality leakage: **0**.

## Field accuracy

Author / year / publisher are extracted **deterministically**, anchored on the date field
(author = chunks before it, publisher = first real chunk after it) — author and publisher
share institutional vocabulary (圖書館/研究所/編輯部), so only position, not content, can
separate them. The date detector covers years, year-lists (`2011; 2002`), ranges, decades
(`1990s`), centuries (`20th–21st c.`), and dating phrases (`forthcoming`, `in preparation`,
`Republican-era`). Validated against the source: **every** emitted author/year/publisher
appears verbatim in its raw line, 725/732 carry a year (the other 7 are genuinely undated in
the source), and 0 fields are mis-assigned. Re-run `build_corpora.py` to re-validate.

## Caveats

- "Holdings" = where a copy was machine-located during the fan-out (not exhaustive);
  WorldCat / LoC / Google Books were bot-walled and are not claimed.
