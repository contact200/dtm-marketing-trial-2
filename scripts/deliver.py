#!/usr/bin/env python3
"""Optional Supabase upload + Make.com approval queue; NEVER direct publishing."""
import json
import mimetypes
import os
import sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote

import requests

def upload(base,key,bucket,filepath,keyname):
    object_path=f"generated/{keyname}/{filepath.name}"
    url=f"{base}/storage/v1/object/{quote(bucket)}/{quote(object_path,safe='/')}"
    mime=mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"
    with filepath.open("rb") as fd:
        response=requests.put(url,data=fd,timeout=180,headers={
            "apikey":key,"Authorization":f"Bearer {key}","Content-Type":mime,
            "x-upsert":"true","cache-control":"3600"
        })
    response.raise_for_status()
    public=f"{base}/storage/v1/object/public/{quote(bucket)}/{quote(object_path,safe='/')}"
    check=requests.get(public,timeout=25,stream=True)
    try:
        check.raise_for_status()
    finally:
        check.close()
    return public

def main():
    out=Path(sys.argv[1] if len(sys.argv)>1 else "outputs/latest")
    payload=json.loads((out/"payload.json").read_text(encoding="utf-8"))
    base=os.getenv("DTM_TRIAL_SUPABASE_URL","").rstrip("/")
    service=os.getenv("DTM_TRIAL_SUPABASE_SERVICE_ROLE_KEY","")
    bucket=os.getenv("DTM_TRIAL_SUPABASE_BUCKET","dtm-trial-2-public")
    webhook=os.getenv("DTM_TRIAL_MAKE_WEBHOOK_URL","")
    enabled=os.getenv("DTM_TRIAL_DELIVER_TO_MAKE","").strip().lower()=="true"
    if not enabled:
        print("Tryb podglądu. Brak wysyłki do Make.")
        return
    if not(base and service and webhook):
        print("Nie skonfigurowano wszystkich sekretów — materiały zostają jako artefakt GitHub Actions.")
        return
    if not (out/"reel.mp4").is_file():
        raise SystemExit("Brak gotowego reel.mp4")
    stamp=os.getenv("GITHUB_RUN_ID",datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"))
    name=f"{payload['date']}/{payload['campaign_id']}/{stamp}"
    video=upload(base,service,bucket,out/"reel.mp4",name)
    cover=upload(base,service,bucket,out/"cover.jpg",name)
    payload.update({
        "video_url":video,"cover_url":cover,
        "status":"pending_approval","approval_required":True,
        "source":"dtm-marketing-trial-2","event":"content_ready_for_review"
    })
    r=requests.post(webhook,json=payload,timeout=30)
    r.raise_for_status()
    (out/"delivery.json").write_text(json.dumps({
        "video_url":video,"cover_url":cover,"webhook_delivery":"success","approval_required":True
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Wysłano do Make do zatwierdzenia:",video)

if __name__=="__main__":
    main()
