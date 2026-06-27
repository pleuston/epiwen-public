# -*- coding: utf-8 -*-
"""Premodern Sources work register — from the (finished) obsidian-vault work. READ-ONLY.

Clean Chinese titles come from ks-concordance.json (953 K&S/SKSLXB works) + the vault
epigraphy work-page filenames (broader, NOT limited to SKSLXB). The *verified* SKSLXB
locators (series.volume:page) live in entries.json — attached to the concordance works by
per-K&S-page positional alignment (both list a page's works top-to-bottom). No paratexts.

Outputs (epiwen-public/harvest/premodern/ + copied to epiwen/):
  premodern.json   — the work register
  skslxb-toc.json  — SKSLXB collection structure (series → works) for the contents page
"""
import json, os, re, glob, shutil
from collections import defaultdict

VAULT = "/Users/sassmann/repos/vaults/obsidian-vault"
KS = VAULT + "/projects/AI responses/kuhn-stahl-dryrun"
WORKPAGES = VAULT + "/knowledge base/Texts/Epigraphy 金石學"
OUT = "/Users/sassmann/repos/GitHub/epiwen-public/harvest/premodern"
APP = "/Users/sassmann/repos/GitHub/epiwen"
CJK = "㐀-鿿豈-﫿"

def norm(s): return re.sub("[^" + CJK + "]", "", s or "")
def cjk_run(s):
    m = re.search("[" + CJK + "]{2,}", s or ""); return m.group(0) if m else ""
def slug(s, pre):
    return pre + "-" + (re.sub(r"[^0-9a-z]+", "-", (s or "").lower()).strip("-") or "x")
def dyn(y):
    if y is None: return ""
    return ("Han 漢" if y < 220 else "Six Dyn. 魏晉南北朝" if y < 589 else "Sui–Tang 隋唐" if y < 907
            else "Song 宋" if y < 1279 else "Yuan 元" if y < 1368 else "Ming 明" if y < 1912 else "Qing 清")
def birth(s):
    m = re.search(r"(\d{3,4})\s*[-–]", s or ""); return int(m.group(1)) if m else None
def parse_wp(fn):
    base = re.sub(r"\.md$", "", fn); tm = re.search(r"《([^》]+)》", base)
    title = tm.group(1) if tm else base; head = base[:tm.start()] if tm else ""
    pin = re.match(r"^([A-Za-z .'-]+)", head or "")
    return title, cjk_run(head), (pin.group(1).strip() if pin else "")

# entries.json grouped by K&S page (in file order = on-page order)
entries = json.load(open(KS + "/entries.json", encoding="utf-8"))
ent_by_page = defaultdict(list)
for e in entries: ent_by_page[e.get("pdf_page")].append(e)

# concordance (clean CJK titles) grouped by page; align to entries positionally
conc = json.load(open(KS + "/ks-concordance.json", encoding="utf-8"))
conc_by_page = defaultdict(list)
for c in conc: conc_by_page[c.get("page")].append(c)

reg = []; seen = set(); loc_hit = 0
for page, clist in conc_by_page.items():
    elist = ent_by_page.get(page, [])
    for k, c in enumerate(clist):
        e = elist[k] if k < len(elist) and len(elist) == len(clist) else None  # zip only when page counts agree
        title = (c.get("title") or "").strip()
        if not norm(title): continue
        seen.add(norm(title))
        author_zh = author_py = vault_page = ""
        if c.get("match"):
            vault_page = c["match"]; _, author_zh, author_py = parse_wp(c["match"])
        loc = e.get("locator") if e else ""
        if loc: loc_hit += 1
        yr = birth(e.get("author_dates")) if e else None
        reg.append({
            "id": slug(loc, "ks") if loc else slug(c.get("title"), "ks-t") + "-" + str(page),
            "title_zh": title, "title_pinyin": "", "author_zh": author_zh, "author_pinyin": author_py,
            "dynasty": dyn(yr), "juan": (e.get("juan") if e else None),
            "in_skslxb": True, "skslxb_series": (e.get("series") if e else c.get("series")),
            "skslxb_locator": loc,
            "skslxb_pages": (str(e.get("page_start")) + "-" + str(e.get("page_end")) if e and e.get("page_start") else ""),
            "period_covered": (e.get("period_covered") if e else None),
            "author_dates": (e.get("author_dates") if e else None),
            "transcriptions": (e.get("transcriptions") if e else None),
            "has_epitaphs": (e.get("has_epitaphs") if e else None),
            "catalogue": {k2: v for k2, v in ((e.get("catalogue") if e else {}) or {}).items() if v not in (None, "", False)},
            "ks_page": page, "ks_date": c.get("date"), "vault_page": vault_page,
            "source": "Kuhn & Stahl 1991 / 石刻史料新編",
        })

