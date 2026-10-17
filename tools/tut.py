# tutorial screenshots: replace Japanese text boxes
import os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import areaimg
from PIL import Image,ImageDraw,ImageFont
SPEC={}   # file -> [(x0,y0,x1,y1,text[,align])]
def add(f,*boxes):SPEC.setdefault(f,[]).extend(boxes)
def box(img,x0,y0,x1,y1,txt,align='l',color=None):
    import cv2
    H,W=img.shape[:2];x1=min(x1,W-1);y1=min(y1,H-1)
    reg=img[y0:y1+1,x0:x1+1,:3].astype(np.int32)
    per=np.concatenate([img[max(0,y0-1),x0:x1+1,:3],img[min(H-1,y1+1),x0:x1+1,:3],img[y0:y1+1,max(0,x0-1),:3],img[y0:y1+1,min(W-1,x1+1),:3]]).astype(np.int32)
    bg=np.median(per,0)
    dist=np.abs(reg-bg).sum(2)
    txtmask=dist>60
    col=np.median(reg[dist>=np.percentile(dist,92)],0) if txtmask.any() else np.array([255,255,255])
    if color is not None:col=np.array(color)
    m=np.zeros((H,W),np.uint8);m[y0:y1+1,x0:x1+1][txtmask]=255
    m=cv2.dilate(m,np.ones((3,3),np.uint8))
    img[:,:,:3]=cv2.inpaint(np.ascontiguousarray(img[:,:,:3]),m,3,cv2.INPAINT_TELEA)
    h=y1-y0+1;w=x1-x0+1
    mm=areaimg.text_img(txt,'cBd',max(7,h))
    if mm.shape[0]>h:mm=np.array(Image.fromarray(mm).resize((max(1,mm.shape[1]*h//mm.shape[0]),h),Image.LANCZOS))
    if mm.shape[1]>w:mm=np.array(Image.fromarray(mm).resize((w,mm.shape[0]),Image.LANCZOS))
    hh,ww=mm.shape;y=y0+(h-hh)//2;x=x0 if align=='l' else (x1+1-ww if align=='r' else x0+(w-ww)//2)
    a=mm/255.0;r=img[y:y+hh,x:x+ww,:3].astype(np.float32)
    img[y:y+hh,x:x+ww,:3]=(r*(1-a[...,None])+col*a[...,None]).astype(np.uint8)
def apply(name,img):
    for b in SPEC.get(name,[]):box(img,*b)
    return img
try:
    import tutspec  # noqa: fills SPEC (edit spec, not published)
except ImportError:
    pass
