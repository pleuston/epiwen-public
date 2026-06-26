# European collections of Chinese rubbings — survey

The backbone for Europe is the **EFEO union database « Estampages chinois conservés
en Europe »** (dir. **Jean-Pierre Drège**, software Richard Schneider, funded by the
**Chiang Ching-kuo Foundation**) — purpose-built to catalogue Chinese rubbings across
European institutions.

- **Live database:** https://estampages.efeo.fr/  (search: `rchrchch2.php`; the old
  `www.efeo.fr/estampages/` path now redirects to EFEO's WordPress site — archived at
  the Wayback Machine, 2025-10).
- **Documented totals (verbatim):** the four French collections hold *« environ 4000
  estampages »*; *« L'ensemble des collections européennes dépasse les dix mille
  exemplaires »* (>10,000) — `programme.php`.
- **Per-institution pages** are `SA.php` / `MG.php` / `IHEC.php` / `EFEO.php` /
  `BodL.php` / `BL.php` / `RM.php`.

> Counts below are the EFEO/published figures where stated, else "—" (confirmed holder,
> count unpublished). Several institutional sites return HTTP 403 to scripted requests
> (BnF Gallica, British Museum, NMS, SOAS, Cambridge CUDL) — they work in a browser.

## EFEO union database members

| code | institution | city | rubbings | EFEO page |
|---|---|---|--:|---|
| SA | Société asiatique | Paris | 1,500+ sheets (~1,200 w/ photos); Chavannes, Longmen | `SA.php` |
| MG | Musée Guimet (MNAAG) | Paris | ≥1,000 (Chavannes, Segalen, d'Ollone) | `MG.php` |
| IH | Institut des hautes études chinoises (Collège de France) | Paris | ~700 Tang epitaphs (~600 Henan; des Rotours 1933) | `IHEC.php` (+ Salamandre) |
| EF | École française d'Extrême-Orient | Paris | 379 (Zhou–early Republic); **hosts the DB** | `EFEO.php` |
| OB | Bodleian Libraries, Oxford | Oxford | — (Lockhart, Backhouse ink-squeezes) | `BodL.php` (+ east-asian.bodleian) |
| BL | British Library | London | — | `BL.php` |
| ZR | Museum Rietberg | Zürich | — | `RM.php` |
| BM | British Museum | London | — (Nestorian Stele rubbing 1989,1004) | union DB |
| SF | Museum of Far Eastern Antiquities (Östasiatiska) | Stockholm | — (own DB Carlotta) | union DB |
| NG | National Gallery Prague | Prague | — | union DB |

## Other verified European holders (own resources)

| institution | city | rubbings | resource |
|---|---|--:|---|
| **Bibliothèque nationale de France** | Paris | **≥10,000 sheets** (Pelliot, Beilin/Xi'an) — plausibly Europe's largest; **not** in the EFEO DB; no published total | Gallica / on-site catalogue |
| **Buddhist Stone Sutras in China** (Heidelberg Academy) | Heidelberg | — (Western scholarly corpus; Shandong/Henan/Hebei/Shaanxi/Sichuan/Fangshan) | **stonesutras.org** (Ledderose) |
| Ashmolean Museum | Oxford | — (Beilin) | Eastern Art Online (Jameel Centre) |
| Musée Cernuschi | Paris | ~400 (single-source) | museum site; 2025–26 exhibition |
| Victoria & Albert Museum | London | Nestorian Stele rubbing E.690-1922 | collections.vam.ac.uk |
| National Museums Scotland | Edinburgh | Wu Liang Shrine + Nestorian rubbings | nms.ac.uk |
| SOAS University of London | London | Chinese Rubbings digital collection | digital.soas.ac.uk |
| Cambridge University Library | Cambridge | CUDL Chinese rubbings | cudl.lib.cam.ac.uk |
| Biblioteca Apostolica Vaticana | Vatican | Nestorian Stele rubbing Barb. or. 151; Jesuit-era materials | DigiVatLib |

## Investigated and EXCLUDED (manuscripts/other, not rubbings)

Staatsbibliothek zu Berlin (CrossAsia), Bayerische Staatsbibliothek Munich, Institute
of Oriental Manuscripts RAS (Tangut/Dunhuang **manuscripts**), Leiden (its estampages
are Indian/Indonesian), Museo delle Civiltà / ex-IsIAO Rome, Naples L'Orientale,
Needham Research Institute (Dunhuang **photographs**), Royal Danish Library. The **IDP
network is manuscripts, not rubbings** — do not treat "IDP partner" as a rubbing holder.

## Catalogued in Epiwen

**19 European collections** in `collections.json`: the 7 EFEO-union members (connector
`efeo-estampages`, `rubbing_site` → their `estampages.efeo.fr/<page>.php`), plus BnF,
Heidelberg/stonesutras, Ashmolean, Cernuschi, V&A, NMS, SOAS, Cambridge UL, Vatican,
British Museum, Stockholm, Prague. `est_count` carries the documented estimate so the
overview table sorts them by rubbing count (BnF 10,000 → SA 1,500 → Guimet 1,000 →
IHEC 700 → Cernuschi 400 → EFEO 379 → …).

_US benchmarks for scale (not catalogued here as European): Field Museum >7,500 (Laufer);
UC Berkeley ~1,500 (harvested: 2,745 records). Source: parallel web research, June 2026._
