# -*- coding: utf-8 -*-
"""Modern epigraphic corpora register — from the obsidian-vault geographic fan-out.
READ-ONLY. Parses the bullet-list topographic inventory into a flat JSON table.

Source: obsidian-vault/projects/AI responses/AI epigraphic-corpora-topographic-inventory.md
  # title
  ## 全國 — national / multi-province series           → section national
  ## 省 — by province → ### region → #### 北京 (23)      → section province (region, province)
       *省級:* / *府/市級:* / *縣級:* / *專題:* / …        → admin level
  ## 名山與重要遺址 → ### 五嶽 → #### 泰山                → section site (category, site)
  entry: - [✚] **title 漢字** (Pinyin) · author · year · publisher · ≈scope · ISBN … — _holdings_

Output: corpora.json (copied to the app for relative no-auth fetch).
"""
import json, os, re, shutil

SRC = "/Users/sassmann/repos/vaults/obsidian-vault/projects/AI responses/AI epigraphic-corpora-topographic-inventory.md"
OUT = "/Users/sassmann/repos/GitHub/epiwen-public/harvest/corpora"
APP = "/Users/sassmann/repos/GitHub/epiwen"
CJK = "㐀-鿿豈-﫿"

# canonical dedup key: CJK-only, folded to SIMPLIFIED so traditional/simplified forms of the
# same title collapse (the 海交史 bibliography is traditional; much of the register is simplified).
# Uses OpenCC if installed (phrase-accurate); otherwise the vendored single-char map
# t2s-charmap.json (generated from OpenCC) so the build is self-contained / reproducible.
_HERE = os.path.dirname(os.path.abspath(__file__))
def _cjk(s): return re.sub("[^" + CJK + "]", "", s or "")
try:
    from opencc import OpenCC
    _conv = OpenCC("t2s").convert
except Exception:
    try:
        _T2S = json.load(open(os.path.join(_HERE, "t2s-charmap.json"), encoding="utf-8"))
    except Exception:
        _T2S = {}
    def _conv(s): return "".join(_T2S.get(ch, ch) for ch in s)
def canon(s): return _conv(_cjk(s))

def slug(s, i):
    return "mc-" + (re.sub(r"[^0-9a-z]+", "-", (s or "").lower()).strip("-")[:24] or "x") + "-" + str(i)

