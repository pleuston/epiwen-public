# -*- coding: utf-8 -*-
"""Premodern Sources register + epigrapher persons. READ-ONLY on the vault & edep_sino.

Spine: the K&S / SKSLXB register (clean CJK titles from ks-concordance.json + the *verified*
SKSLXB locators from entries.json, joined by per-K&S-page alignment) plus the broader vault
epigraphy work pages — same as before. Then **merged with the curated edep_sino works.xml**
(work_id, author→person link, structured editions, work-to-work relations) by Chinese title.
Also builds the **epigrapher person register** from edep_sino persons.xml + people/*.xml, with
each person's authored works derived from the merge. No paratexts.

Outputs (epiwen-public/harvest/premodern/ + copied to epiwen/):
  premodern.json   — the work register (now carrying work_id, author_id, editions, relations)
  persons.json     — epigrapher / person register, with works-authored
  skslxb-toc.json  — SKSLXB contents by series (輯)
(build_concordance.py adds inscriptions.json + toc/<work_id>.json and back-fills counts.)
"""
import json, os, re, glob, shutil
import xml.etree.ElementTree as ET
from collections import defaultdict

VAULT = "/Users/sassmann/repos/vaults/obsidian-vault"
KS = VAULT + "/projects/AI responses/kuhn-stahl-dryrun"
WORKPAGES = VAULT + "/knowledge base/Texts/Epigraphy 金石學"
EDEP = "/Users/sassmann/repos/edep_sino/data-pkg/data"
OUT = "/Users/sassmann/repos/GitHub/epiwen-public/harvest/premodern"
APP = "/Users/sassmann/repos/GitHub/epiwen"
CJK = "㐀-鿿豈-﫿"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"

def norm(s): return re.sub("[^" + CJK + "]", "", s or "")
def cjk_run(s):
    m = re.search("[" + CJK + "]{2,}", s or ""); return m.group(0) if m else ""
def slug(s, pre):
    return pre + "-" + (re.sub(r"[^0-9a-z]+", "-", (s or "").lower()).strip("-") or "x")
def dyn(y):
    if y is None: return ""
    return ("Han 漢" if y < 220 else "Six Dyn. 魏晉南北朝" if y < 589 else "Sui–Tang 隋唐" if y < 907
            else "Song 宋" if y < 1279 else "Yuan 元" if y < 1368 else "Ming 明" if y < 1644
            else "Qing 清" if y < 1912 else "modern 近現代")
def birth(s):
    m = re.search(r"(\d{3,4})\s*[-–]", s or ""); return int(m.group(1)) if m else None
def parse_wp(fn):
    base = re.sub(r"\.md$", "", fn); tm = re.search(r"《([^》]+)》", base)
    title = tm.group(1) if tm else base; head = base[:tm.start()] if tm else ""
    pin = re.match(r"^([A-Za-z .'-]+)", head or "")
    return title, cjk_run(head), (pin.group(1).strip() if pin else "")
def xml_root(path):
    txt = re.sub(r'\sxmlns="[^"]*"', "", open(path, encoding="utf-8").read())
    return ET.fromstring(txt)
def L(el): return el.tag.split("}")[-1]

# ── 1) K&S + vault spine (unchanged) ─────────────────────────────────────────
entries = json.load(open(KS + "/entries.json", encoding="utf-8"))
ent_by_page = defaultdict(list)
for e in entries: ent_by_page[e.get("pdf_page")].append(e)
conc = json.load(open(KS + "/ks-concordance.json", encoding="utf-8"))
conc_by_page = defaultdict(list)
for c in conc: conc_by_page[c.get("page")].append(c)

