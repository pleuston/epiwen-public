#!/usr/bin/env python3
"""build_index.py — rebuild a collection's authority-index.json FROM its XML.

    python3 harvest/places/build_index.py --all          # every derivable collection
    python3 harvest/places/build_index.py epidoc-cn      # one, by name

⚠️  ONLY collections listed in DERIVABLE below are rebuilt. A collection whose
    index carries curated fields its XML does NOT hold must never be rebuilt
    from XML — doing so silently deletes them. Measured: rebuilding `rubbings`
    would drop 22 fields (name_pinyin, wikidata ids on harvard_yenching,
    ihp_rubbings, ucb_eal, efeo, …). Add a collection here only once its XML
    carries everything its index needs.

The XML records under collections/<pkg>/authority/ are the single source of
truth; this derives the browser index from them. Run it after ANY change to a
record — an in-app edit, a hand-edit, or a bulk import — and the Places table
picks the change up. The GitHub Action in .github/workflows/authority-index.yml
runs it automatically on push.

(Contrast build_places.py, which SEEDED the place records from a hardcoded
table. Do not re-run that: it would overwrite edits. This script never touches
the XML.)

Derives, per record:
  id            <mads ID>
  name_zh       <authority><geographic>            (or <name><namePart> …)
  name_pinyin   <variant transliteration=…><geographic>
  en            <variant lang="en"><geographic>
  display_name  "<en> <zh>" — the same rule build_places.py used
  name_type     geographic | corporate | personal
  place_type / province / coordinates / date  from <note type="…">
  wikidata/viaf/gnd/dila_authority/cbdb        from <identifier type="…">
  province_en   mapped;  site_id  when the id is a known site
"""

import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

NS = "{http://www.loc.gov/mads/}"
# Collections whose authority-index.json is fully derivable from their XML.
# See the warning in the module docstring before adding one.
DERIVABLE = {"epidoc-cn"}
PROV_EN = {"山東省": "Shandong Province", "河南省": "Henan Province",
           "四川省": "Sichuan Province"}
SITE_IDS = {"SNS", "CLS", "HDS", "WFY", "LQS", "XNH"}


def text(el):
    return (el.text or "").strip() if el is not None else ""


def parse_record(path):
    root = ET.parse(path).getroot()
    rec = {
        "id": root.get("ID") or os.path.splitext(os.path.basename(path))[0],
        "display_name": "", "name_zh": "", "name_pinyin": "", "name_type": "personal",
        "place_type": "", "province": "", "province_en": "", "coordinates": "", "date": "",
        "wikidata": "", "viaf": "", "gnd": "", "dila_authority": "", "cbdb": "",
    }
    en = ""

    auth = root.find(NS + "authority")
    if auth is not None:
        geo = auth.find(NS + "geographic")
        if geo is not None:
            rec["name_type"] = "geographic"
            rec["name_zh"] = text(geo)
        else:
            nm = auth.find(NS + "name")
            if nm is not None:
                rec["name_type"] = nm.get("type") or "personal"
                parts = [text(p) for p in nm.findall(NS + "namePart") if text(p)]
                rec["name_zh"] = " ".join(parts)

    for var in root.findall(NS + "variant"):
        vgeo = var.find(NS + "geographic")
        val = text(vgeo) if vgeo is not None else ""
        if not val:
            nm = var.find(NS + "name")
            if nm is not None:
                val = " ".join(text(p) for p in nm.findall(NS + "namePart") if text(p))
        if not val:
            continue
        if var.get("transliteration"):
            rec["name_pinyin"] = rec["name_pinyin"] or val
        elif var.get("lang") == "en":
            en = en or val

    for note in root.findall(NS + "note"):
        t = note.get("type") or ""
        v = text(note)
        if t == "place-type":    rec["place_type"] = v
        elif t == "province":    rec["province"] = v
        elif t == "coordinates": rec["coordinates"] = v
        elif t == "attested":    rec["date"] = v

    for ident in root.findall(NS + "identifier"):
        t = ident.get("type") or ""
        v = text(ident)
        if t == "dila":
            rec["dila_authority"] = v
        elif t in ("wikidata", "viaf", "gnd", "cbdb"):
            rec[t] = v

    rec["display_name"] = ("%s %s" % (en, rec["name_zh"])).strip() if en else rec["name_zh"]
    rec["province_en"] = PROV_EN.get(rec["province"], "")
    if rec["id"] in SITE_IDS:
        rec["site_id"] = rec["id"]
    return rec


def build(pkg):
    src = "collections/%s/authority" % pkg
    out = "collections/%s/authority-index.json" % pkg
    if not os.path.isdir(src):
        print("skip %s — no %s/" % (pkg, src))
        return 0
    records, bad = [], []
    for path in sorted(glob.glob(src + "/*.xml")):
        try:
            records.append(parse_record(path))
        except ET.ParseError as e:
            bad.append("%s: %s" % (os.path.basename(path), e))
    if bad:
        # Never write a half-built index from malformed input.
        print("ERROR: %d unparseable record(s) in %s:" % (len(bad), src))
        for b in bad:
            print("   ", b)
        raise SystemExit(1)

    records.sort(key=lambda e: (e["province"] or "￿", e["place_type"], e["id"]))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    from collections import Counter
    print("%s → %d records  types=%s" %
          (out, len(records), dict(Counter(r["name_type"] for r in records))))
    return len(records)


if __name__ == "__main__":
    if not os.path.isdir("collections"):
        raise SystemExit("run from the epiwen-data-public repo root")
    args = sys.argv[1:]
    if not args or "--all" in args:
        # Discover here rather than in the shell — passing a newline-separated
        # list through an unquoted variable word-splits differently per shell
        # and silently rebuilt nothing when it went wrong.
        pkgs = sorted(p for p in DERIVABLE
                      if os.path.isdir("collections/%s/authority" % p))
    else:
        pkgs = args
        refused = [p for p in pkgs if p not in DERIVABLE]
        if refused:
            raise SystemExit(
                "refusing to rebuild %s — not in DERIVABLE. Its index may hold "
                "curated fields the XML does not carry, which a rebuild would "
                "delete. See the note at the top of this file." % ", ".join(refused))
    if not pkgs:
        print("nothing to rebuild")
    for pkg in pkgs:
        build(pkg)
