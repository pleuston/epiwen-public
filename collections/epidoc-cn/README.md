# epiwen-sample — linked TEI files for site / object / inscription

**Status: draft sample (Layer-5 sandbox), not for publication.** The citable demonstration set of
the Epiwen / EpiDoc-CN three-level model: **site → object/monument → inscription**, as mutually
linked TEI files, encoded I.Sicily-style, populated **only** with verbatim data from the
`sutras-data` catalog (nothing invented; gaps are absent + commented).

## The model in one paragraph

What we have is an **ontology** — places, the physical objects in them, the texts carved on the
objects, and the reproductions (rubbings…) that attest both — **pressed into the TEI/EpiDoc
framework**. Each level gets its own TEI file: the **site** is a `<place>` (CRM `E27`/`E53`),
the **object/monument** is a `<object>` (CRM `E22` made-object or `E25` feature; verified against
TEI P5: `<object>` legally contains `msContents`, `physDesc`, `history`, and nested `<object>`
parts), and the **inscription** is an EpiDoc `<msDesc>` + `<div type="edition">` whose
transcription is **delegated** to the upstream corpus via `<ptr>`. A derived CIDOC-CRM/CRMtex
graph is the export target (not built here); `@ana="crm:…"` on the nodes names each element's
CRM class via `<prefixDef>`.

## Division of the physical description (the core rule)

- **Object file** = the general, whole-monument description: overall dimensions, material,
  overall layout/format, monument condition, décor, **parts** (stele faces, cave walls) — and
  the texts it bears (`msContents`).
- **Inscription file** = the text-specific physical data (what the corpus's catalog records
  hold): **dimensions of the script field** (`<dimensions type="field" unit="cm">`), **hand
  description** (`handNote` with `letterHeight` ranges = 字徑, from the per-glyph arrays),
  per-text condition, columns/`ruledLines`, carving technique, orientation (azimuth).
- objectType + material are **thinly duplicated** on inscriptions (`@ana`/`@ref` + terms) so each
  edition is self-sufficient for EpiDoc aggregators; **the object file is the authority**.

## Uniform object policy (the fold rule, retired here)

**Every bearer gets an object file — including single-text surfaces.** The model's *fold rule*
(one surface : one text ⇒ the inscription record IS the object record, no separate file) is
conceptually cleaner, but the Epiwen app traverses **site → object → inscription uniformly**,
so the sample mints thin object nodes even where they are largely redundant (user decision,
2026-07-02): **SNS_1_object.xml** (extant moya) and **CLS_10_object.xml** (lost stone — the
stone-level lost-status + provenance live on the object; the per-record 佚失 condition and the
rubbing-derived field dimensions stay on the inscription). Division of description is unchanged;
for a 1:1 bearer the object file simply stays thin (objectType, material, décor, origin — no
duplicated field data). The fold remains a documented *model* option for contexts without the
uniform-traversal requirement.

## The four cases

| case | demonstrates |
|---|---|
| **SNS 水牛山** | mixed site: E22 stele (faces 碑陽 + two 碑側) + single-text moya (thin object SNS_1_object); one text across TWO faces (SNS_3, multi-target `@corresp`); whole-object condition from per-text records (base+head lost, ornate border); rubbing with its own colophons (SNS_2 witness E) |
| **CLS 徂徠山** | the full-site moya showcase, four bearers: ① 映佛巖 — four texts distributed over ONE boulder (anchor-less); ② 光化寺 boulder — four texts on ≥2 faces (az 216/107); ③ CLS_9 — LOST stone, object from the catalog's combined record, witness-primacy; ④ CLS_10 — lost single-text stone (thin object CLS_10_object) |
| **HDS 洪頂山** | shared-support panel: one E25 surface, sixteen texts, `idno[@type=support]` as sibling key; slope subsites by azimuth; the catalog's own `type="overview"` record ≡ our object file; object-level witnesses (incl. a rubbing correcting a rubbing: 千/十 in 9.14) |
| **WFY 臥佛院** | 4-tier chain site → Section A (nested place) → Cave 33 (object) → walls d/e/f (nested part-objects WITH dimensions) → inscriptions; the cross-wall Consecration as TWO catalog-faithful records joined `@next`/`@prev` |

## Linking mechanics (bidirectional)