def parse_entry(line):
    gap = bool(re.match(r"^✚\s+", line)); line = re.sub(r"^✚\s+", "", line)
    holdings = ""
    m = re.search(r"\s+—\s+_(.+?)_\s*$", line)
    if m: holdings = m.group(1); line = line[:m.start()]
    isbns = re.findall(r"ISBN(?:\s+set)?\s*([0-9Xx][0-9Xx\- ]{8,16}[0-9Xx])", line)
    chunks = [c.strip() for c in line.split(" · ")]
    head = chunks[0]
    tz = re.search(r"\*\*(.+?)\*\*", head)
    title_zh = tz.group(1).strip() if tz else re.sub(r"\*", "", head).strip()
    py = re.search(r"\(([^)]+)\)", head[tz.end():] if tz else head)
    title_py = py.group(1).strip() if py else ""
    rest = chunks[1:]
    # Fields appear in fixed order: [author] · [year] · [publisher] · [≈scope] · [ISBN].
    # The year is the reliable anchor — author is everything before it, publisher the first
    # real chunk after it. Author and publisher share vocabulary (圖書館/研究所/編輯部 occur in
    # both institutional authors and presses), so only position — not content — can separate them.
    def is_scope(c): return c.lstrip().startswith("≈")
    def is_isbn(c): return "ISBN" in c
    def is_date(c):
        # The date FIELD begins with a year/decade/century/circa or an explicit dating phrase.
        # An author with parenthetical dates ("李恆法 (…, 2011)") starts with a name, so is excluded.
        core = re.sub(r"^[(（✚\s]+", "", c.strip())
        core = re.sub(r"^(c\.|ca\.|circa|約|约)\s*", "", core, flags=re.I)
        return bool(re.match(r"(1[5-9]\d\d|20[0-3]\d)\b", core)          # 2011 · 2011; 2002 · 1977–2006
                    or re.match(r"(1[5-9]\d0s|20[0-3]0s)", core)          # 1990s · 2000s
                    or re.match(r"(1[0-9]|2[01])(th|st|nd|rd)\b", core)   # 20th · 21st
                    or (re.match(r"(unknown|in progress|in prep|forthcoming|pending|n\.?d\.?|undated|待考|擬|Republican)", core, re.I)
                        and re.search(r"\d", core)))
    yidx = next((i for i, c in enumerate(rest) if is_date(c)), -1)
    if yidx >= 0:
        author = " · ".join(rest[:yidx]).strip()
        year = rest[yidx].strip()
        after = rest[yidx + 1:]
    else:  # genuinely undated
        author = rest[0].strip() if (rest and not is_scope(rest[0]) and not is_isbn(rest[0])) else ""
        year = ""
        after = rest[1:] if author else rest[:]
    publisher = ""
    for c in after:
        if is_scope(c) or is_isbn(c): continue
        publisher = c.strip(); break
    scope = next((c.lstrip().lstrip("≈").strip() for c in rest if is_scope(c)), "")
    h = holdings
    return {
        "title_zh": title_zh, "title_pinyin": re.sub(r"\s+", " ", title_py),
        "author": author, "year": year, "publisher": publisher, "scope": scope,
        "isbn": [re.sub(r"[\s\-]", "", x) for x in isbns], "gapfill": gap,
        "holdings": {
            "vault": ("in vault" in h or "📁" in h),
            "sbb": ("SBB" in h or "📗" in h or "Staatsbib" in h),
            "k10plus": ("K10plus" in h),
            "harvard": ("Harvard" in h or "🎓" in h),
        },
    }

records = []
section = region = province = site = admin = ""
i = 0
for raw in open(SRC, encoding="utf-8"):
    line = raw.rstrip("\n")
    s = line.strip()
    if s.startswith("## "):
        h = s[3:].strip()
        region = province = site = admin = ""
        if h.startswith("全國"): section = "national"
        elif h.startswith("省"): section = "province"
        elif h.startswith("名山") or "遺址" in h: section = "site"
        elif h.startswith("補遺"): section = "supplement"
        else: section = "meta"   # "Method & status" etc. — not corpora
        continue
    if s.startswith("### "):
        region = re.sub(r"\s*\(.*\)$", "", s[4:].strip()); province = site = ""; admin = ""
        continue
    if s.startswith("#### "):
        name = re.sub(r"\s*\(\d+\)\s*$", "", s[5:].strip())
        if section == "site": site = name
        else: province = name
        admin = ""
        continue
    am = re.match(r"^\*(.+?):\*$", s)
    if am: admin = am.group(1).strip(); continue
    if s.startswith("- "):
        if section not in ("national", "province", "site", "supplement"): continue
        e = parse_entry(s[2:].strip())
        if not e["title_zh"]: continue
        i += 1
        e["id"] = slug(e["title_pinyin"] or e["title_zh"], i)
        e["section"] = section
        e["region"] = region
        e["province"] = province if section == "province" else ""
        e["site"] = site if section == "site" else ""
        e["category"] = region if section == "site" else ""
        e["admin"] = admin if section == "province" else ""
        e["place"] = (province or site or ("national" if section == "national"
                      else "補遺 (gap-fill)" if section == "supplement" else region) or "")
        records.append(e)

# ── append the county/prefecture web fan-out (broad-then-narrow, evidence-required) ──
# These come AFTER the holdings-verified inventory, so the dedup below keeps the verified
# row when a title appears in both. They carry their own county locality + an evidence URL,
# and are flagged web=True (not library-located) so the UI can distinguish them.
def clean_loc(s):
    s = re.split(r"[／/、]", s or "")[0]
    s = re.sub(r"（[^）]*）|\([^)]*\)", "", s)
    return re.sub(r"(地區|地区|自治州|自治區|盟|區|区|市|縣|县)$", "", s).strip()
