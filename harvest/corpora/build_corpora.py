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

# drop exact-duplicate rows (a national/site series cross-listed under a province)
seen = set(); dedup = []
for r in records:
    k = (re.sub("[^" + CJK + "]", "", r["title_zh"]), r["author"], r["year"])
    if k in seen: continue
    seen.add(k); dedup.append(r)
records = dedup

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
