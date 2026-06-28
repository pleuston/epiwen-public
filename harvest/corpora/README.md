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

`modern-corpora.json` — **732 corpora**: 50 national · 492 by province (34 provinces) ·
185 by site (35 sites) · 5 supplement. 639 with a year, 192 with ISBN, ~250 with a located
holding, 33 gap-fill (✚) additions.

## Caveats

- Fields are parsed positionally from prose; author/year are occasionally approximate.
- "Holdings" = where a copy was machine-located during the fan-out (not exhaustive);
  WorldCat / LoC / Google Books were bot-walled and are not claimed.
