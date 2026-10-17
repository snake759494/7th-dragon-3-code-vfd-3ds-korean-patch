import sys,os,glob
sys.path.insert(0,os.path.dirname(__file__))
import sarc,texpatch
from PIL import Image
def find(name,arcpat='cpk/ui/**/*.arc'):
    for p in sorted(glob.glob(arcpat,recursive=True)):
        d=open(p,'rb').read()
        if d[:4]!=b'SARC':continue
        for nm,s,e in sarc.parse(d):
            if nm.endswith('/'+name):yield p,nm,d[s:e]
def show(name,out,scale=2,bg=(60,60,90,255)):
    p,nm,b=next(find(name));img,f=texpatch.flim_decode(b)
    im=Image.fromarray(img,'RGBA');B=Image.new('RGBA',im.size,bg);B.alpha_composite(im)
    B.convert('RGB').resize((im.width*scale,im.height*scale),Image.NEAREST).save(out);return p,img.shape,f
if __name__=='__main__':
    print(show(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 2))