# broader vault work pages NOT already in the register (non-SKSLXB / not in K&S)
extra = 0
for p in sorted(glob.glob(WORKPAGES + "/*《*》*.md")):
    title, author_zh, author_py = parse_wp(os.path.basename(p))
    if not norm(title) or norm(title) in seen: continue
    seen.add(norm(title)); extra += 1
    reg.append({"id": slug(author_py, "wp") + "-" + str(extra), "title_zh": title, "title_pinyin": "",
                "author_zh": author_zh, "author_pinyin": author_py, "dynasty": "", "juan": None,
                "in_skslxb": False, "skslxb_series": None, "skslxb_locator": "", "catalogue": {},
                "vault_page": os.path.basename(p)[:-3], "source": "vault epigraphy work page"})

reg.sort(key=lambda w: (0 if w["in_skslxb"] else 1, w.get("skslxb_series") or 9, w["title_zh"]))
os.makedirs(OUT, exist_ok=True)
json.dump({"generated": "2026-06-27", "count": len(reg), "in_skslxb": sum(1 for w in reg if w["in_skslxb"]),
           "with_locator": sum(1 for w in reg if w["skslxb_locator"]),
           "source": "obsidian-vault: Kuhn & Stahl 1991 annotated bibliography of 石刻史料新編 (clean titles via ks-concordance) + vault epigraphy work pages",
           "note": "Premodern Chinese epigraphy sources (金石學 works). SKSLXB works carry a verified locator (series.volume:page) where the per-page alignment resolved it, else the series. Not limited to SKSLXB. No paratexts.",
           "works": reg}, open(OUT + "/premodern.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

toc = defaultdict(list)
for w in reg:
    if w["in_skslxb"] and w.get("skslxb_series"):
        toc[w["skslxb_series"]].append({"id": w["id"], "title_zh": w["title_zh"], "author_zh": w["author_zh"], "locator": w["skslxb_locator"]})
json.dump({"generated": "2026-06-27", "series": {str(k): toc[k] for k in sorted(toc)},
           "note": "石刻史料新編 (新文豐, 1977–2006), 第一–四輯, via the Kuhn & Stahl bibliography."},
          open(OUT + "/skslxb-toc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in ("premodern.json", "skslxb-toc.json"): shutil.copy(OUT + "/" + f, APP + "/" + f)

print("register:", len(reg), "| in SKSLXB:", sum(1 for w in reg if w['in_skslxb']), "| non-SKSLXB:", extra)
print("with precise locator:", loc_hit, "| with author:", sum(1 for w in reg if w["author_zh"]))
pages_eq = sum(1 for p in conc_by_page if len(conc_by_page[p]) == len(ent_by_page.get(p, [])))
print("K&S pages with concordance==entries count:", pages_eq, "/", len(conc_by_page))
print("SKSLXB series:", {k: len(v) for k, v in sorted(toc.items())})
print("sample:", json.dumps([{ "t": w["title_zh"], "a": w["author_zh"], "loc": w["skslxb_locator"]} for w in reg[:5]], ensure_ascii=False))
