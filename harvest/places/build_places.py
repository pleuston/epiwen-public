#!/usr/bin/env python3
"""build_places.py — SEEDER for the geographic authority register (run once).

⚠️  The XML records are now the SOURCE OF TRUTH, and this script rewrites them
    from the hardcoded table below — so re-running it would DISCARD any edit
    made in the authority editor. It refuses to run unless you pass --force.

    To rebuild the browser index after a record changes, use the derived
    builder instead (it never touches the XML):

        python3 harvest/places/build_index.py

    That is also what .github/workflows/authority-index.yml runs on push.
    Use this seeder only to add/restate places from the table below, and
    re-check the diff before committing.

Writes MADS records to  collections/epidoc-cn/authority/<id>.xml
and the browser index to collections/epidoc-cn/authority-index.json
(picked up automatically by collections.js loadSharedIndex → the Places page).

Three groups, all derived from what the corpus ACTUALLY contains — nothing
invented:

  historical  the 9 places the corpus cites by key (<placeName key="d00594">
              兗州</placeName> in SNS_3 / CLS_3 / CLS_6). These keys had NO
              authority records, so the references dangled. Ids are the
              corpus's own keys so the citations now resolve.
  site        the 6 top-level sites (province + coordinates copied verbatim
              from site-index.json). They stay first-class site records too —
              `site_id` links back to the Sites browser.
  province /  the administrative vocabulary the records use (region +
  county      settlement elements): 3 provinces, 3 counties.

Where a historical place's modern province is not securely attested it is left
EMPTY with a {verify} note — the corpus's own convention (see SNS_stele.xml).
Never guess a province or a coordinate.

Run from the repo root:  python3 harvest/places/build_places.py
"""

import json
import sys
import os

OUT_DIR = "collections/epidoc-cn/authority"
OUT_IDX = "collections/epidoc-cn/authority-index.json"

# id, zh, pinyin, en, place_type, province_zh, coordinates, date(attested), note
PLACES = [
    # ── provinces (the grouping vocabulary; from <region>) ──────────────────
    ("prov_shandong", "山東省", "Shandong Sheng", "Shandong Province",
     "province", "山東省", "", "", "Province vocabulary used by the corpus (region element)."),
    ("prov_henan", "河南省", "Henan Sheng", "Henan Province",
     "province", "河南省", "", "", "Province vocabulary used by the corpus (region element)."),
    ("prov_sichuan", "四川省", "Sichuan Sheng", "Sichuan Province",
     "province", "四川省", "", "", "Province vocabulary used by the corpus (region element)."),

    # ── counties / settlements (from <settlement>, and the SNS museum slots) ─
    ("county_anyang", "安陽縣", "Anyang Xian", "Anyang County",
     "county", "河南省", "", "", "Settlement of the LQS and XNH sites."),
    ("county_anyue", "安岳", "Anyue", "Anyue County",
     "county", "四川省", "", "", "Settlement of the WFY site."),
    ("county_wenshang", "汶上縣", "Wenshang Xian", "Wenshang County",
     "county", "山東省", "", "",
     "Current keeper of the SNS stele (汶上縣中都博物館) — see SNS_stele.xml."),

    # ── sites (province + coordinates verbatim from site-index.json) ────────
    ("SNS", "水牛山", "Shuiniushan", "Mount Shuiniu",
     "site", "山東省", "116.6635,35.7704", "", ""),
    ("CLS", "徂徠山", "Culaishan", "Mount Culai",
     "site", "山東省", "117.3938,36.0112", "", ""),
    ("HDS", "洪頂山", "Hongdingshan", "Mount Hongding",
     "site", "山東省", "116.238,36.064", "", ""),
    ("WFY", "臥佛院", "Wofoyuan", "Wofoyuan",
     "site", "四川省", "105.316629,30.302314", "", ""),
    ("LQS", "靈泉寺", "Lingquansi", "Lingquan Monastery",
     "site", "河南省", "", "", "Anyang County; no coordinates in the upstream record."),
    ("XNH", "小南海石窟", "Xiaonanhai Shiku", "Xiaonanhai Grottoes",
     "site", "河南省", "", "", "Anyang County; no coordinates in the upstream record."),

    # ── historical places cited BY KEY in the colophons ─────────────────────
    # SNS_3 colophon (公元五五八到六六一年); CLS_3 / CLS_6 (武平元年 570).
    ("d00594", "兗州", "Yanzhou", "Yanzhou Prefecture",
     "historical", "山東省", "", "558–661",
     "Cited in the SNS_3 donor colophon (邑人兗州主簿羊穆). Historical prefecture in modern Shandong."),
    ("d03707", "梁父縣", "Liangfuxian", "Liangfu County",
     "historical", "山東省", "", "570",
     "Cited in the CLS_3 / CLS_6 colophons — Wang Zichun 王子椿 held the title 冠軍將軍梁父縣令. "
     "Historical county by Mount Tai, modern Shandong."),
    ("d01587", "太山", "Taishan", "Mount Tai",
     "historical", "山東省", "", "558–661",
     "Cited in the SNS_3 colophon. 太山 = Mount Tai, modern Shandong."),
    ("dh0086", "東陽平", "Dongyangping", "Dongyangping",
     "historical", "", "", "558–661",
     "Cited in the SNS_3 colophon. {verify: modern province not securely attested — not assigned.}"),
    ("Dh0087", "義州", "Yizhou", "Yizhou Prefecture",
     "historical", "", "", "558–661",
     "Cited in the SNS_3 colophon (義州五城上郡太守). {verify: modern province not securely attested.}"),
    ("dh0088", "五城", "Wucheng", "Wucheng Commandery",
     "historical", "", "", "558–661",
     "Cited in the SNS_3 colophon (義州五城上郡太守). {verify: modern province not securely attested.}"),
    ("dh0061", "白石寺", "Baishisi", "Baishi Monastery",
     "historical", "", "", "558–661",
     "Monastery cited in the SNS_3 colophon. {verify: location not securely attested.}"),
    ("dh0062", "石窟寺", "Shikusi", "Shiku Monastery",
     "historical", "", "", "558–661",
     "Monastery cited in the SNS_3 colophon. {verify: location not securely attested.}"),
    ("dh0063", "龍華寺", "Longhuasi", "Longhua Monastery",
     "historical", "", "", "558–661",
     "Monastery cited in the SNS_3 colophon. {verify: location not securely attested.}"),
]

