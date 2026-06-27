# -*- coding: utf-8 -*-
"""Ingest the skslxb harvest (obsidian-vault, READ-ONLY) into Epiwen staging JSON.

Outputs (epiwen-public/harvest/literature/):
  works.json            — 36 works (22 parsed catalogues + 14 gazetteers), list metadata
  toc/<id>.json         — per-work {excerpts, inscriptions(目錄)} (lazy-loaded by the detail page)
  authorities.json      — 1,698 cross-catalog inscription concordance (+ Wikidata for 39)
  README.md             — provenance + licensing
Also copies works.json / authorities.json / toc/ into the app repo (epiwen/) for relative fetch.
"""
import json, os, re, glob, shutil

VAULT = "/Users/sassmann/repos/vaults/obsidian-vault/projects/AI responses/skslxb-tei-md-dryrun"
OUT   = "/Users/sassmann/repos/GitHub/epiwen-public/harvest/literature"
APP   = "/Users/sassmann/repos/GitHub/epiwen"

# ── author 漢字 → dynasty ──────────────────────────────────────────────────
DYN = {
  "歐陽修":"Song 宋","趙明誠":"Song 宋","洪適":"Song 宋","董逌":"Song 宋","陳思":"Song 宋",
  "王象之":"Song 宋","朱長文":"Song 宋","曾宏父":"Song 宋","施宿":"Song 宋",
  "都穆":"Ming 明","郭宗昌":"Ming 明","陶宗儀":"Ming 明","趙均":"Ming 明","朱珪":"Ming 明","董斯張":"Ming 明",
  "顧炎武":"Qing 清","李光暎":"Qing 清","林侗":"Qing 清","孫承澤":"Qing 清","王澍":"Qing 清","倪濤":"Qing 清",
  "顧藹吉":"Qing 清","畢沅":"Qing 清",
  "酈道元":"Northern Wei 北魏","納新":"Yuan 元","吾丘衍":"Yuan 元","陳暐":"Yuan 元",
}
# work 漢字 → (pinyin title, slug). Covers the 22 parsed + 14 gazetteers.
TITLE = {
  "集古錄":("Jigulu","jigulu"), "金石錄":("Jinshilu","jinshilu"), "隸釋":("Lishi","lishi"),
  "隸續":("Lixu","lixu"), "寶刻叢編":("Baoke congbian","baoke-congbian"),
  "寶刻類編":("Baoke leibian","baoke-leibian"), "輿地碑記目":("Yudi beiji mu","yudi-beiji-mu"),
  "廣川書跋":("Guangchuan shuba","guangchuan-shuba"), "墨池編":("Mochi bian","mochi-bian"),
  "石刻鋪敍":("Shike puxu","shike-puxu"), "金薤琳琅":("Jinxie linlang","jinxie-linlang"),
  "古刻叢鈔":("Guke congchao","guke-congchao"), "金石史":("Jinshi shi","jinshi-shi"),
  "吳中金石新編":("Wuzhong jinshi xinbian","wuzhong-jinshi-xinbian"), "名蹟録":("Mingji lu","mingji-lu"),
  "金石林時地考":("Jinshilin shidi kao","jinshilin-shidi-kao"), "金石文字記":("Jinshi wenzi ji","jinshi-wenzi-ji"),
  "金石文考略":("Jinshi wen kaolue","jinshi-wen-kaolue"), "來齋金石刻考畧":("Laizhai jinshike kaolue","laizhai-jinshike-kaolue"),
  "庚子銷夏記":("Gengzi xiaoxia ji","gengzi-xiaoxia-ji"), "竹雲題跋":("Zhuyun tiba","zhuyun-tiba"),
  "六藝之一錄":("Liuyi zhi yilu","liuyi-zhi-yilu"),
  # gazetteers / 字書
  "山西通志":("Shanxi tongzhi","shanxi-tongzhi"), "山東通志":("Shandong tongzhi","shandong-tongzhi"),
  "畿輔通志":("Jifu tongzhi","jifu-tongzhi"), "廣東通志":("Guangdong tongzhi","guangdong-tongzhi"),
  "河南通志":("Henan tongzhi","henan-tongzhi"), "雲南通志":("Yunnan tongzhi","yunnan-tongzhi"),
  "吳興備志":("Wuxing beizhi","wuxing-beizhi"), "會稽志":("Kuaiji zhi","kuaiji-zhi"),
  "水經注":("Shuijing zhu","shuijing-zhu"), "河朔訪古記":("Heshuo fanggu ji","heshuo-fanggu-ji"),
  "關中勝蹟圖志":("Guanzhong shengji tuzhi","guanzhong-shengji-tuzhi"), "隸辨":("Libian","libian"),
  "分隸偶存":("Fenli oucun","fenli-oucun"), "周秦刻石釋音":("Zhouqin keshi shiyin","zhouqin-keshi-shiyin"),
}
GAZ_DYN = {  # gazetteer compilation dynasty + sub-category
  "山西通志":("Qing 清","gazetteer"),"山東通志":("Qing 清","gazetteer"),"畿輔通志":("Qing 清","gazetteer"),
  "廣東通志":("Qing 清","gazetteer"),"河南通志":("Qing 清","gazetteer"),"雲南通志":("Qing 清","gazetteer"),
  "吳興備志":("Ming 明","gazetteer"),"會稽志":("Song 宋","gazetteer"),"水經注":("Northern Wei 北魏","prose"),
  "河朔訪古記":("Yuan 元","prose"),"關中勝蹟圖志":("Qing 清","prose"),
  "隸辨":("Qing 清","zishu"),"分隸偶存":("Qing 清","zishu"),"周秦刻石釋音":("Yuan 元","zishu"),
}

