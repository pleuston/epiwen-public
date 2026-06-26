# Japanese rubbing collections — systematic Japan Search survey

Japan Search (ジャパンサーチ, jpsearch.go.jp) is the **aggregator** through which
Epiwen harvests Japanese rubbings. Querying its cross-search API
(`/api/item/search/jps-cross`) for the keyword **拓本** and reading the **`db`
facet** enumerates every contributing database. As of this survey there are
**98 databases** with 拓本 content, **16,508 keyword matches** total.

> ⚠️ The count is **keyword matches** (records *mentioning* 拓本) — an upper bound.
> The actual rubbing count per database is lower; where Epiwen has already harvested
> a database, the *harvested* (genuine-rubbing) count is given.

Each database's institution + original record site come from the item `common` block
(`provider`, `linkUrl`, `contributor`). The aggregator caps pagination at `from`<2000
per query, so large databases are harvested per-`f-db`.


## A · Major rubbing collections (dedicated infrastructure)  (20)

| db code | institution | 拓本-mentions | harvested | original / dedicated site |
|---|---|--:|--:|---|
| `daito` | Daitō Bunka University — i-Repository (incl. Uno Sesson 宇野雪村文庫) 大東文化大学 i-リポジトリ | 2571 | 212 | https://www.i-repository.net/ · **rubbing DB:** https://www.daito.ac.jp/ |
| `cobas` | ColBase — National Institutes for Cultural Heritage (Tokyo/Kyoto/Nara/Kyushu National Museums) ColBase（国立文化財機構） | 2513 | 947 | https://colbase.nich.go.jp/ |
| `dignl` | National Diet Library — Digital Collections 国立国会図書館デジタルコレクション | 1152 | 494 | https://dl.ndl.go.jp/ |
| `nmj01` | National Museum of Japanese History (Rekihaku) 国立歴史民俗博物館 | 770 | — | https://www.rekihaku.ac.jp/ · **rubbing DB:** https://www.rekihaku.ac.jp/doc/t-db-index.html |
| `arc_books` | Ritsumeikan University Art Research Center — rare books (aggregates partner libraries) 立命館大学アート・リサーチセンター 古典籍 | 637 | 90 | https://www.dh-jac.net/ |
| `NarahakuBijutsuinDB` | Nara National Museum — Bukkyō Bijutsuin database 奈良国立博物館 仏教美術院データベース | 524 | — | https://www.narahaku.go.jp/ · **rubbing DB:** https://bijutsuindb.narahaku.go.jp/ |
| `tokyo` | Tokyo Metropolitan Library 東京都立図書館 | 395 | — | https://www.library.metro.tokyo.lg.jp/ · **rubbing DB:** https://archive.library.metro.tokyo.lg.jp/ |
| `nme_mocat` | National Museum of Ethnology (Minpaku) — object catalogue 国立民族学博物館 標本資料目録 | 377 | 100 | https://www.minpaku.ac.jp/ · **rubbing DB:** https://htq-fs.minpaku.ac.jp/ |
| `bibnl` | National Diet Library — NDL Search 国立国会図書館サーチ | 375 | — | https://ndlsearch.ndl.go.jp/ |
| `NagoyaCity_Museum` | Nagoya City Museum 名古屋市博物館 | 309 | — | https://www.museum.city.nagoya.jp/ |
| `fcm_db` | Fukuoka City Museum 福岡市博物館 | 305 | — | https://museum.city.fukuoka.jp/ |
| `tokyomuseumcolection` | Edo-Tokyo Museum / Tokyo Metropolitan museums collection 東京都立博物館・美術館収蔵品 | 242 | — | https://museumcollection.tokyo/ |
| `nij16` | National Institute of Japanese Literature (NIJL) 国文学研究資料館 | 213 | 120 | https://www.nijl.ac.jp/ · **rubbing DB:** https://base1.nijl.ac.jp/ |
| `arc_resource` | Ritsumeikan University Art Research Center — resources 立命館大学アート・リサーチセンター | 172 | — | https://www.dh-jac.net/ |
| `nme_lib_books` | National Museum of Ethnology (Minpaku) — library 国立民族学博物館 図書 | 124 | — | https://opac.minpaku.ac.jp/ |
| `NarahakuImageDB` | Nara National Museum — Image database 奈良国立博物館 画像データベース | 96 | — | https://imagedb.narahaku.go.jp/ |
| `utokyo_da` | University of Tokyo — Digital Archive (Kashiwa Library) 東京大学 学術資産アーカイブ | 80 | 73 | https://da.dl.itc.u-tokyo.ac.jp/ · **rubbing DB:** https://www.ioc.u-tokyo.ac.jp/database/index.html |
| `nmj02` | National Museum of Japanese History (Rekihaku) — db 02 国立歴史民俗博物館 | 44 | — | https://www.rekihaku.ac.jp/ |
| `nij01` | National Institute of Japanese Literature (NIJL) — db 01 国文学研究資料館 | 40 | — | https://base1.nijl.ac.jp/ |
| `NarahakuCollectionDB` | Nara National Museum — Collection database 奈良国立博物館 収蔵品データベース | 12 | — | https://www.narahaku.go.jp/ |