| junction | down | up |
|---|---|---|
| site ⇄ object | `place/linkGrp[@type="objects"]/ptr[@type="object"]` (in the deepest subsite) | `object/history/origin/origPlace/placeName/@ref="…_site.xml#id"` |
| object ⇄ inscription | `msContents/msItem/@corresp="FILE.xml"` + `locus/@target="#faceId …"` | `msDesc/@corresp="OBJ.xml#faceId"` (space-separated multi-target for spans) + `idno[@type="support"]` |
| inscription → site | — | always ALSO human-readable `origPlace/@ref` (site or subsite) |
| sibling records | `@next`/`@prev` on `<text>` + shared support idno | — |
| out-links | edition `ab/ptr[@type="transcription"]` → `sutras:docs/<Site>/<id>.xml` · `handNote/ptr[@type="glyph-metrics"]` → CSV · `@ana="#x"` → `epiwen-taxonomies.xml` · `@ref` → Getty AAT · `altIdentifier[@type="sutras-data"]` → upstream record | — |

`@ana` bare fragments (`#condition.good`) resolve against **epiwen-taxonomies.xml** by
convention (link-checker enforced; a future ODD should formalise this). The `sutras:` prefix
resolves via `<prefixDef>`; upstream transcriptions verified to live in `docs/<Site>/` (the
catalog records are metadata-only).

## Conventions

- **Units**: every dimension `unit="cm"` (verified against the data: 42–66 cm 榜書 glyphs in a
  126×65 field; the 310×823 panel = 3.1 × 8.2 m).
- **Attested absence is data**: 無 is encoded, never omitted — `ruledLines="0"` (界格 checked
  and absent), `#decor.none`, `#frame.none`, `#polishing.unpolished`. Deliberate divergence from
  EpiDoc's omit-if-absent habit (ODD note).
- **Empty upstream = absent + comment**, never zero-filled and never invented (e.g. WFY field
  dims; CLS_9.x dims; `c:script` is empty corpus-wide → no `@script`/`@ana` asserted on hands).
- **Two-track split**: per-glyph metric arrays (char/col/row/h/w + engraving w/d + grade) are a
  **linked dataset**, not TEI — `SNS/SNS_1_glyphs.csv` (51 measured glyphs) is the demo, linked
  from `handNote/ptr[@type="glyph-metrics"]`. letterHeight `@atLeast/@atMost` = min/max of the
  array.
- **Witnesses (E-WIT)**: rubbings are first-class `<witness>` entries in `<listWit>` with their
  holding collections; they live **where the corpus records them** — per-text lists on the
  inscription (SNS_1 A–D, CLS_1 A–G…), ensemble/overview lists on the **object**
  (HDS_9, CLS_Guanghuasi). **Witness inheritance**: an object-level witness covers the texts it
  reproduces (a formal per-text `witness/@corresp` mechanism is future work). **Witness
  primacy for lost stones**: CLS_9/CLS_10's recorded dimensions are the RUBBINGS' sheet sizes.
  Witness types include the 1821 金石索 **woodcut reproduction** (`#witness.woodcut`, CLS_2/3/4)
  and a rubbing bearing its own dated colophons (SNS_2 E: 魏錫曾 1863, 陸恢 1905).
- **Bilingual throughout**: zh + en titles, terms, catDescs; every CJK character byte-exact
  (variants preserved: 况 in 保存狀况極佳; 横 vs 橫; 弥 in 弥勒佛; curly quotes in “V”形).
- **Naming**: inscription filenames + root `xml:id`s mirror the upstream catalog byte-for-byte
  (dots kept: `HDS_9.1.xml`; inconsistencies kept — see warts).

## Upstream warts (preserved verbatim, never silently repaired)

1. Id inconsistency: `WFY33_Consecration_11/12` (no underscore after WFY) vs `WFY_33_Diamond`;
   filename `WFY_33_d_e_Consecration.xml` has a wall-infix its own xml:id lacks.
2. SNS_1 witness D accession: zh 12496-1/-2 vs en 102496-1/-2.
3. SNS_2/SNS_3 witness B coverage: zh 水牛山2號和１號 vs en "SNS 2 and SNS 3".
4. SNS_2 `c:dimensions` carries attrs 235×179 (read: the 碑陽 field) AND element content
   "233/68/15.2" (read: whole-stele candidate — recorded uninterpreted on SNS_stele.xml).
5. SNS_1's title says 五十二字 (52 characters) but the upstream glyph array holds 51 entries.
6. CLS_3: zh mineral label empty (en "leucogranite"); witness C heights zh 86.5 vs en 141.5.
7. CLS_4 witness C: zh 90(h)×102(w) vs en 102(h)×90(w) — axes swapped.
8. CLS_9.2/9.3 `c:format`: 從長方形 (從 for 縱).
9. CLS_9.3: zh witness note empty (en only).
10. CLS_10 witness C: zh says 徂徠山8號 but en says "Rubbing of CLS 10".
11. CLS_10 technique: 未知 (unknown) — taxonomy category `execution.unknown`.
12. Coordinate axis order: TEI `<geo>` = lat lon; upstream strings are lon-lat — both kept
    (`note type="source-coordinates"`).

