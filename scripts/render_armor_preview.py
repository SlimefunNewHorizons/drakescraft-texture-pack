#!/usr/bin/env python3
"""Maniqui 3D (painter's algorithm) con las capas humanoid/humanoid_leggings. Uso: render_armor_preview.py out.png nombre:ruta_humanoid:ruta_leggings ..."""
import sys, math
from PIL import Image, ImageDraw
import numpy as np

# (nombre, origen UV px(64x32), tamaño wdh, centro xyz, inflado) ; y arriba, z hacia el frente(-z)
def parts(layer):
    if layer == 1:
        return [("head",(0,0),(8,8,8),(0,28,0),1.0),("body",(16,16),(8,12,4),(0,18,0),1.0),
                ("rarm",(40,16),(4,12,4),(-6,18,0),1.0),("larm",(40,16),(4,12,4),(6,18,0),1.0),
                ("rboot",(0,16),(4,12,4),(-2,6,0),1.0),("lboot",(0,16),(4,12,4),(2,6,0),1.0)]
    return [("body",(16,16),(8,12,4),(0,18,0),0.5),("rleg",(0,16),(4,12,4),(-2,6,0),0.5),("lleg",(0,16),(4,12,4),(2,6,0),0.5)]

def faces(uv, size, ctr, inf, sc):
    u,v=uv; w,h,d=size; cx,cy,cz=ctr
    W,H,D=w/2+inf,h/2+inf,d/2+inf
    # cada cara: esquinas 3D (tl,tr,br,bl) y rect UV (x,y,w,h)
    return [
     ("front",[(-W,H,-D),(W,H,-D),(W,-H,-D),(-W,-H,-D)],(u+d,v+d,w,h)),
     ("back",[(W,H,D),(-W,H,D),(-W,-H,D),(W,-H,D)],(u+d+w+d,v+d,w,h)),
     ("right",[(-W,H,D),(-W,H,-D),(-W,-H,-D),(-W,-H,D)],(u,v+d,d,h)),
     ("left",[(W,H,-D),(W,H,D),(W,-H,D),(W,-H,-D)],(u+d+w,v+d,d,h)),
     ("top",[(-W,H,D),(W,H,D),(W,H,-D),(-W,H,-D)],(u+d,v,w,d)),
     ("bottom",[(-W,-H,-D),(W,-H,-D),(W,-H,D),(-W,-H,D)],(u+d+w,v,w,d)),
    ], (cx,cy,cz)

def render(tex1, tex2, yaw, S=14, out=(380,620)):
    img=Image.new("RGBA",out,(0,0,0,0)); dr=ImageDraw.Draw(img)
    k=tex1.size[0]//64
    cy_,sy_=math.cos(yaw),math.sin(yaw); pitch=math.radians(14); cp,sp=math.cos(pitch),math.sin(pitch)
    def proj(p):
        x,y,z=p
        x,z=x*cy_+z*sy_, -x*sy_+z*cy_
        y,z=y*cp-z*sp, y*sp+z*cp
        return (out[0]/2+x*S, out[1]-40-y*S), z
    polys=[]
    for layer,tex in ((2,tex2),(1,tex1)):
        for name,uv,size,ctr,inf in parts(layer):
            fs,(cx,cy,cz)=faces(uv,size,ctr,inf,1)
            for fname,corners,(fx,fy,fw,fh) in fs:
                # profundidad media y normal
                pts=[(x+cx,y+cy,z+cz) for x,y,z in corners]
                pp=[proj(p) for p in pts]
                (a,za),(b,zb),(c,zc),(d_,zd)=pp
                cr=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
                if cr<=0: continue
                zm=(za+zb+zc+zd)/4+(0.001 if layer==2 else 0)
                polys.append((zm,pts,(fx,fy,fw,fh),tex,fname,layer))
    polys.sort(key=lambda t:-t[0])
    for zm,pts,(fx,fy,fw,fh),tex,fname,layer in polys:
        a,b,c,d_=[np.array(p,float) for p in pts]
        nx,ny=int(fw*k),int(fh*k)
        reg=tex.crop((int(fx*k),int(fy*k),int((fx+fw)*k),int((fy+fh)*k)))
        px=reg.load()
        shade={"front":1.0,"back":0.7,"right":0.8,"left":0.85,"top":1.1,"bottom":0.6}[fname]
        for j in range(ny):
            for i in range(nx):
                r,g,bb,al=px[i,j]
                if al<20: continue
                def P(s,t):
                    q=a+(b-a)*s+(d_-a)*t
                    return proj(tuple(q))[0]
                s0,s1,t0,t1=i/nx,(i+1)/nx,j/ny,(j+1)/ny
                poly=[P(s0,t0),P(s1,t0),P(s1,t1),P(s0,t1)]
                col=tuple(min(255,int(v*shade)) for v in (r,g,bb))+(255,)
                dr.polygon(poly,fill=col)
    return img

if __name__=="__main__":
    out=sys.argv[1]; items=sys.argv[2:]
    cols=[]
    for it in items:
        name,p1,p2=it.split(":")
        t1=Image.open(p1).convert("RGBA"); t2=Image.open(p2).convert("RGBA")
        views=[render(t1,t2,math.radians(y)) for y in (-35,145)]
        cols.append((name,views))
    W=Image.new("RGB",(380*2*len(cols)//1,650),(34,30,46))
    from PIL import ImageFont
    d=ImageDraw.Draw(W)
    x=0
    for name,vs in cols:
        for v in vs:
            W.paste(v,(x,30),v); x+=380
        d.text((x-760+10,6),name,fill=(255,255,255))
    W.save(out)