TITLE_DYN = {"寶刻類編":"Song 宋"}  # dynasty for anonymous / unmapped-author works

def slugify(s):
    return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")

# ── parse COVERAGE.md → {title_zh: {kr_id, count, parser}} for the 22 parsed ──
COV = {}
cov = open(os.path.join(VAULT,"COVERAGE.md"),encoding="utf-8").read()
for m in re.finditer(r"^\| *([一-鿿]+) *\| *(KR[0-9a-z]+) *\| *(\d+) *\| *([^|]+?) *\|", cov, re.M):
    COV[m.group(1)] = {"kr_id":m.group(2), "count":int(m.group(3)), "parser":m.group(4).strip().rstrip(" ⚠")}

def parse_md(path):
    raw = open(path,encoding="utf-8").read()
    fm = {}
    fmm = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    body = raw
    if fmm:
        for line in fmm.group(1).splitlines():
            mm = re.match(r"^(\w+): *(.*)$", line)
            if mm: fm[mm.group(1)] = mm.group(2).strip().strip('"')
        body = fmm.group(2)
    # excerpts: ### <name>\n<text...> under "## Content excerpts"
    excerpts = []
    ce = re.search(r"## Content excerpts.*?\n(.*?)(?:\n## |\Z)", body, re.S)
    if ce:
        for sm in re.finditer(r"### (.+?)\n(.*?)(?=\n### |\Z)", ce.group(1), re.S):
            txt = sm.group(2).strip()
            if txt: excerpts.append({"name": sm.group(1).strip(), "text": txt})
    return fm, excerpts

def norm(s):  # for 目錄 ↔ authority matching
    return re.sub(r"[\s·.,;:、，。；：（）()\[\]【】〔〕]", "", s or "")

# ── load authorities (concordance) ──────────────────────────────────────────
auth_raw = json.load(open(os.path.join(VAULT,"authorities/authorities.json"),encoding="utf-8"))
auth_list = auth_raw if isinstance(auth_raw, list) else auth_raw.get("authorities") or auth_raw.get("entries") or []
# Wikidata enrichment from authorities/pages/*.md (by title)
WD = {}
for p in glob.glob(os.path.join(VAULT,"authorities/pages/*.md")):
    fm,_ = parse_md(p)
    t = fm.get("title")
    if t:
        WD[t] = {k:fm[k] for k in ("wikidata","wikidata_url","wikipedia_zh","date_year_gregorian","is_stele") if fm.get(k)}
        if fm.get("instance_of"): WD[t]["instance_of"] = fm["instance_of"]

