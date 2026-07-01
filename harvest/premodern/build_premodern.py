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
SKSLXB_TOC = VAULT + "/knowledge base/Texts/Epigraphy 金石學/Collections, Lists, Bibliographies/《石刻史料新编》第1－4辑目錄.md"
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

# ── 1) K&S + vault spine ──────────────────────────────────────────────────────
entries = json.load(open(KS + "/entries.json", encoding="utf-8"))
ent_by_page = defaultdict(list)
for e in entries: ent_by_page[e.get("pdf_page")].append(e)
valid_loc = set(e["locator"] for e in entries if e.get("locator"))
loc_entry = {e["locator"]: e for e in entries if e.get("locator")}
conc = json.load(open(KS + "/ks-concordance.json", encoding="utf-8"))
conc_by_page = defaultdict(list)
for c in conc: conc_by_page[c.get("page")].append(c)

# locator ↔ clean CJK title from the Apple-Vision OCR (the SKSLXB locator line is followed by
# the work's CJK title); keep only locators that exist in entries.json. This recovers the page
# numbers (verified, in K&S) for far more works than the fragile positional alignment did.
ocrdata = json.load(open(KS + "/ks-applevision-ocr.json", encoding="utf-8"))
LOC_RE = re.compile(r"^\s*([1-4]\.\d+:\d+(?:-\d+)?)")
ocr_loc = {}; loc2title = {}
for _pg, _lines in ocrdata.items():
    for i, ln in enumerate(_lines):
        s = (ln or "").strip(); m = LOC_RE.match(s)
        if not (m and m.group(1) in valid_loc): continue
        t = cjk_run(s[m.end():])                                # title after the locator, SAME line
        if not t and i + 1 < len(_lines): t = cjk_run(_lines[i + 1])   # else the next line
        if t: ocr_loc.setdefault(norm(t), m.group(1)); loc2title.setdefault(m.group(1), t)

# SKSLXB authoritative 目錄 (all four 輯, incl. 第四輯) from the vault TOC
SER_ZH = {"一": 1, "二": 2, "三": 3, "四": 4}
NUM = "〇零一二三四五六七八九十百千兩半"
DYN = ["民國", "北魏", "南朝", "北朝", "三國", "後魏", "五代", "明", "清", "宋", "元", "唐", "漢", "晉", "魏", "隋", "金", "遼", "周", "秦", "梁", "陳", "齊"]
ROLE = r"(撰校勘記|輯補遺|撰並書|手拓|撰|輯|編|纂|注|集|藏|錄)"
def cjk_dyn(d):
    return {"漢": "Han 漢", "魏": "Six Dyn. 魏晉南北朝", "晉": "Six Dyn. 魏晉南北朝", "南朝": "Six Dyn. 魏晉南北朝",
            "北朝": "Six Dyn. 魏晉南北朝", "北魏": "Six Dyn. 魏晉南北朝", "後魏": "Six Dyn. 魏晉南北朝", "三國": "Six Dyn. 魏晉南北朝",
            "隋": "Sui–Tang 隋唐", "唐": "Sui–Tang 隋唐", "五代": "Sui–Tang 隋唐", "宋": "Song 宋", "遼": "Song 宋",
            "金": "Song 宋", "元": "Yuan 元", "明": "Ming 明", "清": "Qing 清", "民國": "modern 近現代"}.get(d, "")
def parse_toc_entry(line):
    line = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", line.strip())   # Obsidian wikilinks → text
    parts = [p.strip() for p in re.split(r"[.．]", line) if p.strip()]
    if not parts: return None
    bk = re.search(r"《([^》]+)》", parts[0])
    if bk:
        title = bk.group(1).strip()
    else:
        jm = re.search(r"(殘[" + NUM + r"]*卷|[" + NUM + r"]+卷|不分卷)", parts[0])   # 六藝之一録殘一百三十一卷 → 六藝之一録
        title = (parts[0][:jm.start()] if jm else parts[0]).strip()
    d = a = ""
    for i, p in enumerate(parts):
        if p in DYN:
            d = p
            if i + 1 < len(parts): a = re.sub(r"\s*" + ROLE + r"$", "", parts[i + 1]).strip()
            break
    if bk and not a: a = cjk_run(parts[0][:bk.start()])
    return {"title": title, "dynasty": d, "author": a}
