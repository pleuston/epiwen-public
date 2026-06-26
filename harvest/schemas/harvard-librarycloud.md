# Connector: Harvard LibraryCloud (Harvard-Yenching rubbings)

Metadata scheme for the Harvard rubbing connector — for re-pulling full metadata
per entry on import and mapping it to the Epiwen rubbing TEI.

- **Aggregator?** No — Harvard is the holding institution and the source.
- **Harvest scope:** `genre=rubbings&repository=Harvard-Yenching Library` → 8,418.
- **Format:** MODS, served as JSON by LibraryCloud (`items.json`). No raw-MODS/MARC
  endpoint (`items.mods` 404s), so the MARC `880` vernacular is **only present for
  ~2,638 records** that carry a vernacular `titleInfo`; the rest are romanized-only.

## Endpoints
- Search/page: `https://api.lib.harvard.edu/v2/items.json?genre=rubbings&repository=Harvard-Yenching%20Library&limit=250&start=<n>`
- **Single full record:** `https://api.lib.harvard.edu/v2/items.json?q=<HOLLIS>` (e.g. `q=9707474`)
- IIIF manifest: `https://iiif.lib.harvard.edu/manifests/drs:<drsObjectId>`
- Image (IIP): `https://mps.lib.harvard.edu/assets/images/drs:<drsFileId>/full/,1000/0/default.jpg`

## Fields (MODS-JSON path → meaning → Epiwen TEI target)
| MODS-JSON path | meaning | Epiwen target |
|---|---|---|
| `titleInfo[].title` (`@type` absent) | romanized title | `title[@xml:lang=en]` |
| `titleInfo[]` containing CJK | vernacular title (when present) | `title[@xml:lang=zh-Hant]` |
| `titleInfo[@type=alternative].title` | variant titles | — / note |
| `name[].namePart` (+ `role`) | creators / calligraphers | `respStmt` / `author` (not yet mapped) |
| `originInfo.dateIssued` / `dateCreated` | date | `origDate` |
| `originInfo.place.placeTerm[@type=text]` | place of publication | (often modern) |
| `physicalDescription.extent` / `form` | extent, format | `physDesc/objectDesc` |
| `abstract` | summary / scope note | `summary` |
| `note[]` | cataloguer notes | `summary` / `note` |
| `location.physicalLocation[@type=repository]` | holding repository | `repository` |
| `location.shelfLocator` | call number | `idno[@type=shelf]` |
| `identifier[@type=oclc]` etc. | identifiers | `idno` |
| `recordInfo.recordIdentifier` | VIA id incl. `URN-3:FHCL:<n>` | `idno[@type=fhcl]` |
| `extension[].cultureWrap.culture` | culture (e.g. Chinese) | filter only |
| `extension[].styleWrap.style` | dynasty/style | dating hint |
| `extension[].DRSMetadata.drsObjectId` | DRS object → IIIF manifest | `ref[@type=iiif-manifest]` |
| `extension[].DRSMetadata.drsFileId` | DRS file → image | `facsimile/graphic/@url` |
| `extension[].DRSMetadata.accessFlag` | P=public / R=restricted | licence / skip-on-import |
| `relatedItem[@type=constituent]` | per-page image constituents | (IIIF covers) |

HOLLIS id: extract from any `id.lib.harvard.edu/aleph/<HOLLIS>/catalog` URL or the
`curiosity/chinese-rubbings-collection/<n>-<HOLLIS>` link.
