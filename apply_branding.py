#!/usr/bin/env python3
"""CxdElite Launcher branding script (run from repo root: python3 apply_branding.py).
Needs: pip install pillow"""
import os, re
R = "ZalithLauncher/src/main/res"
M = "ZalithLauncher/src/main"

def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        s = re.sub(a, b, s)
    open(path, "w", encoding="utf-8").write(s)

# ---- names ----
sub("ZalithLauncher/gradle.properties", [
    (r"(?m)^launcher_name=.*", "launcher_name=CxdEliteLauncher"),
    (r"(?m)^launcher_app_name=.*", "launcher_app_name=CxdElite Launcher"),
    (r"(?m)^launcher_short_name=.*", "launcher_short_name=CxdE"),
])
sub("ZalithLauncher/build.gradle.kts", [
    (r"applicationId = zalithPackageName", 'applicationId = "com.cxdelite.launcher"'),
    (r'\n\s*applicationIdSuffix = "\.v2"', ""),
])
for p in (M + "/AndroidManifest.xml", R + "/values/themes.xml", R + "/values-night/themes.xml"):
    sub(p, [(r"AppTheme\.ZalithLauncher", "AppTheme.CxdEliteLauncher")])
sub(R + "/values-pt-rBR/strings.xml", [(r"ZalithLauncher2", "CxdElite Launcher")])
sub(M + "/java/com/movtery/zalithlauncher/ui/activities/VMActivity.kt",
    [(r"ZalithLauncher: Direct gamepad", "CxdEliteLauncher: Direct gamepad")])
open("NOTICE.md", "w").write("""# CxdElite Launcher

CxdElite Launcher is a rebranded fork of Zalith Launcher 2
(https://github.com/ZalithLauncher/ZalithLauncher2) by MovTery and contributors.

Licensed under GPL-3.0 (see LICENSE). All original copyright notices are retained.
Source code must remain publicly available under the same license.
""")

# ---- logo ----
from PIL import Image, ImageDraw, ImageChops
import math, sys
SS=4
def hexpts(cx,cy,r):
    return [(cx+r*math.sin(math.radians(60*i)), cy-r*math.cos(math.radians(60*i))) for i in range(6)]
def grad(size,c1,c2):
    g=Image.new("RGBA",(size,size))
    px=g.load()
    for y in range(size):
        for x in range(size):
            t=(x+y)/(2*size-2)
            px[x,y]=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))+(255,)
    return g
def letters(d,cx,cy,s,fill):
    # "C" ring + "E" bars, total width ~ 1.9*s
    th=s*0.26
    # C
    ccx=cx-s*0.55; r=s*0.62
    d.arc([ccx-r,cy-r,ccx+r,cy+r],40,320,fill=fill,width=int(th))
    # round caps
    for a in (40,320):
        ex=ccx+(r-th/2)*math.cos(math.radians(a)); ey=cy+(r-th/2)*math.sin(math.radians(a))
        d.ellipse([ex-th/2,ey-th/2,ex+th/2,ey+th/2],fill=fill)
    # E
    ex0=cx+s*0.30; w=s*0.78; h=r*2
    d.rectangle([ex0,cy-r,ex0+th,cy+r],fill=fill)
    for yy in (cy-r, cy-th/2, cy+r-th):
        d.rectangle([ex0,yy,ex0+w,yy+th],fill=fill)