## Notable structural observations

- **The corpus already invented the object tier twice**: the catalog's `type="overview"` record
  `HDS_9.xml` and the combined record `CLS_9.xml` map 1:1 onto our object files — the model
  regularises an existing upstream practice rather than imposing a foreign one.
- **Boulder idioms**: face-anchored (SNS stele — nested identity-only `<object>` faces) vs
  anchor-less (映佛巖 / 光化寺 boulders — continuous or informally-faced surfaces; position is
  per-text via orientation notes). Choose anchors when texts must cite a *named* face (碑陽/碑側,
  cave walls); go anchor-less when the surface has no conventional part names.
- **Dates carried by colophons**: the whole CLS programme is dated 570 by the in-text dates of
  the colophons CLS_4 and CLS_8 (`c:given source="CLS_4, CLS_8"`; `evidence="internal-date"`).

## Ontology crosswalk (Epigraphy.info / EpiOnt)

site `<place>` → `E27/E53` (subsites `P89 falls within`) · object `<object>` → `E22`/`E25`
(nested parts `P46`) · object bears text → `epont:carriesText ⊑ crm:P56_bears_feature` →
`crmtex:TX1 Written Text` (the `<msDesc>` edition = `TX6 Transcription` → `epont:Edition`) ·
witnesses → separate `E22` objects linked by reproduction events. One deliberate divergence from
the WG model: **`E25 Human-Made Feature` for moya/cave-walls** (not `E84 Information Carrier`,
which suits only movable carriers) — the East-Asian extension this profile contributes.

## Validation status (V1–V9, run 2026-07-02)

- **V1 well-formedness: 30/30 XML files pass.**
- **V2 `tei_all.rng` (TEI P5 latest): 30/30 files VALID** — sites, objects, taxonomy AND
  inscriptions. The design's content-model rules held: nested `<object>`s LAST; no bare `<p>`
  mixed with `msContents`/`physDesc`; `msItem` links via `@corresp` (no `<ptr>` child);
  `physDesc` children in canonical order (objectDesc → handDesc → decoDesc).
- **V3 `tei-epidoc.rng` (EpiDoc latest): 7/19 inscription files pass outright; the 12 deltas
  are ONE single cause** — `<listWit>` as sibling of `<msDesc>` inside `<sourceDesc>` (our
  witness layer). Everything else feared proved EpiDoc-legal: `<term>` in
  `objectType`/`material`, `<ptr>` in `handNote`, `<rs>`/`<note>` in `layout`,
  `<idno type="segment|support">`, multi-target `@corresp`, `@next`/`@prev`. → **The future
  `epidoc-cn` ODD needs exactly one content-model extension: allow `listWit` in `sourceDesc`.**
  (Files without witnesses, or with witnesses held at the object level, pass EpiDoc unchanged.)
- **V4 link integrity: 395 pointer tokens resolve** (fragments, cross-file ids, taxonomy `@ana`,
  `sutras:` paths verified against the sister repo); **bidirectional pairs asserted**
  (object⇄inscription back-links, `@next`⇄`@prev`).
- **V5 value fidelity / V6 CJK byte fidelity / V7 `unit="cm"` audit / V8 bilingual audit /
  V9 CSV (51 data rows, letterHeight bounds 14–28 = array min/max): all pass.**

## File inventory (34 = 4 sites + 8 objects + 19 inscriptions + taxonomy + CSV + README)

```
README.md · epiwen-taxonomies.xml
SNS/  SNS_site.xml · SNS_stele.xml · SNS_1_object.xml
      · SNS_1.xml · SNS_2.xml · SNS_3.xml · SNS_1_glyphs.csv
CLS/  CLS_site.xml · CLS_Yingfoyan_object.xml · CLS_Guanghuasi_stone.xml
      · CLS_9_object.xml · CLS_10_object.xml
      · CLS_1.xml · CLS_2.xml · CLS_3.xml · CLS_4.xml · CLS_5.xml · CLS_6.xml · CLS_7.xml
      · CLS_8.xml · CLS_9.1.xml · CLS_9.2.xml · CLS_9.3.xml · CLS_10.xml
HDS/  HDS_site.xml · HDS_9_object.xml · HDS_9.1.xml
WFY/  WFY_site.xml · WFY_33_cave.xml · WFY_33_f_Diamond.xml
      · WFY_33_d_e_Consecration.xml · WFY_33_d_e_Consecration_12.xml
```
