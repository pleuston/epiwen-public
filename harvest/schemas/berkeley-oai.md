# Connector: UC Berkeley Digital Collections (C.V. Starr East Asian Library)

- **Aggregator?** No — Berkeley is the holding institution and source.
- **Harvest scope:** OAI-PMH set `chineserubbings` → 2,745.
- **Protocol:** OAI-PMH at `https://digicoll.lib.berkeley.edu/oai2d`. Formats:
  `oai_dc` (romanized only), **`marcxml` (rich; 880 vernacular = CJK titles)**,
  `oai_openaire`. The harvest uses `oai_dc` for the base record + `marcxml` for the
  CJK title (merged). **Caveat:** the OAI endpoint 503s on sustained load — retry
  with backoff. Parse `<record>` with `Array.from(matchAll(...))` (iterators).

## Endpoints
- Page: `…/oai2d?verb=ListRecords&metadataPrefix=marcxml&set=chineserubbings` (+ `resumptionToken`)
- **Single full record:** `…/oai2d?verb=GetRecord&metadataPrefix=marcxml&identifier=oai:digicoll.lib.berkeley.edu:<id>`
- Record page: `https://digicoll.lib.berkeley.edu/record/<id>` (has CJK colophon transcriptions in the HTML)
- Images: `…/record/<id>/files/<file>.jpg` (from `oai_dc` `dc:identifier`)

## oai_dc → Epiwen
| dc field | meaning | Epiwen target |
|---|---|---|
| `dc:title` | romanized title | `title[@xml:lang=en]` |
| `dc:identifier` (record URL) | record page | `ref[@type=record]` |
| `dc:identifier` (`*.jpg`) | page images | `facsimile/graphic` |
| `dc:description` | scope/description | `summary` |
| `dc:subject` | subjects | keywords |
| `dc:type` | resource type | — |

## marcxml → Epiwen (richer; use for full re-pull)
| MARC tag $sub | meaning | Epiwen target |
|---|---|---|
| `245 $a$b` | title (romanized) | `title[@xml:lang=en]` |
| `880` linked to `245` ($6 `245-…`) | **vernacular title 石鼓文** | `title[@xml:lang=zh-Hant]` |
| `246 $a` | variant title (often CJK) | alt title |
| `260/264 $c` · `880` | date (e.g. 戰國秦 475–221 B.C.) | `origDate` |
| `300 $a` | extent (冊/頁/行/字, 高/寬 cm) | `physDesc` |
| `340 $a` | medium (石 stone) | `physDesc` |
| `500 $a` | general notes (provenance, script, 拓本 type) | `summary`/note |
| `520 $a` (EN + a CJK colophon note) | description / colophon | `summary` |
| `541` | acquisition / origin (出土, 今存…) | `provenance` |
| `561` / `563` | ownership, binding | note |
| `655 $a` · `880` | genre/binding (剪裱旋風裝) | `objectType`/note |
| `650 $a` | subjects | keywords |
| OAI `<header><identifier>` `…:<id>` | record id | `idno[@type=record]` |

Filename scheme on import: `<slug>_rubbing_UCB<id>.xml`.
