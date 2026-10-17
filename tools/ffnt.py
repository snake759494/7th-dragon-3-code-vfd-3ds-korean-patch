import struct,numpy as np,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from tex import untile,tile,untile4,tile4
def read(b):
    assert b[:4]==b'FFNT'
    fi=0x14
    ftype,h,w,asc,lf,alt=struct.unpack_from('<BBBBHH',b,fi+8)
    dw=struct.unpack_from('<bBB',b,fi+16);enc=b[fi+19]
    tg,cw,cm=struct.unpack_from('<III',b,fi+20)
    t=tg-8
    cW,cH,ns,mw,ss,bl,fmt,cols,rows,sw,sh,so=struct.unpack_from('<BBBBIHHHHHHI',b,t+8)
    sheets=[b[so+i*ss:so+(i+1)*ss] for i in range(ns)]
    widths={};o=cw
    while o:
        s,e,nx=struct.unpack_from('<HHI',b,o)
        for i in range(s,e+1):widths[i]=struct.unpack_from('<bBB',b,o+8+3*(i-s))
        o=nx
    cmap={};o=cm
    while o:
        cs,ce,mt,_,nx=struct.unpack_from('<HHHHI',b,o)
        if mt==0:
            off=struct.unpack_from('<H',b,o+12)[0]
            for c in range(cs,ce+1):cmap[c]=off+c-cs
        elif mt==1:
            for c in range(cs,ce+1):
                v=struct.unpack_from('<H',b,o+12+2*(c-cs))[0]
                if v!=0xffff:cmap[c]=v
        else:
            n=struct.unpack_from('<H',b,o+12)[0]
            for k in range(n):
                c,v=struct.unpack_from('<HH',b,o+14+4*k);cmap[c]=v
        o=nx
    return dict(lf=lf,h=h,w=w,asc=asc,alt=alt,dw=dw,enc=enc,cw=cW,ch=cH,bl=bl,mw=mw,ss=ss,fmt=fmt,cols=cols,rows=rows,sw=sw,sh=sh,sheets=sheets,widths=widths,cmap=cmap,tg=t,so=so)
def images(f):
    if f['fmt']==11:return [untile4(s,f['sw'],f['sh']) for s in f['sheets']]
    if f['fmt']==8:return [untile(s,f['sw'],f['sh'],1)[:,:,0] for s in f['sheets']]
    raise Exception(f['fmt'])