PROV_EN = {"山東省": "Shandong Province", "河南省": "Henan Province", "四川省": "Sichuan Province"}
SITE_IDS = {"SNS", "CLS", "HDS", "WFY", "LQS", "XNH"}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def mads(pid, zh, py, en, ptype, prov, coords, date, note):
    x = ['<?xml version="1.0" encoding="UTF-8"?>']
    x.append('<mads xmlns="http://www.loc.gov/mads/" ID="%s">' % esc(pid))
    x.append('    <authority lang="zh">')
    x.append("        <geographic>%s</geographic>" % esc(zh))
    x.append("    </authority>")
    if py:
        x.append('    <variant transliteration="pinyin">')
        x.append("        <geographic>%s</geographic>" % esc(py))
        x.append("    </variant>")
    if en and en != zh:
        x.append('    <variant lang="en" type="translation">')
        x.append("        <geographic>%s</geographic>" % esc(en))
        x.append("    </variant>")
    x.append('    <note type="place-type">%s</note>' % esc(ptype))
    if prov:
        x.append('    <note type="province">%s</note>' % esc(prov))
    if coords:
        x.append('    <note type="coordinates">%s</note>' % esc(coords))
    if date:
        x.append('    <note type="attested">%s</note>' % esc(date))
    if note:
        x.append("    <note>%s</note>" % esc(note))
    x.append("</mads>")
    return "\n".join(x) + "\n"


def main():
    if not os.path.isdir("collections/epidoc-cn"):
        raise SystemExit("run from the epiwen-data-public repo root")
    # The XML is authoritative now — re-seeding would silently discard edits
    # made in the authority editor.
    if "--force" not in sys.argv and os.path.isdir(OUT_DIR):
        raise SystemExit(
            "refusing to re-seed: %s already exists and the XML is the source of "
            "truth.\n  To rebuild only the index:  python3 harvest/places/build_index.py"
            "\n  To seed anyway (OVERWRITES records):  --force" % OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)

    index = []
    for (pid, zh, py, en, ptype, prov, coords, date, note) in PLACES:
        with open(os.path.join(OUT_DIR, pid + ".xml"), "w", encoding="utf-8") as fh:
            fh.write(mads(pid, zh, py, en, ptype, prov, coords, date, note))
        entry = {
            "id": pid,
            "display_name": ("%s %s" % (en, zh)).strip() if en else zh,
            "name_zh": zh,
            "name_pinyin": py,
            "name_type": "geographic",
            "place_type": ptype,
            "province": prov,
            "province_en": PROV_EN.get(prov, ""),
            "coordinates": coords,
            "date": date,
            "wikidata": "", "viaf": "", "gnd": "", "dila_authority": "", "cbdb": "",
        }
        if pid in SITE_IDS:
            entry["site_id"] = pid
        index.append(entry)

    index.sort(key=lambda e: (e["province"] or "￿", e["place_type"], e["id"]))
    with open(OUT_IDX, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    from collections import Counter
    print("wrote %d records → %s" % (len(index), OUT_DIR))
    print("place_type:", dict(Counter(e["place_type"] for e in index)))
    print("province  :", dict(Counter(e["province"] or "(unassigned)" for e in index)))


if __name__ == "__main__":
    main()