# sort authorities: dated first (chrono), then by attestations desc
def adate(a):
    d = a.get("date");
    try: return int(d)
    except: return 99999
auth_list.sort(key=lambda a:(adate(a), -(a.get("n_catalogs") or 0)))
authorities = []
alias_index = {}   # norm(alias) -> [authority ids]   (for 目錄 match)
by_work = {}       # work_slug -> {juan: [authority ids]}
for i,a in enumerate(auth_list):
    aid = "insc-%04d" % (i+1)
    cats = a.get("catalogs") or {}
    cat_slugs = {}
    for wt, juans in cats.items():
        info = TITLE.get(wt)
        key = info[1] if info else slugify(wt)
        cat_slugs[key] = {"title_zh": wt, "juan": juans}
        for j in (juans or []):
            by_work.setdefault(key,{}).setdefault(str(j),[]).append(aid)
    rec = {"id":aid, "main":a.get("main"), "aliases":a.get("aliases") or [], "date":a.get("date"),
           "n_catalogs":a.get("n_catalogs") or len(cats), "catalogs":cat_slugs}
    rec.update(WD.get(a.get("main"), {}))
    authorities.append(rec)
    for al in [a.get("main")] + (a.get("aliases") or []):
        alias_index.setdefault(norm(al), []).append((aid, set(str(j) for js in cats.values() for j in (js or []))))

def match_auth(work_slug, title, juan):
    cands = alias_index.get(norm(title))
    if not cands: return None
    for aid, juans in cands:
        # prefer an authority that cites THIS work at this juan
        wj = by_work.get(work_slug,{})
        if any(aid in wj.get(str(juan),[]) for _ in [0]): return aid
    return cands[0][0]

os.makedirs(os.path.join(OUT,"toc"), exist_ok=True)
works = []