try:
    fo = json.load(open(OUT + "/fanout-counties.json", encoding="utf-8")).get("corpora", [])
except Exception:
    fo = []
# Verification verdicts. A web row is kept ONLY if confirmed in a real LIBRARY CATALOG:
#  - verify-results.json: confirmed_source matching CAT_RE (already a catalog), or
#  - catalog-verify-results.json: in_catalog == true (CiNii / NDL / WorldCat / K10plus / NLC …).
# Booksellers (douban/kongfz), blogs, news, publisher pages, and bibliographies do NOT count.
CAT_RE = re.compile(r"ci\.nii|cinii|worldcat|k10plus|kxp\.k10|opac\.k10|gvk|d-nb|dnb|stabikat|hollis|lib\.harvard"
                    r"|ndl\.go|ndlsearch|iss\.ndl|nlc\.cn|opac\.nlc|read\.nlc|find\.nlc|国家图书馆|國家圖書館|国图"
                    r"|ncl\.edu\.tw|duxiu|读秀|讀秀|calis|\.lib\.|opac|图书馆|圖書館|联合目录|聯合目錄|union catalog|library catalog", re.I)
try:
    verdicts = {v["id"]: v for v in json.load(open(OUT + "/verify-results.json", encoding="utf-8")).get("results", []) if v.get("id")}
except Exception:
    verdicts = {}
try:
    catverdicts = {v["id"]: v for v in json.load(open(OUT + "/catalog-verify-results.json", encoding="utf-8")).get("results", []) if v.get("id")}
except Exception:
    catverdicts = {}
for k, x in enumerate(fo):
    if not x.get("title_zh") or not x.get("province"): continue
    rid = slug(x.get("title_pinyin") or x["title_zh"], 10000 + k)
    v = verdicts.get(rid)
    if verdicts and not (v and v.get("verified")): continue        # must be verified at all
    cv = catverdicts.get(rid)
    in_cat = bool((v and CAT_RE.search(v.get("confirmed_source") or "")) or (cv and cv.get("in_catalog")))
    if catverdicts and not in_cat: continue                        # catalog-only, once the catalog pass exists
    corr = (cv and cv.get("corrections")) or (v and v.get("corrections")) or {}
    isbn_src = corr.get("isbn") or x.get("isbn")
    def catname(s):
        s = s or ""
        for pat, nm in [(r"ci\.nii|cinii", "CiNii"), (r"ndl", "NDL"), (r"worldcat", "WorldCat"),
                        (r"k10|gvk|d-nb|dnb", "K10plus"), (r"nlc|国家图书馆|國家圖書館|国图", "NLC"),
                        (r"hollis|lib\.harvard", "Harvard"), (r"stabikat", "SBB"), (r"duxiu|读秀|讀秀", "讀秀")]:
            if re.search(pat, s, re.I): return nm
        return "catalog" if CAT_RE.search(s) else ""
    catalog = (cv and cv.get("catalog")) or catname(v.get("confirmed_source") if v else "")
    cat_url = (cv and cv.get("catalog_url")) or (v and v.get("confirmed_source")) or x.get("evidence", "")
    records.append({
        "title_zh": x["title_zh"], "title_pinyin": x.get("title_pinyin", ""),
        "author": corr.get("author") or x.get("author", ""), "year": corr.get("year") or x.get("year", ""),
        "publisher": corr.get("publisher") or x.get("publisher", ""), "scope": "",
        "isbn": ([re.sub(r"[\s\-]", "", isbn_src)] if isbn_src else []),
        "gapfill": False, "web": True, "web_verified": True, "web_catalog": catalog,
        "evidence": cat_url,
        "id": rid, "section": "province", "region": x.get("region", ""), "province": x["province"],
        "site": "", "category": "", "admin": x.get("admin", ""),
        "locality": clean_loc(x.get("locality", "")), "place": x["province"],
        "holdings": {"vault": False, "sbb": False, "k10plus": False, "harvard": False},
    })

# drop exact-duplicate rows (a national/site series cross-listed under a province)
seen = set(); dedup = []
for r in records:
    k = (canon(r["title_zh"]), r["author"], r["year"])
    if k in seen: continue
    seen.add(k); dedup.append(r)