# a 目錄 line may BUNDLE several works before the 朝代.作者 tail (壬癸金石跋一卷.己庚金石跋一卷.
# 丁戊金石跋一卷.清.楊守敬 撰) — extract each, cleaning 卷數 / 上下編 / 第N集至第N輯.
_GENRE_T = re.compile("(金石|碑|誌|志|錄|録|記|目|考|跋|刻|銘|碣|磚|瓦|拓|集|編|略|表|圖|譜|苑|林|遺|存|摭|徵|叢|字|篆|隸|款|識|帖)")
def toc_titles(line):
    line = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", line.strip())
    dm = re.search(r"[.．](?:" + "|".join(DYN) + r"|闕名|不著撰|舊題|滿州)(?=[.．\s])", "." + line)
    head = ("." + line)[:dm.start()].lstrip(".．") if dm else line
    out = []
    for seg in re.split(r"[.．]", head):
        seg = re.sub(r"(第[" + NUM + r"0-9]+集[至第\s" + NUM + r"0-9輯]*|殘?[" + NUM + r"]+卷|不分卷)$", "", seg.strip())
        seg = re.sub(r"(上編|下編|坿.*|補遺.*)$", "", seg).strip()
        if re.match(r"^[" + CJK + r"]{3,14}$", seg) and _GENRE_T.search(seg): out.append(seg)
    return out
vault_titles = set()                                          # titles that actually have a vault work-page
for _p in glob.glob(WORKPAGES + "/*《*》*.md"):
    _wt = parse_wp(os.path.basename(_p))[0]
    if _wt: vault_titles.add(norm(_wt))
toc_map = {}; toc_works = []
_ser = 0; _cat = ""
for raw in open(SKSLXB_TOC, encoding="utf-8"):
    s = raw.strip()
    if not s or s.startswith("#") or s.startswith("《石刻史料"): continue
    m = re.match(r"^石刻史料新編第([一二三四])輯", s)
    if m: _ser = SER_ZH[m.group(1)]; _cat = ""; continue
    if re.match(r"^.{1,10}類$", s): _cat = s; continue
    if "新文豐出版公司" in s or s.startswith("景印") or re.match(r"^\d+册", s) or _ser == 0: continue
    e = parse_toc_entry(s)
    if e and e["title"] and re.search("[" + CJK + "]", e["title"]):
        e["series"] = _ser; e["category"] = _cat
        toc_map.setdefault(norm(e["title"]), e); toc_works.append(e)
    for _t in toc_titles(s):                                  # bundled sub-titles — only if a vault page documents it
        if re.search("[" + CJK + "]", _t) and norm(_t) not in toc_map and norm(_t) in vault_titles:
            _e = {"title": _t, "dynasty": (e["dynasty"] if e else ""), "author": "", "series": _ser, "category": _cat}
            toc_map[norm(_t)] = _e; toc_works.append(_e)

# ── K10plus-secured SKSLXB structure: per-册 SBB call numbers ──
#   第一–三輯 → 4"@836959-<輯>,<册>  (callno_map, looked up by K&S 輯.册 locator)
#   第四輯    → 5 B 81572-<册>        (no K&S locator; placed via the 目錄's 册-order segmentation)
try:
    _k10 = json.load(open(OUT + "/k10-skslxb-analytics.json", encoding="utf-8"))
    CALLNO = _k10.get("callno_map", {}); K10_WORKS = _k10.get("works", [])
except Exception:
    CALLNO = {}; K10_WORKS = []
try:
    _T2S = json.load(open(OUT + "/../corpora/t2s-charmap.json", encoding="utf-8"))
except Exception:
    _T2S = {}
_VAR = {"攷": "考", "艸": "草"}                        # 異體字 OpenCC t2s doesn't fold (備攷/備考, 艸隸/草隸)
def tfold(s):                                         # CJK-only, simplified- + 異體字-folded (for SKSLXB title matching)
    return "".join(_VAR.get(_T2S.get(c, c), _T2S.get(c, c)) for c in norm(s))
def sbb_callno(loc):                                  # K&S locator "S.V:page" → 第一–三輯 SBB Signatur for 輯 S, 册 V
    m = re.match(r"^([1-4])\.(\d+)", loc or ""); return CALLNO.get(m.group(1) + "," + m.group(2), "") if m else ""
