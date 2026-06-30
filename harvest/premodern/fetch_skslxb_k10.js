// Harvest the K10plus analytic cataloguing of 石刻史料新編 (SKSLXB) via the public SRU base
// opac-de-627 (keyless MARCXML):  node fetch_skslxb_k10.js  →  k10-skslxb-analytics.json
//
// Yields (a) a per-册 SBB call-number map  {"<輯>,<册>": '4"@836959-<輯>,<册>'} taken from the
// set records' MARC 924 $g (ISIL DE-1*), covering all SBB-held volumes (第一–三輯; 第四輯 not held),
// and (b) the analytic component works with CJK title (880), author, 輯 (490/830), 册 (490 $v).
// build_premodern.py looks up each SKSLXB work's call number from the map via its K&S 輯.册 locator.
const { execSync } = require("child_process"); const fs = require("fs"), path = require("path");
function sru(cql, n){ const url=`https://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=${cql}&maximumRecords=${n}&recordSchema=marcxml`;
  try { return execSync(`curl -sS --max-time 60 ${JSON.stringify(url)}`, { encoding:"utf8", maxBuffer:1<<25 }); } catch(e){ return ""; } }
function df(rec,tag){ const re=new RegExp(`<datafield tag="${tag}"[^>]*>([\\s\\S]*?)</datafield>`,"g"); const o=[]; let m; while(m=re.exec(rec)) o.push(m[1].replace(/\s+/g," ").trim()); return o; }
function s1(b,c){ const m=b.match(new RegExp(`code="${c}">([^<]*)`)); return m?m[1].trim():""; }
function l880(rec,tag){ for(const b of df(rec,"880")) if(new RegExp(`code="6">${tag}`).test(b)) return b; return ""; }
const SBB=/^DE-1[a-z]?$/, ZH="㐀-鿿豈-﫿", JIW={yi:1,er:2,san:3,si:4,"一":1,"二":2,"三":3,"四":4};
function parseJi(s){ let m=s.match(/Di\s*(\d)\s*ji/i)||s.match(/第\s*(\d)\s*[輯辑]/); if(m) return +m[1];
  m=s.match(/Di\s*(yi|er|san|si)\s*ji/i); if(m) return JIW[m[1].toLowerCase()];
  m=s.match(/第\s*([一二三四])\s*[輯辑]/); if(m) return JIW[m[1]]; return null; }
function parseCe(rec){ const v=s1(df(rec,"490")[0]||"","v")||s1(df(rec,"830")[0]||"","v"); let m=(v||"").match(/(\d{1,3})/);
  if(m) return +m[1]; m=(s1(df(rec,"830")[0]||"","p")||"").match(/[;:：]\s*(\d{1,3})/); return m?+m[1]:null; }

const x = sru(encodeURIComponent("pica.tit=石刻史料新編"), 200);
const recs = x.split(/<record[ >]/).slice(1);
function ownSBB(r){ return (df(r,"924").map(b => SBB.test(s1(b,"b")) ? s1(b,"g") : "").filter(Boolean))[0] || ""; }
const map = {};
// 第一–三輯: SBB copy on the set records, $g encodes 輯,册 (4"@836959-<輯>,<册>)
recs.forEach(r => df(r,"924").forEach(b => { if(SBB.test(s1(b,"b"))){ const m=s1(b,"g").match(/836959-(\d+),(\d+)/); if(m) map[m[1]+","+m[2]]=s1(b,"g"); } }));
const works = [];
recs.forEach(r => {
  if(/^shi ke shi liao/i.test(s1(df(r,"245")[0]||"","a"))) return;          // skip set records
  const title=s1(l880(r,"245"),"a")||s1(df(r,"245")[0]||"","a"); if(!new RegExp("["+ZH+"]").test(title)) return;
  const author=s1(l880(r,"100"),"a")||s1(df(r,"100")[0]||"","a")||s1(l880(r,"700"),"a")||"";
  const ji=parseJi(df(r,"490").join(" ")+" "+df(r,"830").join(" ")), ce=parseCe(r);
  const own=ownSBB(r);                                                       // 第四輯: SBB copy on the work record itself (5 B 81572-N)
  if(own && ji && ce) map[ji+","+ce]=map[ji+","+ce]||own;
  works.push({ ppn:(df(r,"001")[0]||"").trim(), title_zh:title, author, ji, ce, sbb_callno: own || (ji&&ce&&map[ji+","+ce]) || "" });
});
fs.writeFileSync(path.join(__dirname,"k10-skslxb-analytics.json"), JSON.stringify({
  generated:"2026-06-30", source:'K10plus SRU opac-de-627 pica.tit=石刻史料新編; SBB call number 4"@836959-<輯>,<册> from set records (ISIL DE-1*)',
  callno_map:map, count:works.length, works }, null, 1));
console.log("call-number 册:", Object.keys(map).length, "| analytic works:", works.length, "| with call no:", works.filter(w=>w.sbb_callno).length);