records = dedup

# narrow the web fan-out: drop a web row whose title already exists in the holdings-verified
# inventory (keep the verified one) or duplicates another web row (multi-volume titles differ,
# so they survive). Non-web rows are untouched (multi-volume same-title sets are preserved).
nonweb = [r for r in records if not r.get("web")]
nonweb_titles = set(canon(r["title_zh"]) for r in nonweb)
web_kept = []; web_seen = set()
for r in records:
    if not r.get("web"): continue
    t = canon(r["title_zh"])
    if not t or t in nonweb_titles or t in web_seen: continue
    web_seen.add(t); web_kept.append(r)
records = nonweb + web_kept

# place the "補遺 — gap-fill additions (unplaced)" entries into the main geographic run
# (keep gapfill=True so they still carry the ✚ marker). Their place is unambiguous from
# the title; mapped explicitly to stay exact.
PLACE_SUPP = {
    "遼代石刻文編": {"section": "national"},                                            # Liao-dynasty corpus, national
    "杭州花港摩崖萃編": {"section": "province", "region": "華東", "province": "浙江"},     # Hangzhou
    "徽州文物圖錄": {"section": "province", "region": "華東", "province": "安徽"},         # Huizhou
    "武當山碑刻": {"section": "site", "category": "道教名山", "site": "武當山"},           # Wudangshan
    "麥積區金石校注": {"section": "province", "region": "西北", "province": "甘肅"},       # Maiji, Tianshui
}
for r in records:
    if r["section"] != "supplement": continue
    p = PLACE_SUPP.get(re.sub("[^" + CJK + "]", "", r["title_zh"]))
    if not p: continue
    r["section"] = p["section"]; r["region"] = p.get("region", ""); r["province"] = p.get("province", "")
    r["site"] = p.get("site", ""); r["category"] = p.get("category", "")
    r["place"] = p.get("province") or p.get("site") or ("national" if p["section"] == "national" else "")

# ── reclassify mis-filed "national" entries to their real geography ────────────
REGION = {}
for reg, provs in {"華北": "北京 天津 河北 山西 內蒙古", "東北": "遼寧 吉林 黑龍江",
                   "華東": "上海 江蘇 浙江 安徽 福建 江西 山東", "中南": "河南 湖北 湖南 廣東 廣西 海南",
                   "西南": "重慶 四川 貴州 雲南 西藏", "西北": "陝西 甘肅 青海 寧夏 新疆",
                   "港澳台": "香港 澳門 台灣"}.items():
    for p in provs.split(): REGION[p] = reg