# 第四輯 册 placement: anchor on the 10 册-leads (六藝之一錄 spans 4–6 → anchor 6), walk the 目錄 in order
def _leadof(s): return re.sub(r"(外[" + NUM + r"]+種|卷.*|殘.*).*$", "", s or "")
_ANCH4 = {}
for _w in K10_WORKS:
    _m = re.search(r"5 B 81572-(\d+)", _w.get("sbb_callno", ""))
    if _m:
        _k = tfold(_leadof(_w["title_zh"]))
        if _k: _ANCH4[_k] = max(_ANCH4.get(_k, 0), int(_m.group(1)))
CE4 = {}; _cur4 = None
for _t in toc_works:                                  # toc_works is in 目錄 order
    if _t.get("series") != 4: continue
    _ft = tfold(_t["title"])
    for _a in _ANCH4:
        if _ft.startswith(_a): _cur4 = _ANCH4[_a]; break
    if _cur4: CE4[_ft] = _cur4
def akey(s):                                          # match key: drop 《》, parentheticals, 外N種/卷-counts; fold 簡/繁/異體
    s = re.sub(r"《([^》]+)》", r"\1", s or ""); s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"外[" + NUM + r"]+種.*$", "", s)       # 六藝之一錄外十種 → 六藝之一錄 (第四輯 catalogues bundle 册-mates)
    s = re.sub(r"([" + NUM + r"]+卷|不分卷).*$", "", s); return tfold(s)   # tfold folds 録/錄, 攷/考 … so variant titles merge
def wp_aliases(path):                                 # frontmatter `aliases:` list of a vault work-page
    try: fm = re.match(r"^---\s*\n(.*?)\n---", open(path, encoding="utf-8").read(), re.S)
    except Exception: return []
    if not fm: return []
    am = re.search(r"^aliases:\s*\n((?:[ \t]*-[ \t]*.*\n?)+)", fm.group(1), re.M)
    return [re.sub(r"^[ \t]*-[ \t]*", "", ln).strip().strip('"').strip("'")
            for ln in am.group(1).splitlines() if ln.strip()] if am else []

reg = []; seen = set()
for page, clist in conc_by_page.items():
    elist = ent_by_page.get(page, [])
    equal = (len(elist) == len(clist))
    for k, c in enumerate(clist):
        title = (c.get("title") or "").strip()
        if not norm(title): continue
        seen.add(norm(title))
        e_pos = elist[k] if (equal and k < len(elist)) else None
        loc = ocr_loc.get(norm(title), "") or (e_pos.get("locator") if e_pos else "")   # OCR-CJK first, positional fallback
        e = loc_entry.get(loc) or e_pos
        t = toc_map.get(norm(title))
        ser = (int(loc.split(".")[0]) if loc else (t["series"] if t else (e.get("series") if e else c.get("series"))))
        author_zh = author_py = vault_page = ""
        if c.get("match"):
            vault_page = c["match"]; _, author_zh, author_py = parse_wp(c["match"])
        if t and t.get("author") and not author_zh: author_zh = t["author"]
        dyn_lbl = (cjk_dyn(t["dynasty"]) if t and t.get("dynasty") else "") or dyn(birth(e.get("author_dates")) if e else None)
        reg.append({
            "id": slug(loc, "ks") if loc else slug(title, "ks-t") + "-" + str(page),
            "title_zh": title, "title_pinyin": "", "author_zh": author_zh, "author_pinyin": author_py,
            "author_id": "", "work_id": "", "dynasty": dyn_lbl, "juan": (e.get("juan") if e else None),
            "in_skslxb": True, "skslxb_series": ser, "skslxb_locator": loc,
            "skslxb_pages": (str(e.get("page_start")) + "-" + str(e.get("page_end")) if e and e.get("page_start") else ""),
            "skslxb_category": (t["category"] if t else ""),
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
                "catalogue": {}, "editions": [], "relations": [], "aliases": wp_aliases(p),
                "vault_page": os.path.basename(p)[:-3], "source": "vault epigraphy work page"})