reg = []; seen = set()
for page, clist in conc_by_page.items():
    elist = ent_by_page.get(page, [])
    for k, c in enumerate(clist):
        e = elist[k] if k < len(elist) and len(elist) == len(clist) else None
        title = (c.get("title") or "").strip()
        if not norm(title): continue
        seen.add(norm(title))
        author_zh = author_py = vault_page = ""
        if c.get("match"):
            vault_page = c["match"]; _, author_zh, author_py = parse_wp(c["match"])
        loc = e.get("locator") if e else ""
        yr = birth(e.get("author_dates")) if e else None
        reg.append({
            "id": slug(loc, "ks") if loc else slug(c.get("title"), "ks-t") + "-" + str(page),
            "title_zh": title, "title_pinyin": "", "author_zh": author_zh, "author_pinyin": author_py,
            "author_id": "", "work_id": "", "dynasty": dyn(yr), "juan": (e.get("juan") if e else None),
            "in_skslxb": True, "skslxb_series": (e.get("series") if e else c.get("series")),
            "skslxb_locator": loc,
            "skslxb_pages": (str(e.get("page_start")) + "-" + str(e.get("page_end")) if e and e.get("page_start") else ""),
            "period_covered": (e.get("period_covered") if e else None),
            "author_dates": (e.get("author_dates") if e else None),
            "transcriptions": (e.get("transcriptions") if e else None),
            "has_epitaphs": (e.get("has_epitaphs") if e else None),
            "catalogue": {k2: v for k2, v in ((e.get("catalogue") if e else {}) or {}).items() if v not in (None, "", False)},
            "editions": [], "relations": [],
            "ks_page": page, "ks_date": c.get("date"), "vault_page": vault_page,
            "source": "Kuhn & Stahl 1991 / 石刻史料新編",
        })
extra = 0
for p in sorted(glob.glob(WORKPAGES + "/*《*》*.md")):
    title, author_zh, author_py = parse_wp(os.path.basename(p))
    if not norm(title) or norm(title) in seen: continue
    seen.add(norm(title)); extra += 1
    reg.append({"id": slug(author_py, "wp") + "-" + str(extra), "title_zh": title, "title_pinyin": "",
                "author_zh": author_zh, "author_pinyin": author_py, "author_id": "", "work_id": "",
                "dynasty": "", "juan": None, "in_skslxb": False, "skslxb_series": None, "skslxb_locator": "",
                "catalogue": {}, "editions": [], "relations": [],
                "vault_page": os.path.basename(p)[:-3], "source": "vault epigraphy work page"})

# ── 2) merge curated edep_sino works.xml by Chinese title ─────────────────────
works_root = xml_root(EDEP + "/registers/works.xml")
wx_by_title = {}; wx_title_by_id = {}
for bibl in works_root.iter():
    if L(bibl) != "bibl" or bibl.get("type") != "work": continue
    wid = bibl.get(XMLID)
    tz = tp = ""; author_zh = author_id = ""; juan = None; compiled = None
    editions = []; relations = []
    for ch in bibl:
        t = L(ch)
        if t == "title":
            if ch.get("{http://www.w3.org/XML/1998/namespace}lang") == "zh-Latn-x-pinyin" or (ch.get("lang") == "zh-Latn-x-pinyin"):
                tp = (ch.text or "").strip()
            elif not tz:
                tz = (ch.text or "").strip()
        elif t == "author":
            pn = ch.find(".//persName") if ch.find("persName") is None else ch.find("persName")
            pn = next((g for g in ch.iter() if L(g) == "persName"), None)
            if pn is not None:
                author_zh = (pn.text or "").strip(); author_id = pn.get("corresp") or ""
        elif t == "date" and ch.get("type") == "compiled":
            compiled = {"text": (ch.text or "").strip(), "when": ch.get("when"), "cert": ch.get("cert")}
        elif t == "extent" and ch.get("unit") == "juan":
            try: juan = int((ch.text or "").strip())
            except: pass
        elif t == "bibl" and ch.get("type") == "edition":
            ed = {"edition": "", "date": "", "publisher": "", "in_collection": ""}
            for g in ch:
                gt = L(g)
                if gt == "edition": ed["edition"] = (g.text or "").strip()
                elif gt == "date": ed["date"] = g.get("when") or (g.text or "").strip()
                elif gt == "publisher": ed["publisher"] = (g.text or "").strip()
                elif gt == "note" and g.get("type") == "in-collection": ed["in_collection"] = (g.text or "").strip()
            editions.append(ed)
        elif t == "relatedItem":
            relations.append({"type": ch.get("type"), "target": ch.get("target")})
    if not norm(tz): continue
    wx_title_by_id[wid] = tz
    wx_by_title[norm(tz)] = {"work_id": wid, "title_pinyin": tp, "author_zh": author_zh,
                             "author_id": author_id, "juan": juan, "compiled": compiled,
                             "editions": editions, "relations": relations}