## B · University repositories  (11)

| db code | institution | 拓本-mentions | harvested | original / dedicated site |
|---|---|--:|--:|---|
| `kyudai` | Kyushu University — Collections 九州大学コレクション | 78 | — | https://catalog.lib.kyushu-u.ac.jp/ |
| `maedatosa` | Maeda Tosanokami-ke Museum (Kanazawa) 前田土佐守家資料館 | 40 | — | https://www.kanazawa-museum.jp/maeda/ |
| `ibaraki_u` | Ibaraki University Library 茨城大学図書館 | 36 | — | https://digitalcollection.lib.ibaraki.ac.jp/ |
| `cria` | Niigata University — Research Institute for Area Studies 新潟大学 | 35 | — | https://arc.human.niigata-u.ac.jp/ |
| `ryukoku` | Ryūkoku University Library 龍谷大学図書館 | 28 | — | https://da.library.ryukoku.ac.jp/ |
| `THERS_da` | Tokai National Higher Education (Nagoya University) — Digital Archive 東海国立大学機構 学術資産アーカイブ | 19 | — | https://da.adm.thers.ac.jp/ |
| `ukansai` | Kansai University — KU-ORCAS 関西大学 KU-ORCAS | 14 | — | https://www.iiif.ku-orcas.kansai-u.ac.jp/ |
| `keioobjecthub` | Keio University — Object Hub 慶應義塾 ObjectHub | 10 | — | https://objecthub.keio.ac.jp/ |
| `meiji_u` | Meiji University 明治大学 | 6 | — | https://m-archives.meiji.jp/ |
| `uryukyu` | University of the Ryukyus 琉球大学 | 2 | — | https://shimuchi.lib.u-ryukyu.ac.jp/ |
| `utokushima` | Tokushima University 徳島大学 | 2 | — | https://www.lib.tokushima-u.ac.jp/ |

## C · Museums, libraries & aggregators (mixed holdings)  (28)

| db code | institution | 拓本-mentions | harvested | original / dedicated site |
|---|---|--:|--:|---|
| `saitama_museum` | Saitama Prefectural Museum of History and Folklore (verify — high keyword noise) 埼玉県立歴史と民俗の博物館 | 4103 | — | https://saitama-rekimin.spec.ed.jp/ |
| `oitadigital_sages` | Ōita Prefectural Library — Sages historical materials 大分県立先哲史料館 | 372 | — | https://library.pref.oita.jp/ |
| `papermuseum_tokyo` | Paper Museum, Tokyo 紙の博物館 | 130 | — | https://papermuseum.jp/ |
| `kochi` | Kochi Library (Otepia) オーテピア高知図書館 | 110 | — | https://otepia.kochi.jp/ |
| `bunka` | Agency for Cultural Affairs / NII — Bunka 文化遺産オンライン | 96 | — | https://bunka.nii.ac.jp/ |
| `adeac` | ADEAC (TRC-ADEAC) digital-archive aggregator ADEAC（地域資料デジタル化） | 85 | — | https://adeac.jp/ |
| `nij10` | nihu_nij | 26 | — | https://bridge.nihu.jp |
| `syozo` | 京都国立近代美術館 | 26 | — | https://search.artmuseums.go.jp |
| `NarahakuBijutsuinDB2` | ？　？ | 22 | — | https://bijutsuindb.narahaku.go.jp |
| `okura` | libokura | 18 | — | https://id.ndl.go.jp |
| `saga` | 佐賀県立図書館 | 18 | — | https://www.sagalibdb.jp |
| `fukui` | libfukui | 15 | — | https://www.library-archives.pref.fukui.lg.jp |
| `artmuseb` | 三重県立美術館 | 14 | — | https://www.bunka.pref.mie.lg.jp |
| `ishikawa` | libishikawa | 14 | — | https://www.library.pref.ishikawa.lg.jp |
| `nij17` | nihu_nij | 14 | — | https://base1.nijl.ac.jp |
| `aokenshida_txt` | prefaomori_2019 | 13 | — | https://kenshi-archives.pref.aomori.lg.jp |
| `exhib` | nmoa | 13 | — | https://nact.jp |
| `irc01` | nihu_irc | 12 | — | https://bridge.nihu.jp |
| `najda` | naj | 12 | — | https://www.digital.archives.go.jp |
| `nme_nakanisi` | nihu_nme | 12 | — | https://htq.minpaku.ac.jp |
| `sekigahara_archive` | 関ケ原町歴史民俗学習館 | 12 | — | https://sekigahara-archive.geoa.tech |
| `arc_nishikie` | nihu_irc | 11 | — | https://www.dh-jac.net |
| `miyagi` | libmiyagi | 10 | — | https://eichi.library.pref.miyagi.jp |
| `apmoa_mapps` | apmoa | 9 | — | https://jmapps.ne.jp |
| `nme_mobib` | nihu_nme | 7 | — | https://htq-fs.minpaku.ac.jp |
| `ukobe_s` | libukobe | 6 | — | https://hdl.handle.net |
| `miemu02` | 三重県総合博物館（MieMu） | 5 | — | https://www.bunka.pref.mie.lg.jp |
| `saisei` | 室生犀星記念館 | 5 | — | https://kanazawa-mplus.jp |