# ── TOC overlay: authoritative 輯 (incl. 第四輯) + add SKSLXB works still missing ──
for w in reg:
    t = toc_map.get(norm(w["title_zh"]))
    if not t: continue
    if not w["in_skslxb"]:
        w["in_skslxb"] = True
        w["source"] = "石刻史料新編 (目錄) / vault"
        loc = ocr_loc.get(norm(w["title_zh"]), "")
        if loc: w["skslxb_locator"] = loc
    w["skslxb_series"] = (int(w["skslxb_locator"].split(".")[0]) if w["skslxb_locator"] else t["series"])
    w.setdefault("skslxb_category", ""); w["skslxb_category"] = w["skslxb_category"] or t["category"]
    if t.get("dynasty") and not w.get("dynasty"): w["dynasty"] = cjk_dyn(t["dynasty"])
    if t.get("author") and not w.get("author_zh"): w["author_zh"] = t["author"]
tadd = 0
for t in toc_works:
    nt = norm(t["title"])
    if nt in seen: continue
    seen.add(nt); tadd += 1
    loc = ocr_loc.get(nt, ""); e = loc_entry.get(loc)
    reg.append({
        "id": slug(loc, "ks") if loc else slug(t["title"], "toc") + "-" + str(tadd),
        "title_zh": t["title"], "title_pinyin": "", "author_zh": t.get("author", ""), "author_pinyin": "",
        "author_id": "", "work_id": "", "dynasty": cjk_dyn(t.get("dynasty", "")),
        "juan": (e.get("juan") if e else None), "in_skslxb": True,
        "skslxb_series": (int(loc.split(".")[0]) if loc else t["series"]), "skslxb_locator": loc,
        "skslxb_pages": (str(e.get("page_start")) + "-" + str(e.get("page_end")) if e and e.get("page_start") else ""),
        "skslxb_category": t["category"],
        "period_covered": (e.get("period_covered") if e else None), "author_dates": (e.get("author_dates") if e else None),
        "transcriptions": (e.get("transcriptions") if e else None), "has_epitaphs": (e.get("has_epitaphs") if e else None),
        "catalogue": {k2: v for k2, v in ((e.get("catalogue") if e else {}) or {}).items() if v not in (None, "", False)},
        "editions": [], "relations": [], "ks_page": None, "ks_date": None,
        "vault_page": "", "source": "石刻史料新編 (目錄)",
    })

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

# ── fold vault gazetteer pages into their SKSLXB twin (alias match) + drop exact SKSLXB dups ──
# A vault page «三台縣志»(金石) is the same work as the K&S spine «三台金石志» (its frontmatter alias);
# merge it in (so it inherits the K&S locator + page numbers) rather than listing it under "Other".
in_idx = {}
for w in reg:
    if w["in_skslxb"]: in_idx.setdefault(akey(w["title_zh"]), w)
keep = []; folded = 0; seen_ik = set()
for w in reg:
    if w["in_skslxb"]:
        sig = (akey(w["title_zh"]), w.get("skslxb_locator", ""))
        if sig in seen_ik: folded += 1; continue            # exact duplicate SKSLXB entry
        seen_ik.add(sig); keep.append(w); continue
    keys = {akey(w["title_zh"])} | {akey(a) for a in (w.get("aliases") or [])}; keys.discard("")
    hit = next((in_idx[k] for k in keys if k in in_idx), None)
    if hit:                                                  # gazetteer twin of an SKSLXB work → merge
        if not hit.get("vault_page"): hit["vault_page"] = w.get("vault_page", "")
        al = hit.setdefault("aliases", [])
        for a in [w["title_zh"]] + (w.get("aliases") or []):
            if a and a not in al and akey(a) != akey(hit["title_zh"]): al.append(a)
        folded += 1; continue
    keep.append(w)
reg = keep
# promote "Other" works that the CATALOGUE itself breaks out as SKSLXB components (the K10plus
# analytics carry 輯+册) — e.g. 天發神讖碑考 is catalogued under 第三輯 but our K&S/目錄 spine missed it.
K10IDX = {}
for kw in K10_WORKS:
    k = akey(kw["title_zh"])
    if k: K10IDX.setdefault(k, kw)