merged = 0
for w in reg:
    wx = wx_by_title.get(norm(w["title_zh"]))
    if not wx: continue
    merged += 1
    w["work_id"] = wx["work_id"]
    if wx["title_pinyin"]: w["title_pinyin"] = wx["title_pinyin"]
    if wx["author_zh"]: w["author_zh"] = wx["author_zh"]
    if wx["author_id"]: w["author_id"] = wx["author_id"]
    if wx["juan"] and not w.get("juan"): w["juan"] = wx["juan"]
    if wx["compiled"]: w["compiled"] = wx["compiled"]
    w["editions"] = wx["editions"]
    w["relations"] = wx["relations"]

# resolve relation targets to titles for display
for w in reg:
    for r in w.get("relations", []):
        r["target_title"] = wx_title_by_id.get(r.get("target"), "")

reg.sort(key=lambda w: (0 if w["in_skslxb"] else 1, w.get("skslxb_series") or 9, w["title_zh"]))

# ── 3) epigrapher / person register (persons.xml + people/*.xml) ──────────────
persons = {}
def add_person(pid, fields):
    cur = persons.setdefault(pid, {"id": pid})
    for k, v in fields.items():
        if v in (None, "", [], {}): continue
        if isinstance(v, list): cur.setdefault(k, []); cur[k] = sorted(set(cur[k] + v), key=v.index if False else None) if False else list(dict.fromkeys(cur.get(k, []) + v))
        else: cur.setdefault(k, v)  # first non-empty wins; people/*.xml loaded last as fallback

def parse_person(el):
    pid = el.get(XMLID)
    name_zh = name_py = sort = bio = ""; zi = []; hao = []; other = []; b = d = fl = None; offices = []
    for ch in el.iter():
        t = L(ch); typ = ch.get("type"); lang = ch.get("lang") or ch.get("{http://www.w3.org/XML/1998/namespace}lang")
        if t == "persName":
            if typ in ("canonical", "main") and not name_zh: name_zh = "".join(ch.itertext()).strip()
            elif (lang and "Latn" in lang) or typ == "pinyin": name_py = name_py or (ch.text or "").strip()
            elif typ == "sort": sort = (ch.text or "").strip()
        elif t == "addName" and typ == "zi": zi.append((ch.text or "").strip())
        elif t == "addName" and typ == "hao": hao.append((ch.text or "").strip())
        elif t == "addName" and typ: other.append({"type": typ, "name": (ch.text or "").strip()})
        elif t == "birth": b = {"when": ch.get("when"), "text": (ch.text or "").strip()}
        elif t == "death": d = {"when": ch.get("when"), "text": (ch.text or "").strip()}
        elif t == "floruit": fl = {"notBefore": ch.get("notBefore"), "notAfter": ch.get("notAfter"), "text": (ch.text or "").strip()}
        elif t == "persState" and typ == "office":
            lab = next((g for g in ch.iter() if L(g) == "label"), None)
            offices.append((lab.text if lab is not None else (ch.text or "")).strip())
        elif t == "note" and typ == "bio": bio = " ".join((ch.text or "").split())
    yr = int(b["when"]) if b and b.get("when") and b["when"].lstrip("-").isdigit() else None
    return pid, {"name_zh": name_zh, "name_pinyin": name_py or sort, "sort": sort or name_py,
                 "zi": zi, "hao": hao, "other_names": other, "birth": b, "death": d, "floruit": fl,
                 "offices": offices, "bio": bio, "dynasty": dyn(yr), "role": el.get("role") or ""}

for el in xml_root(EDEP + "/registers/persons.xml").iter():
    if L(el) == "person" and el.get(XMLID):
        pid, f = parse_person(el); add_person(pid, f)
