# Rubbing-connector metadata schemes

Reference for **re-pulling full metadata per rubbing entry** on import and mapping
it to the Epiwen rubbing TEI. The bulk harvests in `../` capture a list-level
subset; on import we re-fetch the full record from the source using the
single-record endpoints documented here, then map fields to TEI.

| Connector | Doc | Aggregator | Harvested | Single-record endpoint |
|---|---|---|---|---|
| Harvard-Yenching (LibraryCloud) | [harvard-librarycloud.md](harvard-librarycloud.md) | no | 8,418 | `items.json?q=<HOLLIS>` |
| UC Berkeley (OAI) | [berkeley-oai.md](berkeley-oai.md) | no | 2,745 | `oai2d?verb=GetRecord&metadataPrefix=marcxml&identifier=oai:…:<id>` |
| Japan Search | [japan-search.md](japan-search.md) | **yes (43 sub-collections)** | 2,116 | `jps-cross` `common` block / original `linkUrl` |

## Not harvested (no clean API) — catalog-only / offline collections
Documented in `../collections.json` with `catalog_only:true` and a `catalog`
citekey (from the obsidian vault's bibliography). Print/PDF catalogs, no online
harvest; coordinates = holding institution. To ingest, map the printed catalog
manually (no connector).
- **Tōyō Bunko** 東洋文庫 — @Toyobunko2002 · Tokyo
- **Tōhoku University Library** 東北大學附属圖書館 — @Onoetal2013 · Sendai
- **Daitō Bunka Univ. (Uno Sesson Collection)** 宇野雪村文庫 — @Tamamura2004 · Tokyo
- **Shukutoku Univ. Center for Calligraphy** 淑德大學書學文化センター — @Shogakubunkasenta2016 · Saitama (also a digital archive)
- **Field Museum** — @Tchen_Starr1981 · Chicago
- **National Library of China** 北京圖書館藏…彙編 (101 vols) — @BJTSG1989 · Beijing
- **Peking University Library** — @Sunguanwen2020 / @Hu_Tang1998 · Beijing
- **Dalian Library** — @Dairentoshokan1925 · Dalian (historical, 1925)
- **Kyoto Univ. Institute for Research in Humanities** 人文科學研究所 — @Kyoto_zinbun_database · Kyoto
  (has an online database → a *future connector*, not yet harvested)
- **EFEO** estampages (efeo.fr) and **Indianapolis Museum of Art**: hand-added, no API.

## Mapping target (Epiwen rubbing TEI — common fields)
`title[@xml:lang=en]`, `title[@xml:lang=zh-Hant]`, `repository`, `country`,
`settlement`, `idno[@type=…]`, `summary`, `origDate`, `origPlace`,
`facsimile/graphic/@url`, `ref[@type=record]`, `ref[@type=iiif-manifest]`,
`ref[@type=provider]`, `availability/licence`. See `../collections.json` for the
per-collection catalogue (counts, original sites, coordinates).
