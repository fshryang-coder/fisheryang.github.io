# -*- coding: utf-8 -*-
import os, zipfile, re
import xml.etree.ElementTree as ET

BASE = r"C:\Users\Ifyou\OneDrive\桌面\PhD Application\Personal Website\academic-website-materials\articles"
OUT = os.path.join(os.environ.get("TEMP", "."), "articles_txt")
os.makedirs(OUT, exist_ok=True)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def extract(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p in root.iter(W + "p"):
        texts = [t.text for t in p.iter(W + "t") if t.text]
        line = "".join(texts)
        paras.append(line)
    return "\n".join(paras)

for fn in sorted(os.listdir(BASE)):
    if not fn.endswith(".docx"):
        continue
    name = os.path.splitext(fn)[0]
    try:
        txt = extract(os.path.join(BASE, fn))
    except Exception as e:
        txt = "ERROR: " + str(e)
    outp = os.path.join(OUT, name + ".txt")
    with open(outp, "w", encoding="utf-8") as f:
        f.write(txt)
    print("=== %s : %d chars ===" % (name, len(txt)))
print("OUT DIR:", OUT)