# ── 22 parsed catalogues (entries/*.md + 目錄 TOC) ───────────────────────────
for md in glob.glob(os.path.join(VAULT,"entries","*《*》.md")):
    fm, excerpts = parse_md(md)
    tzh = fm.get("title_zh")
    if not tzh or tzh not in TITLE: continue
    pinyin, slug = TITLE[tzh]
    am = re.match(r"^(.*?)\s*([一-鿿]+)$", fm.get("author","").strip())
    author_en = (am.group(1).strip() if am else fm.get("author","")) or ""
    author_zh = am.group(2) if am else ""
    cov = COV.get(tzh, {})
    toc = []
    tj = os.path.join(VAULT,"entries", tzh+"-目錄-TOC.json")
    if os.path.exists(tj):
        toc = json.load(open(tj,encoding="utf-8"))
        for row in toc:
            aid = match_auth(slug, row.get("title",""), row.get("juan",""))
            if aid: row["authority"] = aid
    works.append({"id":slug,"title_zh":tzh,"title_pinyin":pinyin,"author_en":author_en,"author_zh":author_zh,
                  "dynasty":DYN.get(author_zh,"") or TITLE_DYN.get(tzh,""),"kr_id":cov.get("kr_id"),"parser":cov.get("parser"),
                  "inscriptions_count":len(toc) or int(fm.get("inscriptions_included") or 0),
                  "kind":"catalogue","has_excerpts":bool(excerpts),
                  "overlap_note":("Compendium reproducing 集古錄/金石錄/隸釋… — aggregating witness; titles overlap heavily." if tzh=="六藝之一錄" else None)})
    json.dump({"excerpts":excerpts,"inscriptions":toc}, open(os.path.join(OUT,"toc",slug+".json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)

# ── 14 gazetteers / 字書 (entries/separate/*-目錄-TOC.json) ──────────────────
for tj in glob.glob(os.path.join(VAULT,"entries","separate","*-目錄-TOC.json")):
    tzh = os.path.basename(tj).replace("-目錄-TOC.json","")
    if tzh not in TITLE: continue
    pinyin, slug = TITLE[tzh]
    dyn, cat = GAZ_DYN.get(tzh, ("",""))
    toc = json.load(open(tj,encoding="utf-8"))
    works.append({"id":slug,"title_zh":tzh,"title_pinyin":pinyin,"author_en":"","author_zh":"",
                  "dynasty":dyn,"kr_id":COV.get(tzh,{}).get("kr_id"),"parser":"gazetteer/"+cat,
                  "inscriptions_count":len(toc),"kind":"gazetteer","subcategory":cat,"has_excerpts":False,
                  "overlap_note":"Best-effort mention extraction (not a primary inscription catalogue)."})
    json.dump({"excerpts":[],"inscriptions":toc}, open(os.path.join(OUT,"toc",slug+".json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)

works.sort(key=lambda w:-w["inscriptions_count"])
meta = {"generated":"2026-06-27","source":"obsidian-vault skslxb-tei-md-dryrun (Kanripo 四庫全書 WYG+SBCK; 石刻史料新編/SKQS)",
        "license":"Kanripo open / SKQS public-domain; Wikidata CC-BY-SA (attribution); derived excerpts & translations by the Epiwen project",
        "works_count":len(works),"inscriptions_total":sum(w["inscriptions_count"] for w in works),
        "authorities_count":len(authorities),"works":works}
json.dump(meta, open(os.path.join(OUT,"works.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"generated":"2026-06-27","count":len(authorities),
           "note":"Cross-catalog inscription concordance: a canonical inscription → the 金石學 works (+juan) that record it; date (CE) where a 年號 was resolvable; Wikidata for 39 canonical steles.",
           "authorities":authorities}, open(os.path.join(OUT,"authorities.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)

open(os.path.join(OUT,"README.md"),"w",encoding="utf-8").write(
"# Epigraphic Literature (金石學) — staged data\n\n"
"Ingested from the obsidian-vault skslxb harvest (`build_literature.py`).\n\n"
"- `works.json` — %d works (22 parsed catalogues + 14 gazetteers/字書).\n"
"- `toc/<id>.json` — per-work `{excerpts, inscriptions}` (the 目錄).\n"
"- `authorities.json` — %d cross-catalog inscription concordance records (+ Wikidata for 39).\n\n"
"**Provenance / licensing:** texts from **Kanripo** (四庫全書 文淵閣 WYG + 四部叢刊 SBCK; open) and "
"**石刻史料新編 / SKQS** (public-domain); cross-catalog authorities derived by the Epiwen project; "
"**Wikidata** enrichment under CC-BY-SA (attribution required). 六藝之一錄 is an aggregating compendium "
"(its 5,258 titles overlap the other catalogues).\n" % (len(works), len(authorities)))

# ── copy app-facing files into the app repo (relative fetch) ─────────────────
shutil.copy(os.path.join(OUT,"works.json"), os.path.join(APP,"literature.json"))
shutil.copy(os.path.join(OUT,"authorities.json"), os.path.join(APP,"literature-authorities.json"))
app_toc = os.path.join(APP,"literature","toc"); os.makedirs(app_toc, exist_ok=True)
for f in glob.glob(os.path.join(OUT,"toc","*.json")): shutil.copy(f, app_toc)

linked = sum(1 for w in works for r in json.load(open(os.path.join(OUT,"toc",w["id"]+".json")))["inscriptions"] if r.get("authority"))
print("works:",len(works),"| inscriptions:",meta["inscriptions_total"],"| authorities:",len(authorities),"| 目錄 rows linked to a concordance authority:",linked)
print("catalogues:",sum(1 for w in works if w["kind"]=="catalogue"),"| gazetteers:",sum(1 for w in works if w["kind"]=="gazetteer"))
