# Connector: Japan Search (aggregator → Japanese institutions)

- **Aggregator?** YES. Japan Search (国立国会図書館) federates ~100 Japanese
  databases. Our harvest (`keyword=拓本 中国`) spans **43 source collections**.
- **Harvest scope:** harvested per source collection via facet `f-db=<code>`
  (the API caps `from` at 2,000) + a global union → **2,116 of 2,117**.
- **Format:** `jps-cross` JSON. Every item has a normalized **`common`** block
  (what we harvest) plus raw per-source fields keyed `<db>-<n>-<type>` (e.g.
  `cobas-17-h`). For a full re-pull, the `common` block is uniform across all
  sub-collections; the *original* record (via `record_url`) varies per source.

## Endpoints
- Search: `https://jpsearch.go.jp/api/item/search/jps-cross?keyword=拓本%20中国&size=100&from=<n>&f-db=<code>`
- **Single item:** same search with a narrowing keyword, or resolve `record_url` (the original).
- Facets: `…&size=0` → `facets[].key` (`db`, `rights`, `contents`, `type`, `cm`, `tempo`).

## `common` → Epiwen
| common field | meaning | Epiwen target |
|---|---|---|
| `title` | title (usually CJK) | `title[@xml:lang=zh-Hant]` |
| `titleEn` | English title | `title[@xml:lang=en]` |
| `description` (HTML) | scope note | `summary` |
| `contributor[]` (donor + institution, JP+EN) | holding institution + donor | `repository` |
| `database` / `provider` / `ownerOrg` | **source collection code** | collection / `idno` |
| `temporal[]` (JP+EN) | date (original + rubbing date) | `origDate` |
| `location[]` (JP+EN) | original stele location (e.g. 中国・吉林省) | `origPlace` |
| `coordinates {lat,lon}` | original-site coords (when present) | map / `geo` |
| `linkUrl` | **original record** | `ref[@type=record]` |
| `contentsUrl[]` / `thumbnailUrl[]` | image(s) | `facsimile/graphic` |
| `contentsRightsType` (ccby, pdm, incr…) | rights | `availability/licence` |
| `access` (PUBLIC/…) | access | skip-on-import if not PUBLIC |
| `id` (`<db>-<n>`) | Japan Search id | `idno[@type=jps]` |

**Provenance rule:** import records as *"Harvested via Japan Search (collection …)"*
and cite `linkUrl` as the original record; where the original is HTML-only/not
independently resolvable, mark Japan Search as the access path.

## Sub-collections (source `db` → count · original site · native re-pull)
| db | n | original site | native full-record |
|---|---|---|---|
| `cobas` | 947 | colbase.nich.go.jp (ColBase · Nat'l Museums of Japan) | **HTML SPA, no JSON API** → use Japan Search `common` |
| `dignl` | 451 | dl.ndl.go.jp (NDL Digital) | **IIIF manifest** `https://dl.ndl.go.jp/api/iiif/<pid>/manifest.json`; SRU `recordSchema=dcndl` |
| `daito` | 212 | i-repository.net (Daitō Bunka Univ.) | DSpace/JAIRO OAI |
| `nmj01`/`nmj02` | 120 | nihu.jp (Nat'l Inst. Japanese Literature / NIHU) | NIHU APIs |
| `nme_*` | ~105 | minpaku.ac.jp (Nat'l Museum of Ethnology, Osaka) | OPAC |
| `utokyo_da` | 73 | da.dl.itc.u-tokyo.ac.jp (Univ. of Tokyo Digital Archive) | IIIF |
| `arc_*` | ~90 | dh-jac.net (ARC, Ritsumeikan Univ.) | ARC API |
| `bibnl` | 43 | ndlsearch.ndl.go.jp (NDL Search) | SRU dcndl |
| (others, ≤8 each) | — | various (adeac.jp, jmapps.ne.jp, narahaku.go.jp, …) | per-source |

Filename scheme on import: `<slug>_rubbing_JPS<alnum(id)>.xml`.
