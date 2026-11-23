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
    """White-first, spacious diagram canvas. No gradients or decorative scenery."""
    return Image.new("RGB",(w,h),COLORS["white"])

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

def clamp(value, a=0., b=1.):
    return max(a,min(b,value))

def scene_for(t,seconds):
    """Four energetic, highly readable beats over a 13-second reel."""
    x=clamp(t/seconds)
    bounds=(0.,.23,.485,.76,1.)
    for i in range(4):
        if x<bounds[i+1] or i==3:
            return i,clamp((x-bounds[i])/(bounds[i+1]-bounds[i]))
    return 3,1.

def draw_ball(d,x,y,r,color):
    width=max(2,int(r*.11))
    d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=width)
    d.line((x-r*.85,y,x+r*.85,y),fill=color,width=width)
    d.arc((x-r*.48,y-r,x+r*.48,y+r),90,270,fill=color,width=width)
    d.arc((x-r*.48,y-r,x+r*.48,y+r),270,90,fill=color,width=width)

def draw_photo_tile(d,x,y,w,h,accent=False):
    radius=max(5,int(w*.13))
    d.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=(225,235,255) if accent else (239,244,253),outline=COLORS["blue"] if accent else (202,216,243),width=max(2,int(w*.025)))
    draw_ball(d,x+w*.5,y+h*.43,min(w*.18,h*.22),COLORS["blue"])
    d.rounded_rectangle((x+w*.17,y+h*.77,x+w*.73,y+h*.815),radius=3,fill=(165,184,224))

def draw_card(d,x,y,w,h,label,active=False,bold=True):
    fill=COLORS["blue"] if active else (245,248,254)
    fg=COLORS["white"] if active else COLORS["ink"]
    d.rounded_rectangle((x,y,x+w,y+h),radius=max(9,int(w*.085)),fill=fill,outline=None if active else (216,226,246),width=max(2,int(w*.013)))
    f=font(w*.083,bold)
    bbox=d.textbbox((0,0),label,font=f)
    tw=bbox[2]-bbox[0]
    d.text((x+(w-tw)/2,y+h*.5),label,font=f,fill=fg,anchor="lm")