def render(size, mode, scale=1.0):
    """mode: icon (bg+logo), fg (transparent, logo only), mono (white silhouette), logo (transparent big)"""
    S=size*SS
    img=Image.new("RGBA",(S,S),(0,0,0,0))
    if mode=="icon":
        ImageDraw.Draw(img).rectangle([0,0,S,S],fill=(11,16,32,255))
    elif mode=="round":
        ImageDraw.Draw(img).ellipse([0,0,S-1,S-1],fill=(11,16,32,255))
    cx=cy=S/2; R=S*0.34*scale
    mask=Image.new("L",(S,S),0)
    md=ImageDraw.Draw(mask)
    md.polygon(hexpts(cx,cy,R),fill=255)
    if mode=="mono":
        hexl=Image.new("RGBA",(S,S),(255,255,255,255))
        img.paste(hexl,(0,0),mask)
        cut=Image.new("L",(S,S),0); letters(ImageDraw.Draw(cut),cx,cy,R*0.55,255)
        a=img.split()[3]; a=ImageChops.subtract(a,cut); img.putalpha(a)
    else:
        img.paste(grad(S,(0,229,255),(124,77,255)),(0,0),mask)
        # inner dark hex ring for depth
        inner=Image.new("L",(S,S),0)
        ImageDraw.Draw(inner).polygon(hexpts(cx,cy,R*0.86),fill=255)
        dark=Image.new("RGBA",(S,S),(11,16,32,255))
        img.paste(dark,(0,0),inner)
        ImageDraw.Draw(img).line(hexpts(cx,cy,R*0.86)+[hexpts(cx,cy,R*0.86)[0]],fill=(255,255,255,0),width=1)
        letters(ImageDraw.Draw(img),cx,cy,R*0.50,(255,255,255,255))
    return img.resize((size,size),Image.LANCZOS)

from PIL import ImageFilter
os.makedirs(R + "/drawable-nodpi", exist_ok=True)
SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

def circle(im):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, im.size[0]-1, im.size[1]-1], fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

def rounded(im, rad):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0]-1, im.size[1]-1], rad, fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

if os.path.exists("logo.png"):
    src = Image.open("logo.png").convert("RGB")
    side = min(src.size)
    src = src.crop(((src.width-side)//2, (src.height-side)//2, (src.width+side)//2, (src.height+side)//2))
    for d, s in SIZES.items():
        src.resize((s, s), Image.LANCZOS).save(f"{R}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=95)
        circle(src.resize((s*4, s*4), Image.LANCZOS)).resize((s, s), Image.LANCZOS).save(f"{R}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=95)
    # adaptive icon: blurred backdrop + full logo inside the safe zone
    C = 648
    bg = src.resize((C, C), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg.save(R + "/drawable-nodpi/ic_launcher_bg.png")
    fg = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    inner = rounded(src.resize((436, 436), Image.LANCZOS), 40)
    fg.paste(inner, ((C-436)//2, (C-436)//2), inner)
    fg.save(R + "/drawable-nodpi/ic_launcher_foreground.png")
    for f in ("ic_launcher.xml", "ic_launcher_round.xml"):
        open(f"{R}/mipmap-anydpi-v26/{f}", "w").write(
            '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@drawable/ic_launcher_bg"/>\n'
            '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n</adaptive-icon>\n')
    for f in ("ic_launcher_foreground.xml", "ic_launcher_monochrome.xml"):
        if os.path.exists(f"{R}/drawable/{f}"):
            os.remove(f"{R}/drawable/{f}")
    rounded(src.resize((1024, 1024), Image.LANCZOS), 120).save(R + "/drawable/img_launcher.png")
    print("Custom logo.png applied.")
else:
    for d, s in SIZES.items():
        render(s*2, "icon", 1.15).resize((s, s)).save(f"{R}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=95)
        render(s*2, "round", 1.0).resize((s, s)).save(f"{R}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=95)
    render(648, "fg", 1.0).save(R + "/drawable-nodpi/ic_launcher_foreground.png")
    render(648, "mono", 1.0).save(R + "/drawable-nodpi/ic_launcher_monochrome.png")
    for f in ("ic_launcher_foreground.xml", "ic_launcher_monochrome.xml"):
        if os.path.exists(f"{R}/drawable/{f}"):
            os.remove(f"{R}/drawable/{f}")
    render(1556, "fg", 1.45).crop((0, 0, 1556, 1556)).save(R + "/drawable/img_launcher.png")
    open(R + "/values/ic_launcher_background.xml", "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0B1020</color>\n</resources>\n')
print("CxdElite branding applied.")
