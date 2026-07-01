"""Romanization bridge: give in_skslxb works that have a title but NO 輯.冊 locator their
K&S locator, by transliterating the CJK title (pypinyin) and matching — space/syllable-
insensitively — against K&S's own romanized titles (entries.json `pinyin_title`) for the
orphan locators (K&S locators with no register work). Constrained to same 輯 + EXACT
letters-only pinyin match, so it only fills, never mis-assigns.

  <venv-with-pypinyin>/bin/python build_romanized_fills.py   →   ks-romanized-fills.json
Then build_premodern.py reads that file and assigns the locators. Needs pypinyin (pure-python;
the repo build itself does not — this is a precompute step, like k10-skslxb-analytics.json)."""
import json, re, os
from pypinyin import lazy_pinyin

HERE = os.path.dirname(os.path.abspath(__file__))
KS = "/Users/sassmann/repos/vaults/obsidian-vault/projects/AI responses/kuhn-stahl-dryrun"
APP = "/Users/sassmann/repos/GitHub/epiwen"

def letters(s): return re.sub(r"[^a-z]", "", (s or "").lower())
def norm(s): return re.sub(r"[^㐀-鿿]", "", s or "")
def py(cjk):
    core = norm(cjk); return letters("".join(lazy_pinyin(core))) if core else ""
def ktitle(pt):                                  # K&S pinyin_title → leading clean romanized run
    m = re.match(r"^([A-Za-z][A-Za-z\s]*)", pt or ""); return letters(m.group(1)) if m else ""

reg = json.load(open(APP + "/premodern.json"))["works"]
have = set(w["skslxb_locator"] for w in reg if w.get("skslxb_locator"))
# in_skslxb works WITHOUT a precise 輯.冊 locator, keyed by (輯, exact pinyin)
noloc = {}
for w in reg:
    if w["in_skslxb"] and not re.match(r"^[1-4]\.\d", (w.get("skslxb_locator") or "")):
        k = py(w.get("title_zh", ""))
        if len(k) >= 6: noloc.setdefault((w.get("skslxb_series"), k), w)
ent = [e for e in json.load(open(KS + "/entries.json")) if e.get("locator") and e["locator"] not in have]
fills = {}
for e in ent:
    w = noloc.get((e["series"], ktitle(e.get("pinyin_title", ""))))
    if w and norm(w["title_zh"]) not in fills:
        fills[norm(w["title_zh"])] = e["locator"]
json.dump({"generated": "2026-06-30", "source": "pypinyin(title) ↔ K&S entries.json pinyin_title, exact + same 輯",
           "count": len(fills), "fills": fills}, open(HERE + "/ks-romanized-fills.json", "w"), ensure_ascii=False, indent=1)
print("romanized-bridge locator fills:", len(fills))
