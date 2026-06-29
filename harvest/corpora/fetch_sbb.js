// Fetch SBB (Staatsbibliothek zu Berlin) shelf marks + online links for the SBB-held
// corpora, via the public K10plus SRU base opac-de-627 (keyless MARCXML).
//   node fetch_sbb.js   →   sbb-holdings.json   (then re-run build_corpora.py)
//
// SBB = ISIL DE-1 / DE-1a / DE-1b; Signatur = MARC 924 $g (pure-digit $a = EPN, dropped).
// Title-path matches are verified against the record's CJK title (MARC 880, S/T-folded via
// t2s-charmap.json) OR the romanized title (MARC 245) via pinyin (titles-pinyin.json),
// so a homonym title cannot inject the wrong work's shelf mark.
// titles-pinyin.json is regenerated with the scratchpad venv:
//   from pypinyin import lazy_pinyin  (over the SBB titles' CJK core)
const fs = require("fs"), path = require("path");
const { execSync } = require("child_process");
const HERE = __dirname;
const APP_CORPORA = "/Users/sassmann/repos/GitHub/epiwen/modern-corpora.json";

const SBB = /^DE-1[a-z]?$/; // DE-1, DE-1a, DE-1b — NOT DE-15, DE-101, DE-11 …
const CJK = "㐀-鿿豈-﫿";
const MAP = JSON.parse(fs.readFileSync(path.join(HERE, "t2s-charmap.json"), "utf8"));
const PIN = JSON.parse(fs.readFileSync(path.join(HERE, "titles-pinyin.json"), "utf8"));
const t2s = s => s.replace(new RegExp("[" + CJK + "]", "g"), c => MAP[c] || c);
const strip = s => (s || "").replace(/[（(【\[][^）)】\]]*[）)】\]]/g, "");
const core = s => t2s(strip(s).replace(new RegExp("[^" + CJK + "]", "g"), ""));
function titlesMatch(a, b) { a = core(a); b = core(b); if (!a || !b) return false;
  return a === b || (b.startsWith(a) && b.length - a.length <= 4) || (a.startsWith(b) && a.length - b.length <= 4); }
function pinMatch(p, r) { if (!p || !r || p.length < 6 || r.length < 6) return false;
  const [s, l] = p.length <= r.length ? [p, r] : [r, p]; return l === s || (l.startsWith(s) && l.length - s.length <= 6); }

const d = JSON.parse(fs.readFileSync(APP_CORPORA, "utf8")).corpora;
const targets = d.filter(x => x.holdings && x.holdings.sbb === true)
                 .map(x => ({ id: x.id, isbn: (x.isbn && x.isbn[0]) || "", title: x.title_zh || "" }));

function sru(cql, max) {
  const url = `https://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=${cql}&maximumRecords=${max}&recordSchema=marcxml`;
  try { return execSync(`curl -sS --max-time 40 ${JSON.stringify(url)}`, { encoding: "utf8", maxBuffer: 1 << 24 }); }
  catch (e) { return ""; }
}
function parse(xml) {
  if (!xml || /<diag:message>/.test(xml)) return [];
  return xml.split(/<record[ >]/).slice(1).map(r => {
    const ppn = (r.match(/tag="001">([^<]+)/) || [])[1] || "";
    let ctitle = ""; const re880 = /<datafield tag="880"[^>]*>([\s\S]*?)<\/datafield>/g; let m8;
    while ((m8 = re880.exec(r))) { const b = m8[1]; if (/code="6">245/.test(b)) { ctitle = ((b.match(/code="a">([^<]+)/) || [])[1] || "") + ((b.match(/code="b">([^<]+)/) || [])[1] || ""); break; } }
    const rtitle = (((r.match(/<datafield tag="245"[\s\S]*?<\/datafield>/) || [""])[0].match(/code="a">([^<]+)/) || [])[1] || "").toLowerCase().replace(/[^a-z]/g, "");
    const sig = []; const re = /<datafield tag="924"[^>]*>([\s\S]*?)<\/datafield>/g; let m;
    while ((m = re.exec(r))) { const b = m[1]; const isil = (b.match(/code="b">([^<]+)/) || [])[1] || "";
      if (SBB.test(isil)) { const s = (b.match(/code="g">([^<]+)/) || [])[1]; if (s && !/^\d+$/.test(s.trim())) sig.push(s.trim()); } }
    const online = []; const oe = /<datafield tag="856"[^>]*>([\s\S]*?)<\/datafield>/g; let o;
    while ((o = oe.exec(r))) { const u = (o[1].match(/code="u">([^<]+)/) || [])[1]; if (u && /sbb|spk|staatsbib|digital/i.test(u)) online.push(u.trim()); }
    return { ppn, sig, online, ctitle, rtitle };
  });
}

const out = {}; let nSig = 0, nOnline = 0;
targets.forEach(t => {
  let recs = [], match = "none";
  if (t.isbn) { recs = parse(sru("pica.isb%3D" + encodeURIComponent(t.isbn), 3)).filter(r => r.sig.length); if (recs.length) match = "isbn"; }
  if (!recs.length && t.title) { recs = parse(sru("pica.tit%3D" + encodeURIComponent(t.title), 10)).filter(r => r.sig.length && (titlesMatch(t.title, r.ctitle) || pinMatch(PIN[t.id], r.rtitle))); if (recs.length) match = "title"; }
  const signatur = [...new Set([].concat(...recs.map(r => r.sig)))];
  out[t.id] = { match, ppn: [...new Set(recs.map(r => r.ppn).filter(Boolean))], signatur, online: [...new Set([].concat(...recs.map(r => r.online)))] };
  if (signatur.length) nSig++; if (out[t.id].online.length) nOnline++;
});
fs.writeFileSync(path.join(HERE, "sbb-holdings.json"),
  JSON.stringify({ generated: "2026-06-29", source: "K10plus SRU opac-de-627; SBB = ISIL DE-1/DE-1a/DE-1b (MARC 924 $g); title matches verified vs MARC 880 CJK / 245 pinyin", count: targets.length, with_signatur: nSig, with_online: nOnline, holdings: out }, null, 1));
console.log(`DONE: ${targets.length} SBB-held | with Signatur: ${nSig} | with online: ${nOnline}`);