# OCR'd 官方總目 for 第三輯 考證目錄題跋類 (第33–40 冊): explicit 冊 markers place the bundle-works
zongmu = {}
try:
    _cur = None
    for _ln in open(KS + "/zongmu-ser3-cat3-4.txt", encoding="utf-8"):
        _mm = re.search(r"第\s*(\d+)\s*冊", _ln)
        if _mm: _cur = int(_mm.group(1))
        _t = re.sub(r"(殘?[" + NUM + r"]+卷|不分卷).*$", "", re.split(r"[…．.]", re.sub(r"第\s*\d+\s*冊", "", _ln).strip())[0]).strip()
        if norm(_t) and _cur: zongmu.setdefault(norm(_t), _cur)
except Exception:
    zongmu = {}
# curated 第三輯 地方類 join (series3-difang-datasheet.md: gazetteer《…》→ K&S locator) + the 第三輯
# missing list (series3-missing.csv: 冊,類,title) — both carry the 冊 / full K&S locator.
difang = {}
try:
    for _ln in open(KS + "/series3-difang-datasheet.md", encoding="utf-8"):
        _lc = re.search(r"K&S\s+(3\.\d+:\d+(?:-\d+)?)", _ln)
        if not _lc: continue
        _g = re.search(r"《([^》]+)》", _ln)
        if _g: difang.setdefault(norm(_g.group(1)), _lc.group(1))
        _zm = re.search(r"←\s*\*\*([^*·]+)", _ln)
        if _zm: difang.setdefault(norm(_zm.group(1)), _lc.group(1))
except Exception:
    pass
try:
    for _ln in open(KS + "/series3-missing.csv", encoding="utf-8").read().splitlines()[1:]:
        _c = _ln.split(",")
        if len(_c) >= 3 and _c[0].strip().isdigit(): difang.setdefault(norm(_c[2]), "3." + _c[0].strip())
except Exception:
    pass
promoted = 0
for w in reg:
    if w["in_skslxb"]: continue
    kw = next((K10IDX[k] for k in ({akey(w["title_zh"])} | {akey(a) for a in (w.get("aliases") or [])}) if k in K10IDX), None)
    if kw:
        w["in_skslxb"] = True; w["skslxb_series"] = kw.get("ji")
        if kw.get("ji") and kw.get("ce"): w["skslxb_locator"] = str(kw["ji"]) + "." + str(kw["ce"])
        if kw.get("sbb_callno"): w["sbb_callno"] = kw["sbb_callno"]
        w["source"] = "石刻史料新編 (K10plus analytic)"; promoted += 1; continue
    loc = next((ocr_loc[k] for k in ({norm(w["title_zh"])} | {norm(a) for a in (w.get("aliases") or [])}) if k in ocr_loc), "")
    if loc:                                                  # OCR'd K&S 目錄 places it (第三輯 gazetteers the spine missed)
        w["in_skslxb"] = True; w["skslxb_series"] = int(loc.split(".")[0])
        w["skslxb_locator"] = loc; w["source"] = "石刻史料新編 (K&S OCR 目錄)"; promoted += 1; continue
    ce = next((zongmu[k] for k in ({norm(w["title_zh"])} | {norm(a) for a in (w.get("aliases") or [])}) if k in zongmu), None)
    if ce:                                                   # OCR'd 官方總目 (第三輯 考證目錄題跋類)
        w["in_skslxb"] = True; w["skslxb_series"] = 3
        w["skslxb_locator"] = "3." + str(ce); w["source"] = "石刻史料新編 (OCR 總目 第三輯)"; promoted += 1; continue
    lc2 = next((difang[k] for k in ({norm(w["title_zh"])} | {norm(a) for a in (w.get("aliases") or [])}) if k in difang), None)
    if lc2:                                                  # 第三輯 地方類 join / missing list (gazetteers etc.)
        w["in_skslxb"] = True; w["skslxb_series"] = int(lc2.split(".")[0])
        w["skslxb_locator"] = lc2; w["source"] = "石刻史料新編 (第三輯 地方類/總目 join)"; promoted += 1
# ── gap-fill: K&S locators (entries.json) with NO register work → attach to a matching work, or add it ──
_GENRE = re.compile("(金石|碑|誌|志|錄|録|記|目|考|跋|刻|銘|碣|磚|瓦|拓|集|編|略|表|圖|譜|苑|林|遺|存|摭|徵|叢|石)")
have_loc = set(w.get("skslxb_locator") for w in reg if w.get("skslxb_locator"))
reg_ak = {}
for w in reg:
    for _a in [w["title_zh"]] + (w.get("aliases") or []):
        reg_ak.setdefault(akey(_a), w)
