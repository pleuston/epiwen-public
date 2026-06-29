import sys, os, glob, json
os.environ.setdefault("GLOG_minloglevel", "3")
from paddleocr import PaddleOCR

# usage: pp_ocr_all.py <pngdir> <out.json>  → {ppn: "full OCR text"} (ppn = filename before _NNN)
pngdir, out = sys.argv[1], sys.argv[2]
ocr = PaddleOCR(lang="ch", use_textline_orientation=True,
                use_doc_orientation_classify=False, use_doc_unwarping=False)
pngs = sorted(glob.glob(pngdir + "/*.png"))
byppn = {}
for i, img in enumerate(pngs):
    ppn = os.path.basename(img).rsplit("_", 1)[0]
    texts = []
    for r in ocr.predict(input=img):
        try:
            texts += list(r["rec_texts"])
        except Exception:
            pass
    byppn.setdefault(ppn, []).append("\n".join(texts))
    if i % 20 == 0:
        print(f"{i+1}/{len(pngs)} ({ppn})", flush=True)
res = {ppn: "\n".join(pages).strip() for ppn, pages in byppn.items()}
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("DONE", len(res), "ppns,", len(pngs), "pages")
