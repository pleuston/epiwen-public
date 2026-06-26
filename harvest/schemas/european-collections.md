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

> **Harvest policy: do NOT harvest the EFEO site directly.** EFEO's database is an
> **aggregator / finding-aid** — it is *linked* for discovery (with basic info on what
> it holds), but for actual data Epiwen takes the **detour through each member
> institution's own online collection** where one exists (IHEC → Salamandre; Bodleian →
> east-asian.bodleian; British Museum → its collection; Stockholm → Carlotta). Members
> with **no** independent online collection (Société asiatique, Guimet, British Library,
> Rietberg, Prague) are marked `via_aggregator: "EFEO"` — discoverable through the EFEO
> record only, not yet independently harvestable.

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

### Harvestability (`harvest` field)

- **`api` — open machine API, harvestable** (8): **V&A** (REST, api.vam.ac.uk — ~125
  Chinese rubbings incl. the Nestorian rubbing), **BnF** (SRU + IIIF, Gallica),
  **Stockholm MFEA** (K-samsök/SOCH — verified), **Cambridge UL**, **Bodleian** (Digital
  Bodleian IIIF), **SOAS**, **Ashmolean** (Jameel IIIF), **Heidelberg/stonesutras** (TEI
  corpus). Each carries `api` (type) + `api_url`.
- **`request` — data by request, no open API** (9): Société asiatique, Musée Guimet,
  British Library, Rietberg, National Gallery Prague (only via the EFEO aggregator);
  Musée Cernuschi, National Museums Scotland; **British Museum** (SPARQL endpoint
  unreachable); **Vatican (DigiVatLib)** — IIIF *item-level only*, no open search API.
- **online (no confirmed bulk API)**: IHEC/Collège de France (Salamandre).
- **aggregator**: the EFEO union database (link only — never harvested directly).

## Korea (한국) — 9 collections (Asia ▸ South Korea)

Korean epigraphy is written in literary Chinese, so Korean rubbing collections are in
scope. Verified by follow-up research:

**`api` (harvestable):**
- **Korean Epigraphy DB 한국금석문 — NRICH** (국립문화유산연구원). The old `gsm.nrich.go.kr`
  is **dead**; live DB on the 지식이음 portal (`portal.nrich.go.kr/.../ksmUsrList.do`),
  **6,557 records**. Best target: **`http://portal.nrich.go.kr/kor/openapi.do?idx=51`** —
  live XML, **keyless**, CC-BY (data.go.kr mirror 15015633 may need a key). **NB: this is
  an INSCRIPTION database, not a rubbing repository** — each record = a stone monument
  (title, dynasty, dimensions, location, script) + 판독문 transcription, 해석문
  interpretation, and 탁본 rubbing/photo images where available. The 6,557 are inscriptions,
  not rubbings; it maps to Epiwen's inscription/object model, rubbings being one witness.
- **National Museum of Korea / e-museum** — `kind:aggregator`: e-museum federates **407
  institutions, 2,477 takbon**. OpenAPI base `http://www.emuseum.go.kr/openapi/`
  (**serviceKey** from data.go.kr; list/detail param spec is in an unretrieved .docx —
  needed before harvesting). NMK's own ~658 + a colonial-era survey (~800 N-Korean +
  ~1,300 S-Korean rubbings — key witness to inaccessible NK epigraphy).
- **Jangseogak 장서각** (Academy of Korean Studies) — ~370 rubbings; kostma OpenAPI
  (`kostma.aks.ac.kr/OpenAPI/OpenAPI.aspx`), rubbing-specific coverage unconfirmed.

**`request` (no open API / web-only):**
- **Sungkyunkwan University Museum 성균관대학교** — **~1,000 takbon** (Cho Dong-won donation);
  request-only. (The biggest holding found.)
- **Seoul Calligraphy Museum 서울서예박물관** (Seoul Arts Center) — 74 pieces / 217 sheets
  (Ogawa Keikichi → Gana 2011), National-Treasure rank; web DB, no API.
- **Buddhist Central Museum 불교중앙박물관** (Jogye Order) — ~750+ new rubbings 2014–2023.
- **Dongguk University Museum 동국대학교** — Buddhist epigraphy; surfaces via e-museum.
- **Kyujanggak 규장각** (SNU) — mainly books; rubbings **not** a distinct collection (holds
  the compilation books 大東金石書 / 海東金石苑); web-only.
- **National Library of Korea 국립중앙도서관** — collects 금석문; APIs are bibliographic only.

No IIIF or OAI-PMH confirmed at any Korean institution. _Leads: SKKU & Buddhist Central
request-only; Kyung Hee Hyejeong holds an original-stone Gwanggaeto rubbing (single item)._

_US benchmarks for scale (not catalogued here as European): Field Museum >7,500 (Laufer);
UC Berkeley ~1,500 (harvested: 2,745 records). Source: parallel web research, June 2026._
