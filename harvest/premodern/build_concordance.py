# -*- coding: utf-8 -*-
"""Inscription concordance, two layers on the shared work-ids. READ-ONLY sources.

  curated layer : edep_sino jinshi.xml  → inscriptions.json (260 inscriptions, each with the
                  works that attest it + how they title it + juan + rubbing surrogates)
  broad layer   : skslxb-tei-md-dryrun  → toc/<work_id>.json (per-work 目錄, ~17.6k entries
                  across the deep-parsed catalogues), keyed to the works.xml work_id

Back-fills premodern.json with per-work `recorded_count` (curated attestations) and
`toc_count` / `toc_key` (broad 目錄). Run AFTER build_premodern.py.
"""
import json, os, re, glob, shutil
import xml.etree.ElementTree as ET
from collections import defaultdict

VAULT = "/Users/sassmann/repos/vaults/obsidian-vault"
DRY = VAULT + "/projects/AI responses/skslxb-tei-md-dryrun/entries"
EDEP = "/Users/sassmann/repos/edep_sino/data-pkg/data"
OUT = "/Users/sassmann/repos/GitHub/epiwen-public/harvest/premodern"
APP = "/Users/sassmann/repos/GitHub/epiwen"
CJK = "㐀-鿿豈-﫿"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
def norm(s): return re.sub("[^" + CJK + "]", "", s or "")
def L(el): return el.tag.split("}")[-1]
def xml_root(path):
    return ET.fromstring(re.sub(r'\sxmlns="[^"]*"', "", open(path, encoding="utf-8").read()))

# works.xml: title(norm) -> work_id, and work_id -> title
wroot = xml_root(EDEP + "/registers/works.xml")
wid_by_title = {}; title_by_wid = {}
for bibl in wroot.iter():
    if L(bibl) != "bibl" or bibl.get("type") != "work": continue
    tz = next((ch.text for ch in bibl if L(ch) == "title" and (ch.text or "").strip() and "Latn" not in (ch.get("lang") or "")), "")
    if tz: wid_by_title[norm(tz)] = bibl.get(XMLID); title_by_wid[bibl.get(XMLID)] = tz.strip()

# ── curated layer: jinshi.xml ────────────────────────────────────────────────
inscr = []; recorded = defaultdict(int)
for obj in xml_root(EDEP + "/registers/jinshi.xml").iter():
    if L(obj) != "object": continue
    iid = obj.get(XMLID); name_zh = name_py = ""; alt = []; origd = origp = ""
    atts = []; surr = []
    for el in obj.iter():
        t = L(el); typ = el.get("type")
        if t == "objectName":
            if typ == "main": name_zh = (el.text or "").strip()
            elif typ == "sort": name_py = (el.text or "").strip()
            elif typ == "alt": alt.append((el.text or "").strip())
        elif t == "origDate": origd = el.get("when") or (el.text or "").strip()
        elif t == "origPlace": origp = el.get("corresp") or (el.text or "").strip()
    attlist = next((e for e in obj.iter() if L(e) == "listBibl" and e.get("type") == "attestations"), None)
    if attlist is not None:
        for b in attlist:
            if L(b) != "bibl": continue
            wid = b.get("corresp") or ""
            tiw = next((g.text for g in b if L(g) == "title"), "")
            jr = next((g.get("unit") and (g.text or g.get("from") or "") for g in b if L(g) == "citedRange"), "")
            note = next((" ".join((g.text or "").split()) for g in b if L(g) == "note"), "")
            atts.append({"work_id": wid, "title_in_work": (tiw or "").strip(), "juan": (jr or "").strip(), "note": note})
            if wid: recorded[wid] += 1
    sgr = next((e for e in obj.iter() if L(e) == "surrogates"), None)
    if sgr is not None:
        for b in sgr:
            if L(b) != "bibl": continue
            ttl = next((g.text for g in b if L(g) == "title"), "")
            ref = next((g.get("target") for g in b if L(g) == "ref"), "")
            if ref: surr.append({"type": b.get("type") or "", "title": (ttl or "").strip(), "ref": ref})
    inscr.append({"id": iid, "name_zh": name_zh, "name_pinyin": name_py,
                  "alt": [a for a in alt if a and norm(a) != norm(name_zh)],
                  "origDate": origd, "origPlace": origp, "attestations": atts, "surrogates": surr})

inscr.sort(key=lambda x: (x.get("origDate") or "9999", x.get("name_pinyin") or ""))
os.makedirs(OUT, exist_ok=True)
json.dump({"generated": "2026-06-27", "count": len(inscr),
           "att_links": sum(len(i["attestations"]) for i in inscr),
           "source": "edep_sino jinshi.xml — curated inscription↔work attestation concordance",
           "inscriptions": inscr}, open(OUT + "/inscriptions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── broad layer: per-work 目錄 from skslxb-tei-md-dryrun ──────────────────────
tocdir = OUT + "/toc"
os.makedirs(tocdir, exist_ok=True)
for f in glob.glob(tocdir + "/*.json"): os.remove(f)
toc_count = {}  # work_id -> n
matched = unmatched = 0
for p in glob.glob(DRY + "/*TOC.json"):
    m = re.search(r"《?([^》/]+?)》?-目錄", os.path.basename(p))
    title = m.group(1) if m else os.path.basename(p)
    d = json.load(open(p, encoding="utf-8"))
    arr = d if isinstance(d, list) else (d.get("entries") or d.get("toc") or d.get("items") or [])
    wid = wid_by_title.get(norm(title))
    key = wid or ("t-" + norm(title))
    if wid: matched += 1
    else: unmatched += 1
    toc_count[key] = len(arr)
    json.dump({"work_id": wid, "title_zh": title_by_wid.get(wid, title), "count": len(arr),
               "entries": [{"seq": e.get("seq"), "title": e.get("title"), "attribution": e.get("attribution"),
                            "juan": e.get("juan"), "wyg": e.get("wyg"), "sbck": e.get("sbck")} for e in arr]},
              open(tocdir + "/" + key + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── back-fill premodern.json ─────────────────────────────────────────────────
pm = json.load(open(OUT + "/premodern.json", encoding="utf-8"))
for w in pm["works"]:
    wid = w.get("work_id")
    w["recorded_count"] = recorded.get(wid, 0) if wid else 0
    tk = wid if (wid and wid in toc_count) else ("t-" + norm(w["title_zh"]))
    if tk in toc_count: w["toc_count"] = toc_count[tk]; w["toc_key"] = tk
json.dump(pm, open(OUT + "/premodern.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# copy to app
shutil.copy(OUT + "/inscriptions.json", APP + "/inscriptions.json")
shutil.copy(OUT + "/premodern.json", APP + "/premodern.json")
appstoc = APP + "/toc"; os.makedirs(appstoc, exist_ok=True)
for f in glob.glob(appstoc + "/*.json"): os.remove(f)
for f in glob.glob(tocdir + "/*.json"): shutil.copy(f, appstoc + "/" + os.path.basename(f))

print("inscriptions:", len(inscr), "| attestation links:", sum(len(i["attestations"]) for i in inscr))
print("toc files:", matched + unmatched, "(matched work_id:", matched, "| unmatched:", unmatched, ")",
      "| total 目錄 entries:", sum(toc_count.values()))
print("works w/ recorded inscriptions:", sum(1 for w in pm["works"] if w.get("recorded_count")),
      "| works w/ 目錄:", sum(1 for w in pm["works"] if w.get("toc_count")))
