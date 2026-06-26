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

## Not harvested (no clean API)
- **EFEO** (École française d'Extrême-Orient — estampages union catalogue): no
  public machine API located. 1 record was hand-added. Needs a contact / manual
  export. Original site: efeo.fr.
- **Indianapolis Museum of Art (Newfields)** and other one-off holdings: hand-added.

## Mapping target (Epiwen rubbing TEI — common fields)
`title[@xml:lang=en]`, `title[@xml:lang=zh-Hant]`, `repository`, `country`,
`settlement`, `idno[@type=…]`, `summary`, `origDate`, `origPlace`,
`facsimile/graphic/@url`, `ref[@type=record]`, `ref[@type=iiif-manifest]`,
`ref[@type=provider]`, `availability/licence`. See `../collections.json` for the
per-collection catalogue (counts, original sites, coordinates).
