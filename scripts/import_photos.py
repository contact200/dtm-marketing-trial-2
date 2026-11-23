#!/usr/bin/env python3
"""Import ONLY owner-approved HTTPS photos; no-photo mode always works."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
CONFIG=ROOT/"config/photos.json"

def main():
    content=json.loads(CONFIG.read_text(encoding="utf-8"))
    updated=False
    (ROOT/"assets/photos").mkdir(parents=True,exist_ok=True)
    for i,rec in enumerate(content.get("photos",[])):
        if not rec.get("approved") or rec.get("file") or not rec.get("url"):
            continue
        url=rec["url"]
        parsed=urlparse(url)
        if parsed.scheme!="https" or not parsed.netloc or parsed.username or parsed.password:
            print("Pominięto niepoprawny adres HTTPS",i)
            continue
        stem=re.sub(r"[^a-zA-Z0-9_-]","-",rec.get("name") or f"foto-{i+1}")[:55]
        dest=ROOT/"assets/photos"/(stem+".jpg")
        try:
            r=requests.get(url,timeout=20,stream=True,headers={"User-Agent":"DTM-Trial/1.0"})
            r.raise_for_status()
            size=0
            with dest.open("wb") as f:
                for block in r.iter_content(65536):
                    size+=len(block)
                    if size>16*1024*1024:
                        raise ValueError("Plik przekracza 16MB")
                    f.write(block)
            with Image.open(dest) as im:
                im.verify()
            rec["file"]=str(dest.relative_to(ROOT))
            updated=True
            print("Zaimportowano:",dest.name)
        except Exception as exc:
            dest.unlink(missing_ok=True)
            print("Nie udało się pobrać zdjęcia; kontynuuję bez niego:",str(exc)[:150])
    if updated:
        CONFIG.write_text(json.dumps(content,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