gapfill = 0
for e in entries:
    loc = e.get("locator")
    if not loc or loc in have_loc: continue
    t = loc2title.get(loc)
    if not t or not _GENRE.search(t): continue               # need a genre-word title (skip mis-OCR'd author names)
    hit = reg_ak.get(akey(t))
    if hit and not hit["in_skslxb"]:                         # promote a straggling "Other" work
        hit["in_skslxb"] = True; hit["skslxb_series"] = e.get("series"); hit["skslxb_locator"] = loc
        hit["source"] = "石刻史料新編 (K&S OCR gap-fill)"; gapfill += 1; have_loc.add(loc)
    elif hit and not hit.get("skslxb_locator"):
        hit["skslxb_locator"] = loc; have_loc.add(loc)
    elif not hit:                                            # genuinely missing work → add it
        reg.append({"id": slug(loc, "gap"), "title_zh": t, "title_pinyin": "", "author_zh": "", "author_pinyin": "",
            "author_id": "", "work_id": "", "dynasty": "", "juan": e.get("juan"), "in_skslxb": True,
            "skslxb_series": e.get("series"), "skslxb_locator": loc,
            "skslxb_pages": (str(e.get("page_start")) + "-" + str(e.get("page_end")) if e.get("page_start") else ""),
            "skslxb_category": "", "period_covered": e.get("period_covered"), "author_dates": e.get("author_dates"),
            "catalogue": {}, "editions": [], "relations": [], "vault_page": "", "aliases": [],
            "source": "石刻史料新編 (K&S OCR gap-fill)"})
        gapfill += 1; have_loc.add(loc); reg_ak.setdefault(akey(t), reg[-1])
print("gap-filled orphan K&S locators:", gapfill)
# romanization bridge: give locator-less in_skslxb works their K&S locator (ks-romanized-fills.json,
# pypinyin(title) ↔ K&S romanized titles, exact + same 輯 — precomputed by build_romanized_fills.py)
try:
    _rfills = json.load(open(OUT + "/ks-romanized-fills.json", encoding="utf-8")).get("fills", {})
except Exception:
    _rfills = {}
rfilled = 0
for w in reg:
    if w["in_skslxb"] and not re.match(r"^[1-4]\.\d", (w.get("skslxb_locator") or "")):
        loc = _rfills.get(norm(w["title_zh"]))
        if loc: w["skslxb_locator"] = loc; w["source"] = (w.get("source") or "") + " +romanized-locator"; rfilled += 1
print("romanized-bridge locators filled:", rfilled)
for w in reg:                                                # add the SBB call number from the 輯.册 locator
    cn = sbb_callno(w.get("skslxb_locator", ""))
    if cn: w["sbb_callno"] = cn
# 第四輯 (and any work lacking a precise K&S locator) → match K10plus analytic titles for the call number
try:
    K10W = {akey(w["title_zh"]): w.get("sbb_callno", "") for w in
            json.load(open(OUT + "/k10-skslxb-analytics.json", encoding="utf-8")).get("works", []) if w.get("sbb_callno")}
except Exception:
    K10W = {}
for w in reg:
    if w["in_skslxb"] and not w.get("sbb_callno"):
        for k in ({akey(w["title_zh"])} | {akey(a) for a in (w.get("aliases") or [])}):
            if k and k in K10W: w["sbb_callno"] = K10W[k]; break
        if not w.get("sbb_callno") and w.get("skslxb_series") == 4:   # place into its 册 via the 目錄 segmentation
            ce = CE4.get(tfold(w["title_zh"])) or next((CE4[tfold(a)] for a in (w.get("aliases") or []) if tfold(a) in CE4), None)
            w["sbb_callno"] = ("5 B 81572-" + str(ce)) if ce else "5 B 81572"
print("folded vault gazetteers / dup SKSLXB entries:", folded,
      "| SBB call numbers added:", sum(1 for w in reg if w.get("sbb_callno")),
      "| via 第四輯 title-match:", sum(1 for w in reg if w.get("sbb_callno", "").startswith("5 B 81572")))

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