for pf in glob.glob("/Users/sassmann/repos/edep_sino/data-pkg/data/people/*.xml"):
    el = xml_root(pf)
    if L(el) == "person" and el.get(XMLID):
        pid, f = parse_person(el); add_person(pid, f)

# works-authored per person: explicit author@corresp link OR exact author-name-token match
# (recovers epigraphers whose works.xml author wasn't corresp-linked; exact tokens avoid the
# substring false matches that "王素" in "王素芳" would cause).
name_pids = {}
for pid, p in persons.items():
    if p.get("name_zh"): name_pids.setdefault(p["name_zh"], []).append(pid)
def author_tokens(az):
    return set(t for t in re.split(r"[、,，;；/／·\s()（）]+", az or "") if re.search("[" + CJK + "]", t))
works_by_person = defaultdict(list)
for w in reg:
    pids = set()
    if w.get("author_id"): pids.add(w["author_id"])
    for tok in author_tokens(w.get("author_zh")):
        for pid in name_pids.get(tok, []): pids.add(pid)
    rec = {"id": w["id"], "title_zh": w["title_zh"], "year": (w.get("compiled") or {}).get("when") or "", "skslxb": w["in_skslxb"]}
    for pid in pids: works_by_person[pid].append(rec)
for pid, p in persons.items():
    ws = sorted(works_by_person.get(pid, []), key=lambda x: (x["year"] or "9999"))
    p["works"] = ws; p["work_count"] = len(ws)

# EPIGRAPHERS ONLY: a person belongs here iff they authored >=1 work in the register.
# persons.xml is a general authority (monks, officials, calligraphers, inscription subjects) —
# those non-authors are excluded.
plist = [p for p in persons.values() if p.get("name_zh") and p.get("work_count", 0) >= 1]
def pyear(p): return int(p["birth"]["when"]) if p.get("birth") and (p["birth"].get("when") or "").lstrip("-").isdigit() else 99999
plist.sort(key=lambda p: (pyear(p), p.get("sort") or ""))

os.makedirs(OUT, exist_ok=True)
json.dump({"generated": "2026-06-27", "count": len(reg), "in_skslxb": sum(1 for w in reg if w["in_skslxb"]),
           "with_locator": sum(1 for w in reg if w["skslxb_locator"]), "merged_workxml": merged,
           "source": "K&S/SKSLXB (kuhn-stahl-dryrun) + vault work pages, merged with edep_sino works.xml",
           "note": "Premodern Chinese epigraphy works (金石學). SKSLXB locator where resolved else series. Curated author→person links, editions, relations from edep_sino works.xml. Not limited to SKSLXB. No paratexts.",
           "works": reg}, open(OUT + "/premodern.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"generated": "2026-06-27", "count": len(plist),
           "source": "edep_sino persons.xml (register) + people/*.xml (canonical); works-authored from the work merge",
           "persons": plist}, open(OUT + "/persons.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

toc = defaultdict(list)
for w in reg:
    if w["in_skslxb"] and w.get("skslxb_series"):
        toc[w["skslxb_series"]].append({"id": w["id"], "title_zh": w["title_zh"], "author_zh": w["author_zh"], "locator": w["skslxb_locator"]})
json.dump({"generated": "2026-06-27", "series": {str(k): toc[k] for k in sorted(toc)},
           "note": "石刻史料新編 (新文豐, 1977–2006), 第一–四輯, via the Kuhn & Stahl bibliography."},
          open(OUT + "/skslxb-toc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in ("premodern.json", "persons.json", "skslxb-toc.json"): shutil.copy(OUT + "/" + f, APP + "/" + f)

print("register:", len(reg), "| merged with works.xml:", merged, "| with author_id:", sum(1 for w in reg if w["author_id"]))
print("persons:", len(plist), "| with >=1 work:", sum(1 for p in plist if p["work_count"]),
      "| with bio:", sum(1 for p in plist if p.get("bio")), "| with zi/hao:", sum(1 for p in plist if p.get("zi") or p.get("hao")))
print("editions attached:", sum(len(w["editions"]) for w in reg), "| relations:", sum(len(w["relations"]) for w in reg))