def draw_illustration(d,theme,scene,p,w,h):
    """Seven separate clean marketing mechanisms. Motion lives INSIDE the diagram."""
    blue=COLORS["blue"];ink=COLORS["ink"];pale=(225,235,255)
    x0,y0=w*.095,h*.39
    pw,ph=w*.81,h*.315
    progress=smooth(clamp(p*1.14))
    if theme=="calendar_fills":
        n=28
        cell=w*.096;gap=w*.014
        ox=w*.11;oy=h*.37
        for j in range(n):
            row,col=divmod(j,7)
            x=ox+col*(cell+gap);y=oy+row*(h*.078)
            filled=j<int(progress*(n+2))
            d.rounded_rectangle((x,y,x+cell,y+h*.067),radius=max(5,int(cell*.17)),fill=blue if filled else pale)
            if filled:
                d.rounded_rectangle((x+cell*.24,y+h*.026,x+cell*.72,y+h*.034),radius=3,fill=COLORS["white"])
        d.text((w*.12,h*.74),"POSTS, PLANNED.",font=font(w*.038,True),fill=blue)
    elif theme=="one_match_months":
        draw_photo_tile(d,w*.10,h*.43,w*.26,h*.215,True)
        d.line((w*.40,h*.545,w*.51,h*.545),fill=blue,width=max(4,w//130))
        d.polygon([(w*.50,h*.535),(w*.525,h*.545),(w*.50,h*.555)],fill=blue)
        count=1+int(progress*11)
        for j in range(12):
            row,col=divmod(j,4)
            x=w*(.56+col*.082);y=h*(.405+row*.085)
            d.rounded_rectangle((x,y,x+w*.066,y+h*.067),radius=max(3,w//120),fill=blue if j<count else pale)
            if j<count:d.line((x+w*.013,y+h*.022,x+w*.05,y+h*.022),fill=COLORS["white"],width=max(2,w//220))
        d.text((w*.56,h*.73),"WEEKS OF POSTS",font=font(w*.03,True),fill=blue)
    elif theme=="club_voice":
        d.rounded_rectangle((w*.115,h*.425,w*.405,h*.665),radius=w//30,fill=(239,244,253),outline=pale,width=3)
        d.rounded_rectangle((w*.155,h*.455,w*.275,h*.495),radius=w//120,fill=blue)
        d.text((w*.172,h*.462),"PDF",font=font(w*.041,True),fill=COLORS["white"])
        for j in range(4):
            yy=h*(.525+j*.027)
            d.line((w*.155,yy,w*(.35 if j%2 else .30),yy),fill=(177,193,225),width=max(3,w//180))
        d.line((w*.445,h*.55,w*.54,h*.55),fill=blue,width=max(4,w//125))
        d.polygon([(w*.525,h*.54),(w*.545,h*.55),(w*.525,h*.56)],fill=blue)
        for j,label in enumerate(("MATCH DAY","CAPTION","CLUB VOICE")):
            active=j<=int(progress*3)
            draw_card(d,w*.58,h*(.415+j*.087),w*.32,h*.068,label,active)
    elif theme=="time_saved":
        for j,label in enumerate(("PICK PHOTOS","WRITE CAPTION","PLAN POSTS","PUBLISH")):
            y=h*(.39+j*.076)
            complete=j<int(progress*5)
            d.rounded_rectangle((w*.13,y,w*.87,y+h*.06),radius=w//48,fill=(229,236,252) if not complete else blue)
            d.text((w*.19,y+h*.03),label,font=font(w*.041,True),fill=COLORS["white"] if complete else ink,anchor="lm")
            if complete:
                d.ellipse((w*.78,y+h*.019,w*.82,y+h*.046),fill=COLORS["white"])
        d.text((w*.21,h*.74),"BACKGROUND RUNNING",font=font(w*.034,True),fill=blue)
    elif theme=="media_pipeline":
        labels=("PHOTOS","CAPTIONS","SCHEDULE","POST")
        for j,label in enumerate(labels):
            active=j<=int(progress*4)
            xx=w*(.115+(j%2)*.412); yy=h*(.395+(j//2)*.166)
            draw_card(d,xx,yy,w*.358,h*.115,label,active)
        d.line((w*.47,h*.451,w*.525,h*.451),fill=blue,width=max(4,w//160))
        d.polygon([(w*.516,h*.439),(w*.536,h*.451),(w*.516,h*.463)],fill=blue)
        d.line((w*.70,h*.51,w*.70,h*.56),fill=blue,width=max(4,w//160))
        d.line((w*.47,h*.616,w*.525,h*.616),fill=blue,width=max(4,w//160))
        d.polygon([(w*.516,h*.604),(w*.536,h*.616),(w*.516,h*.628)],fill=blue)
        d.text((w*.22,h*.752),"ONE CONNECTED FLOW",font=font(w*.034,True),fill=blue)
    elif theme=="quiet_cadence":
        day_labels=("MON","TUE","WED","THU","FRI","SAT","SUN")
        for j,label in enumerate(day_labels):
            x=w*(.107+j*.113)
            d.text((x,h*.375),label,font=font(w*.025,True),fill=COLORS["slate"])
        for j in range(21):
            row,col=divmod(j,7)
            x=w*(.11+col*.113);y=h*(.413+row*.091)
            active=j<int(progress*22)
            d.rounded_rectangle((x,y,x+w*.084,y+h*.067),radius=w//60,fill=blue if active else pale)
            if active:d.ellipse((x+w*.031,y+h*.024,x+w*.053,y+h*.04),fill=COLORS["white"])
        d.rounded_rectangle((w*.12,h*.728,w*.88,h*.779),radius=w//55,fill=pale)
        d.ellipse((w*.155,h*.741,w*.184,h*.764),fill=blue)
        d.text((w*.215,h*.738),"AUTO-SCHEDULE ACTIVE",font=font(w*.036,True),fill=ink)
    elif theme=="moments_live_on":
        k=int(progress*3.9)
        for j in range(3):
            x=w*(.115+j*.225);y=h*(.425+(j%2)*.063)
            draw_photo_tile(d,x,y,w*.23,h*.175,j<k)
        d.line((w*.39,h*.685,w*.59,h*.685),fill=blue,width=max(4,w//120))
        d.polygon([(w*.576,h*.676),(w*.60,h*.685),(w*.576,h*.695)],fill=blue)
        d.rounded_rectangle((w*.665,h*.616,w*.89,h*.779),radius=w//35,fill=pale,outline=blue,width=max(3,w//150))
        d.rounded_rectangle((w*.69,h*.643,w*.864,h*.727),radius=w//70,fill=blue)
        d.line((w*.70,h*.75,w*.83,h*.75),fill=(150,173,226),width=max(2,w//185))
    else:
        draw_card(d,x0,y0,pw,ph,"SPORTS CONTENT",True)

def text_layer(base,theme,scene,campaign,brand,w,h,p,is_photo=False):
    overlay=Image.new("RGBA",(w,h),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    fg=COLORS["white"] if is_photo else COLORS["ink"]
    blue=COLORS["blue"]
    accent=COLORS["white"] if is_photo else blue
    left=int(w*.09)
    messages=(campaign["hook"],campaign["second"],campaign["third"],campaign["closing"])
    message=messages[scene]
    alpha=int(255*smooth(p/.085)*smooth((1-p)/.085))
    if scene==3:
        y=h*.31
        if not is_photo:
            d.rounded_rectangle((w*.082,h*.448,w*.918,h*.602),radius=w//22,fill=(*blue,int(alpha*.99)))
            d.text((w*.50,h*.526),"FULLY AUTOMATED",font=font(w*.059,True),fill=(255,255,255,alpha),anchor="mm")
    else:
        y=h*.178
    if is_photo:
        d.rounded_rectangle((left-w*.026,y-w*.031,w-left+w*.021,y+h*.165),radius=w//45,fill=(4,12,33,int(alpha*.83)))
    f,lines,size=fit_lines(d,message,w*.81,3,w*.088,w*.054,True)
    lineheight=int(size*1.19)
    shift=(1-smooth(p/.16))*w*.058
    for i,line in enumerate(lines):
        d.text((left,y+i*lineheight+shift),line,font=f,fill=(*fg,alpha))
    d.rounded_rectangle((left,y+len(lines)*lineheight+w*.03,left+w*.11,y+len(lines)*lineheight+w*.04),radius=3,fill=(*accent,alpha))
    d.text((left,h*.065),"DATETHEMOMENT",font=font(w*.059,True),fill=(*fg,245))
    d.text((left,h*.107),"PHOTOS / CAPTIONS / SCHEDULING / POSTS",font=font(w*.025,True),fill=(*accent,225))
    footer="BOLD.  /  RUNS IN THE BACKGROUND."
    d.text((left,h*.855),footer,font=font(w*.035,True),fill=(*fg,alpha))
    for j in range(4):
        xx=w*(.09+j*.208)
        d.rounded_rectangle((xx,h*.916,xx+w*.177,h*.923),radius=w//110,fill=(*(accent if j<=scene else fg),int(alpha if j<=scene else alpha*.18)))
    d.text((left,h*.955),"DATETHEMOMENT.COM",font=font(w*.028,True),fill=(*fg,220))
    return Image.alpha_composite(base.convert("RGBA"),overlay).convert("RGB")

def render_frame(base,campaign,brand,theme,w,h,t,seconds,photo=None):
    scene,p=scene_for(t,seconds)
    active_photo=(photo[scene%len(photo)] if isinstance(photo,list) else photo) if photo is not None else None
    img=(active_photo if active_photo is not None else base).copy()
    if active_photo is None:
        draw_illustration(ImageDraw.Draw(img),theme,scene,p,w,h)
    return text_layer(img,theme,scene,campaign,brand,w,h,p,active_photo is not None)

def select_campaign(campaigns,requested,date,sequence=None):
    byid={c["id"]:c for c in campaigns}
    if requested!="auto":
        if requested not in byid:raise SystemExit("Unknown campaign: "+requested)
        return byid[requested]
    if sequence is not None:
        return campaigns[sequence%len(campaigns)]
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
    ap.add_argument("--sequence",type=int,default=None,help="Unique GitHub run sequence; auto cycles through distinct concepts")
    ap.add_argument("--no-video",action="store_true")
    ap.add_argument("--no-audio",action="store_true")
    args=ap.parse_args()
    if not 1<=args.fps<=60 or not 2<=args.seconds<=60:ap.error("fps: 1..60, seconds: 2..60")
    w,h=args.size;out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    brand=json.loads((ROOT/"config/brand.json").read_text(encoding="utf-8"))
    campaigns=json.loads((ROOT/"config/campaigns.json").read_text(encoding="utf-8"))
    c=dict(select_campaign(campaigns,args.concept,args.date,args.sequence))
    bank=json.loads((ROOT/"config/copy_variations.json").read_text(encoding="utf-8"))
    day=dt.date.fromisoformat(args.date)
    cycle=((day-dt.date(2026,11,23)).days//7)*3+{0:0,2:1,4:2}.get(day.weekday(),min(2,day.weekday()//2))
    variant_index=((args.sequence//len(campaigns))%4 if args.sequence is not None else (cycle//len(campaigns))%4) if args.concept=="auto" else (day.toordinal()//7)%4
    if variant_index:c.update(bank[c["id"]][variant_index-1])
    photos=photo_candidates()
    if args.visual_mode=="full_bleed_photo" and not photos:ap.error("full_bleed_photo requires at least one approved photo")
    visual_mode=args.visual_mode
    if visual_mode=="auto":visual_mode="full_bleed_photo" if photos and c["theme"] in ("moments_live_on","one_match_months") else "motion_graphic"
    chosen=[photos[(day.toordinal()*4+j)%len(photos)] for j in range(4)] if visual_mode=="full_bleed_photo" else []
    layers=[make_photo_layer(p,w,h) for p in chosen] if chosen else None
    if layers and any(x is None for x in layers):ap.error("Could not decode an approved photo")
    base=artwork_base(c["theme"],w,h)
    preview=render_frame(base,c,brand,c["theme"],w,h,args.seconds*.49,args.seconds,layers)
    preview.save(out/"cover.jpg",quality=91,optimize=True)
    (out/"caption.txt").write_text(c["caption"]+"\n",encoding="utf-8")
    payload={"business":brand["name"],"language":"en-US","campaign_id":c["id"],"concept_family":c["theme"],
        "visual_mode":visual_mode,"copy_variant":variant_index,"date":args.date,"caption":c["caption"],
        "creative_angle":c["name"],"creative_hook":c["hook"],
        "on_screen_text":" | ".join((c["hook"],c["second"],c["third"],c["closing"])),
        "website_url":brand["website"],"status":"pending_approval","approval_required":True,"creative_sequence":args.sequence,
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
