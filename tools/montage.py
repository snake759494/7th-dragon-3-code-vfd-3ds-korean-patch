import sys,os,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import texpatch,sarc
from PIL import Image,ImageDraw
def load(p):
    d=open(p,'rb').read()
    if d[:4]==b'SARC':
        return [(p+':'+nm,d[s:e]) for nm,s,e in sarc.parse(d) if nm.endswith('.bflim')]
    return [(p,d)]
def sheet(items,out,maxw=200):
    ims=[]
    for k,b in items:
        try:img,fmt=texpatch.flim_decode(b)
        except Exception as e:continue
        im=Image.fromarray(img,'RGBA');bg=Image.new('RGBA',im.size,(60,60,90,255));bg.alpha_composite(im);im=bg.convert('RGB')
        if im.width>maxw:im=im.resize((maxw,max(1,im.height*maxw//im.width)))
        ims.append((k,im))
    W=1000;x=y=0;rh=0;pos=[]
    for k,im in ims:
        if x+im.width>W:x=0;y+=rh+14;rh=0
        pos.append((x,y));x+=im.width+6;rh=max(rh,im.height)
    H=y+rh+14;S=Image.new('RGB',(W,max(H,10)),(255,255,255));D=ImageDraw.Draw(S)
    for (k,im),(x,y) in zip(ims,pos):S.paste(im,(x,y+12));D.text((x,y),os.path.basename(k)[-28:],fill=(255,0,0))
    S.save(out);return len(ims)
if __name__=='__main__':
    items=[]
    for g in sys.argv[2:]:
        for p in sorted(glob.glob(g)):items+=load(p)
    print(sheet(items,sys.argv[1]))
