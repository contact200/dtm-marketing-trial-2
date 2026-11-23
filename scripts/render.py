#!/usr/bin/env python3
"""DateTheMoment: portrait sports marketing reel generator."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
COLORS={"ink":(11,13,19),"white":(250,251,255),"blue":(36,83,231),"teal":(20,174,190),"orange":(255,138,89),"pale":(229,236,254),"slate":(91,106,137)}

def lerp(a,b,t):
    return a+(b-a)*t

def smooth(t):
    t=max(0.,min(1.,t))
    return t*t*(3.-2.*t)

def font(size:int,bold=False):
    paths = (["/usr/share/fonts/truetype/lato/Lato-Heavy.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else ["/usr/share/fonts/truetype/lato/Lato-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in paths:
        if Path(path).is_file():
            return ImageFont.truetype(path,size=max(11,int(size)))
    return ImageFont.load_default(size=max(11,int(size)))

def fit_lines(draw,text,max_width,max_lines,font_size,min_size,bold=False):
    for size in range(int(font_size),int(min_size)-1,-2):
        ft=font(size,bold);lines=[];cur=""
        for word in text.split():
            candidate=(cur+" "+word).strip()
            if draw.textbbox((0,0),candidate,font=ft)[2]<=max_width:
                cur=candidate
            else:
                if cur:lines.append(cur)
                cur=word
        if cur:lines.append(cur)
        if len(lines)<=max_lines and all(draw.textbbox((0,0),line,font=ft)[2]<=max_width for line in lines):
            return ft,lines,size
    return font(min_size,bold),[text],min_size

def fill_gradient(w,h,a,b):
    im=Image.new("RGB",(w,h));d=ImageDraw.Draw(im)
    for y in range(h):
        v=(y/max(1,h-1))**.85
        c=tuple(int(lerp(a[i],b[i],v)) for i in range(3))
        d.line([(0,y),(w,y)],fill=c,width=1)
    return im

def artwork_base(theme,w,h):
    white=COLORS["white"];blue=COLORS["blue"];ink=COLORS["ink"];teal=COLORS["teal"];orange=COLORS["orange"]
    dark=theme in ("one_match_months","media_pipeline")
    im=fill_gradient(w,h,(18,42,144),(8,14,34)) if dark else fill_gradient(w,h,white,(232,238,255))
    d=ImageDraw.Draw(im)
    if theme=="calendar_fills":
        for row in range(5):
            for col in range(7):
                x=w*(.08+col*.12);y=h*(.29+row*.083)
                active=((row*11+col*7)%9)<6
                d.rounded_rectangle((x,y,x+w*.105,y+h*.072),radius=max(5,w//85),fill=blue if active else COLORS["pale"],outline=(195,209,247),width=2)
                if active:d.line((x+w*.018,y+h*.022,x+w*.074,y+h*.022),fill=(212,225,255),width=max(2,w//230))
    elif theme=="one_match_months":
        cx,cy=w*.5,h*.48
        d.ellipse((cx-w*.16,cy-w*.095,cx+w*.16,cy+w*.095),fill=white)
        d.rounded_rectangle((cx-w*.055,cy-h*.018,cx+w*.055,cy+h*.018),radius=w//40,fill=blue)
        for j in range(18):
            a=j*math.tau/18;r=w*(.29 if j%2 else .36)
            x=cx+math.cos(a)*r;y=cy+math.sin(a)*r*1.42
            d.line((cx,cy,x,y),fill=(74,107,198),width=max(2,w//200))
            d.rounded_rectangle((x-w*.03,y-w*.03,x+w*.03,y+w*.03),radius=w//110,fill=orange if j%5==0 else (149,182,255))
    elif theme=="club_voice":
        d.rounded_rectangle((w*.09,h*.33,w*.91,h*.62),radius=w//35,fill=white,outline=(185,205,249),width=3)
        for j in range(26):
            x=w*(.135+j*.029);amp=h*(.025+abs(math.sin(j*1.31))*.10)
            d.rounded_rectangle((x,h*.47-amp/2,x+w*.013,h*.47+amp/2),radius=max(2,w//180),fill=blue if j%4 else teal)
    elif theme=="time_saved":
        cx,cy=w*.5,h*.455;r=w*.28
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=blue,width=max(8,w//50))
        for j in range(12):
            a=j*math.tau/12
            d.line((cx+math.sin(a)*r*.76,cy-math.cos(a)*r*.76,cx+math.sin(a)*r*.90,cy-math.cos(a)*r*.90),fill=ink,width=max(3,w//200))
        d.line((cx,cy,cx-w*.10,cy-h*.08),fill=ink,width=max(5,w//90))
    elif theme=="media_pipeline":
        for j,label in enumerate(["GALLERY","CAPTIONS","CALENDAR"]):
            y=h*(.29+j*.14)
            d.rounded_rectangle((w*.10,y,w*.90,y+h*.111),radius=w//34,fill=(231,239,255) if j==2 else (46,78,170),outline=(105,138,236),width=3)
            d.rounded_rectangle((w*.14,y+h*.03,w*.225,y+h*.08),radius=10,fill=orange if j==2 else teal)
            d.text((w*.26,y+h*.04),label,font=font(w*.044,True),fill=ink if j==2 else white)
            if j<2:d.line((w*.5,y+h*.11,w*.5,y+h*.14),fill=teal,width=max(5,w//145))
    elif theme=="quiet_cadence":
        for j,day in enumerate("MTWTFSS"):
            x=w*(.11+j*.112);hh=h*(.105+(j%3)*.05)
            d.rounded_rectangle((x,h*.58-hh,x+w*.076,h*.58),radius=w//35,fill=blue if j%3 else teal)
            d.text((x+w*.038,h*.61),day,font=font(w*.035,True),fill=ink,anchor="mm")
    elif theme=="moments_live_on":
        for j,(x,y) in enumerate([(.10,.32),(.36,.25),(.62,.35)]):
            xx=w*x;yy=h*y
            d.rounded_rectangle((xx,yy,xx+w*.29,yy+h*.26),radius=w//35,fill=(244,248,255),outline=blue if j==1 else (181,199,243),width=max(3,w//210))
            d.polygon([(xx+w*.03,yy+h*.21),(xx+w*.10,yy+h*.13),(xx+w*.16,yy+h*.18),(xx+w*.23,yy+h*.10),(xx+w*.26,yy+h*.21)],fill=(150,174,240))
            d.ellipse((xx+w*.18,yy+h*.063,xx+w*.23,yy+h*.093),fill=orange)
    return im

def photo_candidates():
    cfg=json.loads((ROOT/"config/photos.json").read_text(encoding="utf-8"))
    photos=[]
    for rec in cfg.get("photos",[]):
        if not rec.get("approved",False):continue
        src=rec.get("file","")
        if not src or src.startswith("/") or ".." in Path(src).parts:continue
        path=ROOT/src
        if not path.exists():continue
        try:
            with Image.open(path) as im:im.verify()
            photos.append(path)
        except Exception:pass
    return photos

def make_photo_layer(path,w,h):
    try:
        with Image.open(path) as img:
            img=ImageOps.exif_transpose(img).convert("RGB")
            img=ImageOps.fit(img,(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.5))
            return Image.blend(img,Image.new("RGB",(w,h),COLORS["ink"]),.19)
    except Exception:return None

def text_layer(base,theme,scene,campaign,brand,w,h,p,is_photo=False):
    overlay=Image.new("RGBA",(w,h));d=ImageDraw.Draw(overlay)
    dark=theme in ("one_match_months","media_pipeline") or is_photo
    fg=COLORS["white"] if dark else COLORS["ink"]
    accent=COLORS["orange"] if dark else COLORS["blue"]
    margin=int(w*.083);alpha=max(0,min(255,int(255*smooth(p/.15)*smooth((1-p)/.1))))
    if scene==0:msg=campaign["hook"];y=int(h*.15);sub="THE CONTENT STUDIO"
    elif scene==1:msg=campaign["second"];y=int(h*.704);sub=campaign["name"].upper()
    else:msg=campaign["closing"];y=int(h*.44);sub="SPORTS CONTENT. ON YOUR TERMS."
    ft,lines,sz=fit_lines(d,msg,w*.80,4,w*.086,w*.046,True)
    lh=int(sz*1.19);height=len(lines)*lh
    d.rounded_rectangle((margin-w*.025,y-sz*.33,w-margin+w*.01,y+height+sz*.94),radius=w//40,fill=(7,13,29,int(alpha*.87)) if dark else (255,255,255,int(alpha*.90)))
    d.rounded_rectangle((margin,y-sz*.17,margin+w*.085,y-sz*.105),radius=4,fill=(*accent,alpha))
    for i,line in enumerate(lines):
        dy=int((1-smooth(p/.21))*w*.05)
        d.text((margin,y+i*lh+dy),line,font=ft,fill=(*fg,alpha))
    d.text((margin,y+height+sz*.19),sub,font=font(w*.025,True),fill=(*(COLORS["pale"] if dark else COLORS["slate"]),alpha))
    d.text((margin,h*.064),"DATE THE MOMENT",font=font(w*.052,True),fill=(*fg,240))
    d.text((margin,h*.104),"THE SOCIAL CONTENT STUDIO",font=font(w*.024),fill=(*(COLORS["pale"] if dark else COLORS["slate"]),225))
    d.rounded_rectangle((margin,h*.91,margin+w*.067,h*.917),radius=3,fill=(*accent,240))
    d.text((margin,h*.937),"DATETHEMOMENT.COM",font=font(w*.029,True),fill=(*fg,235))
    return Image.alpha_composite(base.convert("RGBA"),overlay).convert("RGB")

def scene_for(t,seconds):
    x=t/seconds
    if x<.34:return 0,x/.34
    if x<.75:return 1,(x-.34)/.41
    return 2,(x-.75)/.25

def render_frame(base,campaign,brand,theme,w,h,t,seconds,photo=None):
    scene,p=scene_for(t,seconds)
    active_photo=(photo[scene] if isinstance(photo,list) else photo) if photo is not None else None
    img=(active_photo if active_photo is not None else base).copy()
    d=ImageDraw.Draw(img)
    if active_photo is None:
        progress=smooth(t/seconds)
        if theme=="calendar_fills":
            col=int(progress*6.9);row=int(t*1.7)%5
            x=w*(.08+col*.12);y=h*(.29+row*.083)
            d.rounded_rectangle((x,y,x+w*.105,y+h*.072),radius=w//85,outline=COLORS["orange"],width=max(5,w//135))
        elif theme=="club_voice":
            for j in range(7):
                x=w*(.19+j*.085);amp=h*.04*abs(math.sin(t*3+j))
                d.line((x,h*.475-amp,x,h*.475+amp),fill=COLORS["orange"],width=max(4,w//140))
        elif theme=="time_saved":
            cx,cy=w*.5,h*.455;a=t*.7;r=w*.22
            d.line((cx,cy,cx+math.sin(a)*r,cy-math.cos(a)*r),fill=COLORS["orange"],width=max(5,w//110))
        elif theme=="quiet_cadence":
            x=w*(.11+(int(t*1.7)%7)*.112)
            d.ellipse((x,h*.64,x+w*.05,h*.67),fill=COLORS["orange"])
        elif theme=="moments_live_on":
            j=int(t*1.4)%3;x=w*[.10,.36,.62][j];y=h*[.32,.25,.35][j]
            d.rounded_rectangle((x,y,x+w*.29,y+h*.26),radius=w//35,outline=COLORS["orange"],width=max(5,w//135))
        elif theme=="one_match_months":
            cx,cy=w*.5,h*.48;a=t*1.3
            x=cx+math.cos(a)*w*.31;y=cy+math.sin(a)*w*.38
            d.ellipse((x-w*.025,y-w*.025,x+w*.025,y+w*.025),fill=COLORS["orange"])
        elif theme=="media_pipeline":
            y=h*(.29+progress*.41)
            d.ellipse((w*.92,y,w*.955,y+h*.02),fill=COLORS["orange"])
    return text_layer(img,theme,scene,campaign,brand,w,h,p,active_photo is not None)

def select_campaign(campaigns,requested,date):
    byid={c["id"]:c for c in campaigns}
    if requested!="auto":
        if requested not in byid:raise SystemExit("Unknown campaign: "+requested)
        return byid[requested]
    d=dt.date.fromisoformat(date);anchor=dt.date(2026,11,23)
    week=(d-anchor).days//7
    slot={0:0,2:1,4:2}.get(d.weekday(),min(2,d.weekday()//2))
    return campaigns[(week*3+slot)%len(campaigns)]

def parse_size(value):
    try:
        w,h=(int(s) for s in value.lower().split("x"))
        if not (w>=320 and h>=540 and w<h):raise ValueError()
        return w,h
    except ValueError:
        raise argparse.ArgumentTypeError("Use 1080x1920")

def main():
    ap=argparse.ArgumentParser(description="DateTheMoment trial social marketing reels")
    ap.add_argument("--concept",default="auto")
    ap.add_argument("--date",default=dt.date.today().isoformat())
    ap.add_argument("--visual-mode",choices=["auto","motion_graphic","full_bleed_photo"],default="auto")
    ap.add_argument("--output",default="outputs/latest")
    ap.add_argument("--size",type=parse_size,default=(1080,1920))
    ap.add_argument("--fps",type=int,default=24)
    ap.add_argument("--seconds",type=float,default=13)
    ap.add_argument("--no-video",action="store_true")
    ap.add_argument("--no-audio",action="store_true")
    args=ap.parse_args()
    if not 1<=args.fps<=60 or not 2<=args.seconds<=60:ap.error("fps: 1..60, seconds: 2..60")
    w,h=args.size;out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    brand=json.loads((ROOT/"config/brand.json").read_text(encoding="utf-8"))
    campaigns=json.loads((ROOT/"config/campaigns.json").read_text(encoding="utf-8"))
    c=dict(select_campaign(campaigns,args.concept,args.date))
    bank=json.loads((ROOT/"config/copy_variations.json").read_text(encoding="utf-8"))
    day=dt.date.fromisoformat(args.date)
    cycle=((day-dt.date(2026,11,23)).days//7)*3+{0:0,2:1,4:2}.get(day.weekday(),min(2,day.weekday()//2))
    variant_index=(cycle//len(campaigns))%4 if args.concept=="auto" else (day.toordinal()//7)%4
    if variant_index:c.update(bank[c["id"]][variant_index-1])
    photos=photo_candidates()
    if args.visual_mode=="full_bleed_photo" and not photos:ap.error("full_bleed_photo requires at least one approved photo")
    visual_mode=args.visual_mode
    if visual_mode=="auto":visual_mode="full_bleed_photo" if photos and c["theme"] in ("moments_live_on","one_match_months") else "motion_graphic"
    chosen=[photos[(day.toordinal()*3+j)%len(photos)] for j in range(3)] if visual_mode=="full_bleed_photo" else []
    layers=[make_photo_layer(p,w,h) for p in chosen] if chosen else None
    if layers and any(x is None for x in layers):ap.error("Could not decode an approved photo")
    base=artwork_base(c["theme"],w,h)
    preview=render_frame(base,c,brand,c["theme"],w,h,args.seconds*.49,args.seconds,layers)
    preview.save(out/"cover.jpg",quality=91,optimize=True)
    (out/"caption.txt").write_text(c["caption"]+"\n",encoding="utf-8")
    payload={"business":brand["name"],"language":"en-US","campaign_id":c["id"],"concept_family":c["theme"],
        "visual_mode":visual_mode,"copy_variant":variant_index,"date":args.date,"caption":c["caption"],
        "website_url":brand["website"],"status":"pending_approval","approval_required":True,
        "photo_count":len(chosen),"video_file":"reel.mp4" if not args.no_video else None,
        "cover_file":"cover.jpg","source_attribution":[str(p.relative_to(ROOT)) for p in chosen] if chosen else ["original abstract motion graphics"]}
    if not args.no_video:
        audio_path=None
        if not args.no_audio:
            from audio import create_audio
            audio_path=out/"original_soundtrack.wav"
            create_audio(audio_path,args.seconds)
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
             "-s",f"{w}x{h}","-r",str(args.fps),"-i","-"]
        if audio_path:cmd+=["-i",str(audio_path)]
        cmd+=["-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p"]
        if audio_path:cmd+=["-c:a","aac","-b:a","160k","-shortest"]
        cmd+=["-movflags","+faststart",str(out/"reel.mp4")]
        print("Rendering",c["id"],visual_mode,w,h,args.fps,args.seconds,flush=True)
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for frame in range(round(args.seconds*args.fps)):
                im=render_frame(base,c,brand,c["theme"],w,h,frame/args.fps,args.seconds,layers)
                proc.stdin.write(im.tobytes())
            proc.stdin.close()
            error=proc.stderr.read().decode("utf-8",errors="replace")
            if proc.wait():raise RuntimeError("FFmpeg: "+error[-1600:])
        except (Exception,KeyboardInterrupt):
            proc.kill()
            raise
        if audio_path and audio_path.exists():audio_path.unlink()
    (out/"payload.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Ready:",out,"concept:",c["name"],"visual_mode:",visual_mode)

if __name__=="__main__":
    main()