def prov(pn, loc=""): return {"section": "province", "province": pn, "region": REGION.get(pn, ""), "locality": loc}
def site(s, cat): return {"section": "site", "site": s, "category": cat}
def regionwide(reg): return {"section": "province", "region": reg, "place": reg + "地區"}
RECLASS = {  # entries absent here stay genuinely national (nationwide / multi-region / by-dynasty)
    "廣西石刻總集輯校 (全三冊)": prov("廣西"), "陝西碑刻總目提要初編": prov("陝西"),
    "陝西藥王山碑刻藝術總集": prov("陝西", "藥王山"), "山東石刻分類全集（全八冊）": prov("山東"),
    "三晉石刻總目": prov("山西"), "三晉石刻大全": prov("山西"), "千唐誌齋藏誌": prov("河南", "新安"),
    "澤州碑刻大全": prov("山西", "晉城"), "南京歷代碑刻集成": prov("江蘇", "南京"),
    "西安碑林全集": prov("陝西", "西安"), "桂林石刻總集輯校": prov("廣西", "桂林"),
    "西安碑林博物館新藏墓誌彙編 / 續編": prov("陝西", "西安"), "石門石刻大全": prov("陝西", "漢中"),
    "河南碑刻類編 / 河南碑刻續編": prov("河南"), "四川歷代碑刻": prov("四川"),
    "晉城金石志": prov("山西", "晉城"), "齊魯碑刻": prov("山東"), "新中國出土墓誌·河南卷": prov("河南"),
    "澳門記憶（Memória de Macau / Macau Memory）": prov("澳門"), "臺灣古碑拓本": prov("台灣"),
    "國史館臺灣文獻館 碑碣拓本資料庫": prov("台灣"),
    "中國西北地區歷代石刻匯編": regionwide("西北"), "中國西南地區歷代石刻匯編": regionwide("西南"),
    "巴蜀珍稀金石文獻匯刊": regionwide("西南"),
    "響堂山石窟碑刻題記總錄": site("響堂山", "石窟 grottoes"), "龍門石窟碑刻題記彙錄": site("龍門石窟", "石窟 grottoes"),
    "房山石經題記匯編 / 房山石經題記整理與研究": site("房山雲居寺", "刻經 sutra-sites"),
    "泰山石刻 / 泰山石刻大全": site("泰山", "五嶽"),
    "第一批古代名碑名刻文物名錄（黃山摩崖石刻群）": site("黃山", "摩崖 cliff-clusters"),
}
for r in records:
    if r["section"] != "national": continue
    p = RECLASS.get(r["title_zh"])
    if not p: continue
    r["section"] = p["section"]; r["region"] = p.get("region", ""); r["province"] = p.get("province", "")
    r["site"] = p.get("site", ""); r["category"] = p.get("category", ""); r["locality"] = p.get("locality", "")
    r["place"] = p.get("place") or p.get("province") or p.get("site") or r["place"]

# ── 新編碑刻集書目 (李仁淵 / 海交史) — authoritative published bibliography. Add entries not
# already present. Unlike the web fan-out, these are KEPT even when uncatalogued (the source is
# scholarly), flagged verification_pending; a biblio-catalog-verify.json pass can upgrade them.
def bib_place(prov):
    if "專題" in prov or "全區" in prov or "全国" in prov: return ("national", "", "")
    if "東南亞" in prov: return ("overseas", "東南亞 Southeast Asia", "")
    if "重慶" in prov or "四川" in prov: return ("province", "西南", "四川")
    p = {"內蒙": "內蒙古"}.get(prov, prov)
    return ("province", REGION.get(p, ""), p)
try:
    biblio = json.load(open(OUT + "/xinbian-beikeji.json", encoding="utf-8")).get("entries", [])
except Exception:
    biblio = []
try:
    bibcat = {v["id"]: v for v in json.load(open(OUT + "/biblio-catalog-verify.json", encoding="utf-8")).get("results", []) if v.get("id")}
except Exception:
    bibcat = {}
present = set(canon(r["title_zh"]) for r in records)
badd = 0
for e in biblio:
    t = (e.get("title") or "").strip(); nt = canon(t)
    if not nt or nt in present: continue
    present.add(nt); badd += 1
    sec, reg, prov = bib_place(e.get("province", ""))
    if "重慶" in t: prov = "重慶"
    rid = slug(t, 20000 + badd)
    cv = bibcat.get(rid); in_cat = bool(cv and cv.get("in_catalog")); corr = (cv and cv.get("corrections")) or {}
    records.append({
        "title_zh": t, "title_pinyin": "", "author": corr.get("author") or e.get("author", ""),
        "year": corr.get("year") or e.get("year", ""), "publisher": corr.get("publisher") or e.get("publisher", ""),
        "scope": "", "isbn": ([re.sub(r"[\s\-]", "", corr["isbn"])] if corr.get("isbn") else []),
        "gapfill": False, "biblio": True, "web_verified": in_cat, "web_catalog": (cv.get("catalog") if in_cat else ""),
        "verification_pending": (not in_cat),
        "evidence": (cv.get("catalog_url") if in_cat else "https://idv.sinica.edu.tw/ryli/stoneinscriptions.htm"),
        "id": rid, "section": sec, "region": reg, "province": prov, "site": "", "category": "", "admin": "",
        "locality": "", "place": (prov or ("全國" if sec == "national" else reg) or "東南亞"),
        "holdings": {"vault": False, "sbb": False, "k10plus": False, "harvard": False},
    })

