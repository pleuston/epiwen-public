import re,json,glob,os,urllib.parse
DIR="collections/rubbings"
def field(xml,pat):
    m=re.search(pat,xml,re.S); return m.group(1).strip() if m else ""
# canonical inscription rules (filename OR title), order matters (specific first)
RULES=[
 (r'Cao_Quan|曹全', "Cao Quan bei","曹全碑"),
 (r'Cuan_Baozi|爨寶子|爨宝子', "Cuan Baozi bei","爨寶子碑"),
 (r'Yi_Ying|乙瑛', "Yi Ying bei","乙瑛碑"),
 (r'Zhang_Menglong|張猛龍|Zhang_Meng_Long', "Zhang Menglong bei","張猛龍碑"),
 (r'Daji_shan|大基山|xian_tan|xian tan|Daji Shan', "Daji shan immortals-altar poem","大基山仙壇詩"),
 (r'Guan_hai|觀海|観海|Kankai|kankai', "Guan hai dao shi","觀海島詩"),
 (r'Lun_jing_shu|論經書|Ron_keisho|Ron keisho|keisho', "Lun jing shu shi","論經書詩"),
 (r'Tianzhu|天柱|Tenchu|Tenchuzan', "Tianzhu shan inscriptions","天柱山刻石"),
 (r'Zheng_Wengong|Zheng_Xi|鄭文公|鄭羲|鄭氏|熒陽|Tei_Bunko|Tei_Gi|Keiy_Tei|Tei Bunko|Tei Gi|Tei-shi', "Zheng Wengong bei","鄭文公碑"),
 (r'Yunfeng|雲峰|雲峯|Unho|Unpo|Unho_zan', "Yunfeng shan cliff inscriptions","雲峰山刻石"),
 (r'Zheng_Daozhao|鄭道昭|Tei_Dosh|Tei Dosh|daikoku|Yunju|Taiji|Fuzi_miao|chong_deng', "Zheng Daozhao — other cliff inscriptions","鄭道昭題刻"),
 (r'SNS|Shuiniushan|水牛山|Manjusri|Ma_ju', "Shuiniushan Mañjuśrī-Prajñā sutra","水牛山文殊般若經"),
 (r'Tai_Jingshiyu|JSY|經石峪|Jingshiyu|jing_shi_yu', "Mount Tai Jingshiyu Diamond Sutra","泰山經石峪金剛經"),
 (r'Jiucheng_gong|九成宮', "Jiucheng gong Liquan ming","九成宮醴泉銘"),
 (r'Duobaota|多寶塔', "Duobaota bei","多寶塔碑"),
 (r'Yanta_Shengjiao|雁塔聖教|Shengjiao', "Yanta Shengjiao xu","雁塔聖教序"),
 (r'Shimen_ming|石門銘', "Shimen ming","石門銘"),
 (r'Zhang_Qian|張遷', "Zhang Qian bei","張遷碑"),
 (r'Liqi_bei|禮器', "Liqi bei","禮器碑"),
 (r'Shichen|史晨', "Shichen bei","史晨碑"),
 (r'Cuan_Longyan|爨龍顏', "Cuan Longyan bei","爨龍顏碑"),
 (r'Yishan|嶧山', "Yishan bei","嶧山碑"),
 (r'Shiguwen|石鼓', "Shiguwen (Stone Drums)","石鼓文"),
 (r'Haodawang|好大王|Gwanggaeto', "Haodawang / Gwanggaeto stele","好大王碑"),
]
def institution(repo):
    r=repo
    if 'Harvard' in r: return ("Harvard-Yenching","1")
    if 'National Diet' in r: return ("NDL (Japan)","3")
    if 'Berkeley' in r or 'Starr' in r: return ("UC Berkeley","2")
    if 'Japan Search' in r: return ("Japan Search / Daitō Bunka","4")
    if 'ColBase' in r or 'Cultural Heritage' in r: return ("ColBase (Japan)","5")
    if 'Newfields' in r or 'Indianapolis' in r: return ("Indianapolis MA","6")
    if 'EFEO' in r: return ("EFEO (Europe)","7")
    return (r[:24] or "—","9")
groups={}
for fp in glob.glob(DIR+"/*.xml"):
    xml=open(fp,encoding="utf-8").read(); base=os.path.basename(fp)
    title=field(xml,r'<title xml:lang="en">(.*?)</title>')
    repo=field(xml,r'<repository>(.*?)</repository>')
    manifest=field(xml,r'type="iiif-manifest" target="([^"]+)"')
    rec=field(xml,r'type="(?:record|provider|source)" target="([^"]+)"')
    hay=base+" "+title
    ins=None
    for pat,en,zh in RULES:
        if re.search(pat,hay,re.I): ins=(en,zh); break
    if not ins: ins=(title or base,"")
    # short id: FHCL, or filename suffix, or record-id
    fhcl=re.search(r'FHCL:(\d+)',xml)
    sid = fhcl.group(1) if fhcl else (re.search(r'_([A-Z]{2,3}[A-Za-z0-9]+)\.xml$',base) or re.search(r'(\d{4,})',base))
    sid = fhcl.group(1) if fhcl else (sid.group(1) if sid else base[:8])
    link = ("viewer.html?manifest="+urllib.parse.quote(manifest,safe="")) if manifest else (rec or "#")
    inst,order=institution(repo)
    key=ins[0]
    g=groups.setdefault(key,{"en":ins[0],"zh":ins[1],"holds":{}})
    h=g["holds"].setdefault(inst,{"order":order,"items":[]})
    h["items"].append({"id":sid,"link":link})
# build sorted output
out=[]
for key,g in groups.items():
    holds=[]
    for inst,h in sorted(g["holds"].items(), key=lambda kv:kv[1]["order"]):
        items=sorted(h["items"], key=lambda x:str(x["id"]))
        holds.append({"institution":inst,"items":items})
    out.append({"en":g["en"],"zh":g["zh"],"count":sum(len(h["items"]) for h in holds),"holdings":holds})
out.sort(key=lambda x:-x["count"])
json.dump(out, open(DIR+"/_inscription_index.json","w"), ensure_ascii=False, indent=0)
print("inscriptions:",len(out),"| total rubbings indexed:",sum(x["count"] for x in out))
for x in out:
    insts=", ".join("%s(%d)"%(h["institution"],len(h["items"])) for h in x["holdings"])
    print("  %-42s %3d  [%s]"%((x["en"]+" "+x["zh"])[:42],x["count"],insts))