## D · Long tail / likely non-rubbing noise  (39)

Codes with very few matches or non-rubbing media (video/text/prints) where 拓本 appears incidentally:

`Showa_magazine (24)`, `bunkazai_video (13)`, `NagoyaCity_Museum_hk (4)`, `nin01 (4)`, `sdcommons_npmh (4)`, `tnricp_uritate (4)`, `arc_photodb (3)`, `tdc (3)`, `bjfl (2)`, `hpmm_book (2)`, `minakata (2)`, `nme_umesaoWW (2)`, `oitacityarchive (2)`, `saitama_digi_lib (2)`, `toyama_koshibun (2)`, `ARC_maps (1)`, `Amagasaki_Digital (1)`, `SHUGYOKU2 (1)`, `Showa_video (1)`, `aichi (1)`, `aokenshida_doc (1)`, `aokenshida_lib (1)`, `aozora (1)`, `gunma (1)`, `jin (1)`, `kinpaku (1)`, `kyotogyoen_archives (1)`, `miebunkazai (1)`, `miemub (1)`, `narabook (1)`, `nij19 (1)`, `nij21 (1)`, `nij22 (1)`, `nme_ir (1)`, `nmj03 (1)`, `ojiya_dna (1)`, `rih04 (1)`, `tdc_muse (1)`, `tpada_kenmei (1)`


## Already harvested into Epiwen

`cobas` (ColBase, 947), `dignl`/`bibnl` (NDL, 494), `daito` (Daitō, 212), `nij*` (NIJL, 120),
`nme_*` (Minpaku, 100), `arc_*` (Ritsumeikan ARC, 90), `utokyo_da` (U-Tokyo, 73), plus a misc union (80).

## Notable collections newly identified by this survey

- **Nara National Museum** 奈良国立博物館 — dedicated DBs (bijutsuindb / imagedb / collectiondb), ~630 matches.
- **National Museum of Japanese History (Rekihaku)** 国立歴史民俗博物館 — ~814 matches; rubbing DB at rekihaku.ac.jp.
- **Tokyo Metropolitan Library** 東京都立図書館 — 395; TOKYO archive (archive.library.metro.tokyo.lg.jp).
- **Nagoya City Museum** 名古屋市博物館 — 309; noted Chinese calligraphy/rubbing holdings.
- **Fukuoka City Museum** 福岡市博物館 — 305.
- **Edo-Tokyo / Tokyo metropolitan museums** (museumcollection.tokyo) — 242.
- **Kyushu University** 九州大学 — 78; and university repositories: Ibaraki, Niigata, Ryūkoku, Kansai (KU-ORCAS), Keio, Meiji, Ryukyus, Tokushima.

_Generated from the Japan Search `db` facet for 拓本; counts are keyword matches (upper bound)._