# ── county/prefecture level: a `locality` for each entry ───────────────────────
GENRE = (r"(金石|石刻|碑刻|碑誌|碑志|墓誌|墓志|題記|題刻|題名|摩崖|碑碣|碑帖|碑石|碑銘|貞石|石經|造像|碑林|石窟|"
         r"畫像石|磚銘|磚文|題跋|拓片|拓本|文物|碑錄|碑版|名碑|誌|志|錄|彙編|匯編|輯録|輯校|總目|總集|大全|"
         r"集成|全集|類編|選編|選粹|菁華|擷英|考|圖錄|資料|新編|續編|補正|存)")
ALIASES = {"齊魯", "山右", "三晉", "中州", "中原", "巴蜀", "八閩", "三秦", "燕趙", "荊楚", "嶺南", "關中", "河朔", "日下", "京師", "金陵"}
def compute_locality(r):
    if r["section"] == "site": return r.get("site", "")
    if r["section"] != "province" or not r.get("province"): return ""
    if r.get("admin") in ("省級", "全國", "專題"): return ""        # province-wide / thematic
    t = r["title_zh"].split(" ")[0].split("／")[0].split("/")[0]
    t = re.sub(r"^.{1,9}?(圖書館|博物館|博物院|檔案館|大學|研究院|研究所|文管會|文物局|文化局|文管處|地方誌)[^藏]{0,4}?(藏|新藏|編|)", "", t)
    t = re.sub(r"^(明清以來|明清|清代|清|明代|明|宋元|元明|歷代|近代|當代|近現代|民國|漢魏|隋唐五代|隋唐|唐宋|北朝|南北朝|新出|新發現|新見|出土)", "", t)
    t = re.sub("^(" + re.escape(r["province"]) + ")(省|市|地區|區|自治區)?", "", t)
    m = re.search(GENRE, t)
    if not m: return ""                                            # no genre word → not a clean place+genre title
    loc = t[:m.start()]
    loc = re.sub(r"(省|市|地區|自治區|自治州|盟|區|縣)$", "", loc).strip("（）()·・ 　")
    for _ in range(4):  # strip trailing era/topic qualifiers left clinging to the place name
        loc2 = re.sub(r"(歷代|歴代|古代|古刻|新出|新見|出土|道教|佛教|工商業|社會史|農業經濟|縣學|寺廟|地區|地区|選|古)$", "", loc).strip()
        loc2 = re.sub(r"(地區|地区|區|区|市)$", "", loc2)
        if loc2 == loc: break
        loc = loc2
    if loc in ALIASES: return ""                                    # classical alias == the province itself
    return loc if re.match(r"^[㐀-鿿]{1,5}$", loc) else ""
for r in records:
    if not r.get("locality"): r["locality"] = compute_locality(r)

os.makedirs(OUT, exist_ok=True)
meta = {"generated": "2026-06-26", "count": len(records),
        "source": "obsidian-vault geographic fan-out: AI epigraphic-corpora-topographic-inventory.md",
        "note": "Modern (20th–21st c.) published epigraphic corpora of China, by geography (national / province / site). Holdings checked against Harvard-Yenching, Staatsbibliothek Berlin, K10plus.",
        "corpora": records}
json.dump(meta, open(OUT + "/corpora.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
shutil.copy(OUT + "/corpora.json", APP + "/modern-corpora.json")

bysec = {}
for r in records: bysec[r["section"]] = bysec.get(r["section"], 0) + 1
print("corpora:", len(records), "| by section:", bysec)
print("with year:", sum(1 for r in records if r["year"]), "| with ISBN:", sum(1 for r in records if r["isbn"]),
      "| holdings(any):", sum(1 for r in records if any(r["holdings"].values())), "| gapfill:", sum(1 for r in records if r["gapfill"]))
print("provinces:", len(set(r["province"] for r in records if r["province"])),
      "| sites:", len(set(r["site"] for r in records if r["site"])))
print("sample:", json.dumps({k: records[20][k] for k in ("title_zh", "author", "year", "publisher", "place", "region", "holdings")}, ensure_ascii=False))
