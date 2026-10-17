# Korean area-title images
import sys,os,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
F={k:os.path.join(B,'NanumSquareNeo-%s.ttf'%k) for k in('bRg','cBd','dEb','eHv')}
def text_img(txt,font,size,skew=0.0):
    f=ImageFont.truetype(F[font],size)
    bb=f.getbbox(txt);w=bb[2]-bb[0]+4+int(abs(skew)*size);h=size+6
    im=Image.new('L',(w,h));d=ImageDraw.Draw(im);d.text((2-bb[0]+int(abs(skew)*size*0.5),2),txt,font=f,fill=255)
    if skew:im=im.transform(im.size,Image.AFFINE,(1,skew,-skew*h/2,0,1,0),Image.BICUBIC)
    a=np.array(im);ys,xs=np.nonzero(a>8)
    return a[ys.min():ys.max()+1,xs.min():xs.max()+1] if len(xs) else a[:1,:1]
def fit(mask,maxw):
    if mask.shape[1]<=maxw:return mask
    im=Image.fromarray(mask).resize((maxw,mask.shape[0]),Image.LANCZOS);return np.array(im)
def outline(mask,r=1):
    im=Image.fromarray(mask).filter(ImageFilter.MaxFilter(2*r+1));return np.array(im)
def dark(orig,l2,l3):
    """orig: (64,512,4) RGBA. keep rows<20 (AREA), rebuild bands 20-33 and 36-53"""
    out=orig.copy()
    H,W=orig.shape[:2]
    def band(y0,y1,txt,font,size,rmargin):
        m=text_img(txt,font,size);m=fit(m,W-40)
        o=outline(m,1);tw=m.shape[1]
        # background row profile from original band (non-text pixels)
        reg=orig[y0:y1].astype(np.int32)
        lum=reg[:,:,:3].mean(2);a=reg[:,:,3]
        bgcol=np.zeros((y1-y0,4),np.int32)
        for i in range(y1-y0):
            sel=(a[i]>0)&(lum[i]<90)
            bgcol[i]=np.median(reg[i][sel],0) if sel.sum()>3 else [0,0,0,0]
        x0=max(0,W-rmargin-tw-22)
        newreg=np.zeros_like(reg)
        for i in range(y1-y0):
            newreg[i,x0:]=bgcol[i]
            # fade-in over first 12px
            for k in range(12):
                if x0+k<W:newreg[i,x0+k,3]=bgcol[i][3]*(k+1)//13
        out[y0:y1]=newreg.astype(np.uint8)
        # paste text vertically centered
        cy=(y0+y1)//2;ty=cy-m.shape[0]//2;tx=W-rmargin-tw
        for yy in range(m.shape[0]):
            for c in (0,):pass
        sub=out[ty-1:ty-1+o.shape[0]+2,tx-1:tx-1+o.shape[1]+2]
        oo=outline(np.pad(m,1),1)/255.0;mm=np.pad(m,1)/255.0
        h_,w_=sub.shape[:2];oo=oo[:h_,:w_];mm=mm[:h_,:w_]
        s=sub.astype(np.float32)
        # outline black
        s[:,:,:3]=s[:,:,:3]*(1-oo[...,None]);s[:,:,3]=np.maximum(s[:,:,3],oo*255)
        s[:,:,:3]=s[:,:,:3]*(1-mm[...,None])+255*mm[...,None]
        out[ty-1:ty-1+h_,tx-1:tx-1+w_]=np.clip(s,0,255).astype(np.uint8)
    # right margin: from original line positions
    band(20,34,l2,'eHv',11,6)
    band(36,54,l3,'dEb',15,6)
    return out
def light(orig,l1,l2):
    H,W=orig.shape[:2]
    from collections import Counter
    bg=np.array(Counter(map(tuple,orig.reshape(-1,4))).most_common(1)[0][0],np.float32)
    fg=np.array([106,147,147,255],np.float32)
    out=np.tile(bg,(H,W,1))
    m1=fit(text_img(l1,'eHv',11,-0.2),W//2);m2=fit(text_img(l2,'eHv',15,-0.2),W-8)
    def put(m,x,y):
        a=m/255.0;h,w=a.shape;h=min(h,H-y);w=min(w,W-x);a=a[:h,:w,None]
        out[y:y+h,x:x+w]=out[y:y+h,x:x+w]*(1-a)+fg*a
    put(m1,3,max(0,6-m1.shape[0]//2));put(m2,W-6-m2.shape[1],H-2-m2.shape[0])
    return out.astype(np.uint8)
CHAPTER={'chapter_0':'태초의 한 알','chapter_1':'해신의 나라','chapter_2':'밑바닥에 켜진 불','chapter_3.6':'콜 13반!','chapter_3':'용과 검',
 'chapter_4':'얽매이지 않는 도시의 프린켑스','chapter_5.1':'각오와 각성','chapter_5':'연리의 쐐기','chapter_6':'이 꽃이 피는 때','chapter_7':'심연 136×10^8'}
def chapter(orig,txt):
    import cv2
    img=orig.copy();lum=img[:,:,:3].astype(int).min(2)
    mask=np.zeros(lum.shape,np.uint8)
    mask[124:146,20:300][lum[124:146,20:300]>150]=255
    mask=cv2.dilate(mask,np.ones((3,3),np.uint8),iterations=2)
    rgb=cv2.inpaint(np.ascontiguousarray(img[:,:,:3]),mask,5,cv2.INPAINT_TELEA)
    img[:,:,:3]=rgb
    m=fit(text_img(txt,'eHv',13),260)
    a=m/255.0;h,w=a.shape;y=128+(14-h)//2;x=31
    reg=img[y:y+h,x:x+w,:3].astype(np.float32)
    img[y:y+h,x:x+w,:3]=(reg*(1-a[...,None])+255*a[...,None]).astype(np.uint8)
    return img
