# Harvest status — all collections

Final state of harvesting the collections in `collections.json`. **Harvested** = a
staging JSON exists in this folder. **Blocked** = cannot be pulled from this
environment, with the reason. Counts are records in the staging file.

_Last updated 2026-06-26._

## ✅ Harvested (staging files here)

| Source | File | Records | API |
|---|---|--:|---|
| Harvard-Yenching | `harvard-rubbings.json` | 8,418 | LibraryCloud MODS-JSON |
| UC Berkeley (C.V. Starr) | `berkeley-rubbings.json` | 2,745 | OAI-PMH (oai_dc + MARCXML 880) |
| Japan Search (ColBase 947, NDL, Daitō, NIJL, Minpaku, U-Tokyo, ARC, +union) | `japansearch-rubbings.json` | 2,116 | jps-cross API, per `f-db` |
| **NRICH — Korean epigraphy** 한국금석문 | `nrich-inscriptions.json` | **6,557** | keyless XML; range pagination `firstindex`=start … `recordcountperpage`=END |
| **Shanghai Library — 古代碑帖知識庫** | `shanghai-library-beitie.json` | **45** | `names.library.sh.cn/whzk/beitie/search` (BIBFRAME/JSON-LD); the LOD knowledge-base exemplars (not the ~100k physical holdings) |

**Total staged: ~19,881 records** across 5 sources.

## ⛔ Blocked — cannot harvest from here

| Collection | API | Blocker |
|---|---|---|
| **National Library of China** (NLC) | guji.nlc.cn REST | **Geo-blocked** outside China (connection refused). On-site / in-China access only. |
| **e-museum** (National Museum of Korea) | data.go.kr OpenAPI | Needs a **data.go.kr serviceKey** (free, but registration required). Would unlock 탁본 across 400+ Korean institutions. |
| **Korean Ancient Epigraphy** (NIKH) | data.go.kr bulk XML (15053630) | Needs a **data.go.kr account/key**. |
| **Academia Sinica IHP** 傅斯年圖書館 | IHPKMC | **Member-gated** (full 釋文 behind login; session-token URLs). Active data-sharing outreach target — not openly harvestable. |
| **Jangseogak** (Academy of Korean Studies) | kostma OpenAPI | API exists but **rubbing (탁본) coverage unconfirmed** — the OpenAPI emphasises 고문서/고지도; the 370 rubbings may be browse-only. |

## 🟡 Reachable but deferred (no clean API — bulk HTML/AJAX scrape)

| Collection | Records | Why deferred |
|---|--:|---|
| **NCL Taipei — 金石拓片** (rbook.ncl.edu.tw) | **6,498** | No CSV/JSON/OAI/IIIF list endpoint (ExportCSV 404s). The results grid loads via AJAX (`swhgLoad`/DataGrid); each record is a `SearchDetail?item=<32hex>` link. Harvesting needs a **session-based scrape of ~650 result pages + ~6,498 detail fetches** — heavy on a government server and fragile. Reproducible recipe below. |

**NCL session recipe** (for a future dedicated scraper):
1. `GET /NCLSearch/Search/Index/5` with a cookie jar → extract `__RequestVerificationToken`.
2. `POST /NCLSearch/Search/SearchResult/5` with that token + cookies (sets the session query) → 302.
3. `GET /NCLSearch/Search/SearchResult/5?SourceID=5` (and `/SearchResult/Page/N` for pages) with the session cookie → results HTML containing `SearchDetail?item=<id>` links.
4. `GET /NCLSearch/Search/SearchDetail?item=<id>` per record for full metadata.

## ℹ️ Not applicable (no API by nature)

All `connector: none` collections marked **catalog-only**, **needs-request**,
**subscription**, or **verification-pending** in `collections.json` (e.g. Palace
Museum Beijing, PKU, Xi'an Stele Forest, NPM Taipei, the European EFEO-union members,
the offline Japanese catalogue collections, 中國金石總録) have **no machine API** and
are linked for discovery only — nothing to harvest.

## Next steps
- Provide a **data.go.kr serviceKey** → harvest e-museum + Korean Ancient Epigraphy.
- A dedicated **NCL scraper** (recipe above) → 6,498 金石拓片 records.
- Enrich Shanghai Library per-record via `/whzk/beitie/info?id=<@id>` (IIIF + character OCR).
- In-China collaborator → NLC (guji.nlc.cn), and the on-site-only mainland holders.
