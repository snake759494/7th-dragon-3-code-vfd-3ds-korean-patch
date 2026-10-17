# Japanese text images inside layout arcs -> Korean
import os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import texpatch,areaimg
from PIL import Image,ImageDraw,ImageFont
def draw(img,x0,y0,x1,y1,txt,size=11,font='cBd',color=(255,255,255),align='l',erase=True):
    if erase:img[y0:y1+1,x0:x1+1]=0
    m=areaimg.fit(areaimg.text_img(txt,font,size),x1-x0+1)
    h,w=m.shape;y=y0+max(0,((y1-y0+1)-h)//2);x=x0 if align=='l' else (x1+1-w if align=='r' else x0+((x1-x0+1)-w)//2)
    h=min(h,img.shape[0]-y);a=m[:h]/255.0
    reg=img[y:y+h,x:x+w].astype(np.float32)
    reg[:,:,:3]=reg[:,:,:3]*(1-a[...,None])+np.array(color)*a[...,None];reg[:,:,3]=np.maximum(reg[:,:,3],a*255)
    img[y:y+h,x:x+w]=reg.astype(np.uint8)
def caution(img):
    W=img[:240,:400]
    W[:,:,:3]=255;W[:,:,3]=255
    lines=['<주의>','게임 소프트를 권리자의 허락 없이 인터넷을','통해 배포·전송하는 행위, 또한 불법 인터넷','배포임을 알면서 다운로드하는 행위는','법률로 엄격히 금지되어 있습니다.','여러분의 이해와 협조를 부탁드립니다.']
    f=ImageFont.truetype(areaimg.F['bRg'],14)
    im=Image.fromarray(np.ascontiguousarray(W),'RGBA');d=ImageDraw.Draw(im)
    y=38
    for i,l in enumerate(lines):
        w=d.textlength(l,font=f);x=(400-w)/2 if i==0 else 54
        d.text((x,y),l,font=f,fill=(0,0,0,255));y+=25
    img[:240,:400]=np.array(im)
def patch(arc,nm,b):
    base=os.path.basename(nm)
    if base=='txt_help.bflim':
        img,f=texpatch.flim_decode(b)
        draw(img,64,1,127,12,'사용');draw(img,64,15,127,26,'버리기');draw(img,64,28,127,40,'장비 해제')
    elif base=='txt_floor.bflim':
        img,f=texpatch.flim_decode(b)
        draw(img,32,0,63,13,'본관');draw(img,32,15,63,28,'별관');draw(img,32,30,63,44,'동관')
    elif base=='txt_world.bflim':
        img,f=texpatch.flim_decode(b)
        draw(img,120,0,190,13,'도쿄');draw(img,54,13,190,27,'아틀란티스 해양왕국');draw(img,98,28,190,41,'에덴')
    elif base=='txt_caution.bflim':
        img,f=texpatch.flim_decode(b);caution(img)
    elif base=='areatitle_t_tbs_00.bflim':
        img,f=texpatch.flim_decode(b);img=areaimg.dark(img,'노덴스 엔터프라이즈','정문 앞 광장')
    elif base=='ic_jobsp.bflim':
        img,f=texpatch.flim_decode(b)
        for x0,x1,t in((12,36,'발도'),(48,72,'거합'),(84,108,'쌍검')):
            reg=img[0:12,x0:x1];bg=np.median(reg[reg[:,:,:3].min(2)<150],0).astype(np.uint8);img[0:12,x0:x1]=bg
            draw(img,x0,0,x1-1,11,t,size=11,font='eHv',align='c',erase=False)
    elif base=='next_charge.bflim':
        img,f=texpatch.flim_decode(b);draw(img,0,1,19,12,'남은',size=11,font='eHv')
    elif base.startswith('trial_') and base in __import__('tut').SPEC:
        img,f=texpatch.flim_decode(b);img=__import__('tut').apply(base,img)
    elif base in LOGO:
        img,f=texpatch.flim_decode(b);img=logo(img,*LOGO[base],trial='trial' in base)
    else:return None
    nb=texpatch.flim_encode(b,img)
    return nb+b[len(nb):]
LOGO={'title_rogo.bflim':(117,126),'title_rogo_trial.bflim':(103,111),'rogoset.bflim':(110,119)}
def logo(img,y0,y1,trial=False):
    import cv2
    r,g,b,a=[img[:,:,i].astype(int) for i in range(4)]
    m=np.zeros(r.shape,bool);m[y0:y1+1,120:300]=True
    teal=m&(g-r>25)&(a>60)
    col=np.median(img[teal][:,:3],0) if teal.sum() else np.array([40,150,140])
    mk=cv2.dilate(teal.astype(np.uint8)*255,np.ones((3,3),np.uint8))
    rgb=cv2.inpaint(np.ascontiguousarray(img[:,:,:3]),mk,3,cv2.INPAINT_TELEA)
    al=cv2.inpaint(np.ascontiguousarray(img[:,:,3]),mk,3,cv2.INPAINT_TELEA)
    img[:,:,:3]=rgb;img[:,:,3]=al
    xs=np.nonzero(teal.any(0))[0];x0,x1=(xs.min(),xs.max()) if len(xs) else (145,270)
    chars=list('세븐스드래곤·Ⅲ');n=len(chars);hh=y1-y0+1
    for i,ch in enumerate(chars):
        mm=areaimg.text_img(ch,'eHv',hh+1)
        if mm.shape[0]>hh:mm=np.array(Image.fromarray(mm).resize((max(1,mm.shape[1]*hh//mm.shape[0]),hh),Image.LANCZOS))
        h,w=mm.shape;cx=x0+(x1-x0)*i/(n-1);x=int(round(cx-w/2));y=y0+(hh-h)//2;aa=mm/255.0
        x=max(0,min(x,img.shape[1]-w))
        reg=img[y:y+h,x:x+w].astype(np.float32)
        reg[:,:,:3]=reg[:,:,:3]*(1-aa[...,None])+col*aa[...,None];reg[:,:,3]=np.maximum(reg[:,:,3],aa*255)
        img[y:y+h,x:x+w]=reg.astype(np.uint8)
    if trial:
        reg=img[131:166,140:270];vis=reg[:,:,3]>30
        ys,xs2=np.nonzero(vis)
        if len(ys):
            c2=np.median(reg[vis&(reg[:,:,:3].astype(int).mean(2)<120)][:,:3],0)
            yy0,yy1,xx0,xx1=ys.min()+131,ys.max()+131,xs2.min()+140,xs2.max()+140
            img[131:166,140:270]=0
            draw(img,xx0-4,yy0,xx1+4,yy1,'체험판',size=(yy1-yy0)+3,font='eHv',color=tuple(int(v) for v in c2),align='c',erase=False)
    return img
