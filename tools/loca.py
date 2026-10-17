# location title cards: parse bflyt panes, render composite, write back Korean composite into textures
import struct,sys,os,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import sarc,texpatch
from PIL import Image
def parse(b):
    hl=struct.unpack_from('<H',b,6)[0];n=struct.unpack_from('<H',b,0x10)[0];o=hl
    texs=[];mats=[];panes=[];stack=[];last=None
    for i in range(n):
        mg=b[o:o+4];sz=struct.unpack_from('<I',b,o+4)[0]
        if mg==b'txl1':
            c=struct.unpack_from('<I',b,o+8)[0]
            for k in range(c):
                no=struct.unpack_from('<I',b,o+12+4*k)[0];texs.append(b[o+12+no:].split(b'\0')[0].decode())
        elif mg==b'mat1':
            c=struct.unpack_from('<I',b,o+8)[0]
            for k in range(c):
                mo=o+struct.unpack_from('<I',b,o+12+4*k)[0]
                fl=struct.unpack_from('<I',b,mo+0x24)[0]
                mats.append(struct.unpack_from('<H',b,mo+0x28)[0] if fl&3 else None)
        elif mg in(b'pan1',b'pic1',b'txt1',b'wnd1',b'bnd1'):
            name=b[o+0xc:o+0x24].split(b'\0')[0].decode()
            fl,bp,al,ps=b[o+8],b[o+9],b[o+10],b[o+11]
            tx,ty,tz=struct.unpack_from('<3f',b,o+0x2c);rx,ry,rz=struct.unpack_from('<3f',b,o+0x38)
            sx,sy=struct.unpack_from('<2f',b,o+0x44);w,h=struct.unpack_from('<2f',b,o+0x4c)
            p=dict(name=name,kind=mg.decode(),off=o,bp=bp,t=(tx,ty),r=rz,s=(sx,sy),size=(w,h),parent=stack[-1] if stack else None,vis=fl&1)
            if mg==b'pic1':
                p['mat']=struct.unpack_from('<H',b,o+0x64)[0];nc=b[o+0x66]
                p['uv']=[struct.unpack_from('<8f',b,o+0x68+32*k) for k in range(nc)]
            panes.append(p);last=len(panes)-1
        elif mg==b'pas1':stack.append(last)
        elif mg==b'pae1':stack.pop()
        o+=sz
    return texs,mats,panes
def world(panes,i):
    """returns center x,y (y up), total scale"""
    p=panes[i];x,y=p['t'];sx,sy=p['s']
    if p['parent'] is not None:
        px,py,psx,psy=world(panes,p['parent'])
        pp=panes[p['parent']];pw,ph=pp['size']
        # origin offset for basePos relative to parent (parentRelative bits ignored)
        x=px+x*psx;y=py+y*psy;sx*=psx;sy*=psy
    # basePos: bits0-1 x origin(0 center,1 left,2 right), bits2-3 y origin(0 center,1 top,2 bottom)
    w,h=p['size'];bx=p['bp']&3;by=(p['bp']>>2)&3
    cx=x+(w*sx/2 if bx==1 else -w*sx/2 if bx==2 else 0);cy=y+(-h*sy/2 if by==1 else h*sy/2 if by==2 else 0)
    return (cx if p['kind'] else x,cy,sx,sy) if False else (x,y,sx,sy)
def rect(panes,i):
    x,y,sx,sy=world(panes,i);p=panes[i];w,h=p['size']
    bx=p['bp']&3;by=(p['bp']>>2)&3
    W,H=w*abs(sx),h*abs(sy)
    x0=x-W/2 if bx==0 else x if bx==1 else x-W
    y1=y+H/2 if by==0 else y if by==1 else y+H
    return x0,y1-H,W,H   # x0, ybottom (y up), w, h
def load(arcpath):
    d=open(arcpath,'rb').read();files={}
    for nm,s,e in sarc.parse(d):files[os.path.basename(nm)]=(nm,s,e)
    lay=[v for k,v in files.items() if k.endswith('.bflyt')][0]
    texs,mats,panes=parse(d[lay[1]:lay[2]])
    imgs={}
    for t in texs:
        if t in files:
            nm,s,e=files[t];imgs[t]=texpatch.flim_decode(d[s:e])[0]
    return d,files,texs,mats,panes,imgs
def pieces(arcpath,pred=lambda t:'loca_ti' in t or 'loca_kana' in t):
    d,files,texs,mats,panes,imgs=load(arcpath);out=[]
    for i,p in enumerate(panes):
        if p['kind']!='pic1' or not p['uv']:continue
        ti=mats[p['mat']]
        if ti is None:continue
        t=texs[ti]
        if not pred(t):continue
        u=p['uv'][0];us=[u[0],u[2],u[4],u[6]];vs=[u[1],u[3],u[5],u[7]]
        out.append(dict(i=i,name=p['name'],tex=t,rect=rect(panes,i),uv=(min(us),min(vs),max(us),max(vs)),flipx=u[0]>u[2],flipy=u[1]>u[5],r=p['r']))
    return d,files,texs,imgs,out
def uvpix(img,uv):
    H,W=img.shape[:2];u0,v0,u1,v1=uv
    # texture v: 0 = top in decoded orientation? decoded images are top-down; flim v origin bottom -> v=1 top
    return int(round(u0*W)),int(round(v0*H)),int(round(u1*W)),int(round(v1*H))
def composite(arcpath,scale=1):
    d,files,texs,imgs,P=pieces(arcpath)
    xs=[p['rect'][0] for p in P]+[p['rect'][0]+p['rect'][2] for p in P];ys=[p['rect'][1] for p in P]+[p['rect'][1]+p['rect'][3] for p in P]
    X0,X1,Y0,Y1=min(xs),max(xs),min(ys),max(ys)
    Wc,Hc=int(X1-X0)+2,int(Y1-Y0)+2
    can=Image.new('RGBA',(Wc*scale,Hc*scale),(40,40,70,255))
    for p in P:
        img=imgs[p['tex']];x0,y0,x1,y1=uvpix(img,p['uv'])
        if x1<=x0 or y1<=y0:continue
        sub=Image.fromarray(img[y0:y1,x0:x1],'RGBA')
        if p['flipx']:sub=sub.transpose(Image.FLIP_LEFT_RIGHT)
        if p['flipy']:sub=sub.transpose(Image.FLIP_TOP_BOTTOM)
        rx,ry,rw,rh=p['rect'];sub=sub.resize((max(1,int(rw*scale)),max(1,int(rh*scale))))
        can.alpha_composite(sub,(int((rx-X0)*scale),int((Y1-(ry+rh))*scale)))
    return can,(X0,Y0,X1,Y1),P
if __name__=='__main__':
    for a in sys.argv[1:]:
        c,bb,P=composite(a,2);c.save(os.path.join('img','comp_'+os.path.basename(a)+'.png'))
        print(a,bb,[(p['name'],p['tex'],[round(v) for v in p['rect']],p['uv'],round(p['r'])) for p in P])
from PIL import ImageDraw,ImageFont,ImageFilter
GAME=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
KO={
 'abs':('그레이트풀 세븐스',{'loca_ti_abs_f':'풀','loca_ti_abs_g':'그레이트','loca_ti_abs':'세븐스'}),
 'atb':('수도 아틀란티카',{'loca_ti_atb_s':'수','loca_ti_atb_t':'도','loca_ti_atb':'아틀란티카'}),
 'atl':('베르크 해양궁전',{'loca_ti_atl_b':'베','loca_ti_atl_l':'르크','loca_ti_atl':'해양궁전'}),
 'cld':('저층구 클라디온',{'loca_ti_cld_t2':'저','loca_ti_cld_t':'층구','loca_ti_cld':'클라디온'}),
 'crm':('홍항의 탑',{'loca_ti_crm_k':'홍','loca_ti_crm_k2':'항','loca_ti_crm_n':'의','loca_ti_crm':'탑'}),
 'ges':('도쿄 지하도',{'loca_ti_ges_t':'도쿄','loca_ti_ges_c':'지','loca_ti_ges':'하도'}),
 'gzd':('특별지정사적 국회의사당',{'loca_ti_gzd_t':'특별','loca_ti_gzd_s':'지정\n사적','loca_ti_gzd_k':'국','loca_ti_gzd':'회의사당'}),
 'hpb':('카잔 공화국',{'loca_ti_hpb_k':'카','loca_ti_hpb_z':'잔','loca_ti_hpb':'공화국'}),
 'plr':('학도 플레로마',{'loca_ti_plr_g':'학도','loca_ti_plr':'플레','loca_ti_plr_r':'로마'}),
 'tbs':('노덴스 엔터프라이즈',{'loca_ti_tbs_n':'노','loca_ti_bts_dn':'덴','loca_ti_tbs_s':'스','loca_ti_tbs_d':'·','loca_ti_tbs':'엔터프라이즈'}),
 'tra':('서기 2021년 도쿄 스카이타워',{'loca_ti_d':'서기','loca_ti_y':'년','loca_ti_tra_t':'도쿄','loca_ti_tra':'스카이타워'}),
 'urd':('환영수도·그림자',{'loca_ti_urd':'환','loca_ti_a_00':'영','loca_ti_a_01':'수','loca_ti_a_02':'도','loca_ti_a_03':'·','loca_ti_a_04':'그림자',
        'loca_ti_urd_g':'환','loca_ti_urd_e':'영','loca_ti_urd_s':'수','loca_ti_urd_t':'도','loca_ti_urd_s_0':'·','loca_ti_urd_s_k':'그림자'}),
}
def _mask(txt,W,H,font):
    W=max(1,W);H=max(1,H);S=4
    vertical=(H>W*1.3 and len(txt.replace('\n',''))>1) or '\n' in txt
    if '\n' in txt:lines=txt.split('\n')
    elif vertical:lines=list(txt)
    else:lines=[txt]
    big=Image.new('L',(W*S,H*S));d=ImageDraw.Draw(big)
    n=len(lines);lh=H*S/n
    fs=int(min(lh*0.95,(W*S*0.95)/max(1,max(len(l) for l in lines))*1.0))
    if not vertical and '\n' not in txt:fs=int(min(H*S*0.9,W*S*0.95/max(1,len(txt))))
    f=ImageFont.truetype(font,max(4,fs))
    for i,l in enumerate(lines):
        bb=d.textbbox((0,0),l,font=f);tw=bb[2]-bb[0];th=bb[3]-bb[1]
        if tw>W*S*0.98:
            f2=ImageFont.truetype(font,max(4,int(fs*W*S*0.98/tw)));bb=d.textbbox((0,0),l,font=f2);tw=bb[2]-bb[0];th=bb[3]-bb[1]
        else:f2=f
        x=(W*S-tw)/2-bb[0];y=lh*i+(lh-th)/2-bb[1]
        d.text((x,y),l,font=f2,fill=255)
    return np.array(big.resize((W,H),Image.LANCZOS))
def build_ko(arcpath):
    key=os.path.basename(arcpath)[len('a_common_locationtitle_'):-4]
    if key not in KO:return None
    kana,M=KO[key]
    d,files,texs,imgs,P=pieces(arcpath)
    new={t:imgs[t].copy() for t in imgs}
    serif=os.path.join(GAME,'SeoulHangangEB.ttf');goth=os.path.join(GAME,'NanumSquareNeo-cBd.ttf')
    for p in P:
        img=new[p['tex']];x0,y0,x1,y1=uvpix(img,p['uv'])
        if x1<=x0 or y1<=y0:continue
        if p['name']=='loca_kana':txt=kana;font=goth
        elif p['name'] in M:txt=M[p['name']];font=serif
        else:continue
        W,H=x1-x0,y1-y0
        orig=imgs[p['tex']][y0:y1,x0:x1,3].astype(np.float32)/255
        env=orig.max(1,keepdims=True) if p['name']!='loca_kana' else np.ones((H,1),np.float32)
        env=np.maximum(env,0) ;env=env/ max(1e-3,env.max()) * orig.max() if orig.max()>0 else env
        if p['name']=='loca_kana':
            f=ImageFont.truetype(font,max(6,H-4));im=Image.new('L',(W,H));ImageDraw.Draw(im).text((2,1),txt,font=f,fill=255);m=np.array(im)
            # original kana length in px
        else:
            pad=max(1,min(W,H)//16);m=np.zeros((H,W),np.uint8);mm=_mask(txt,W-2*pad,H-2*pad,font);m[pad:pad+mm.shape[0],pad:pad+mm.shape[1]]=mm
        if p['flipx']:m=m[:,::-1]
        if p['flipy']:m=m[::-1]
        a=m.astype(np.float32)/255
        sh=np.zeros_like(a);o=max(1,min(W,H)//24);sh[o:,o:]=a[:-o or None,:-o or None] if o<min(W,H) else 0
        sh=np.array(Image.fromarray((sh*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)))/255.0
        A=np.clip(np.maximum(a,sh*0.7),0,1)*env
        rgb=np.where(a[...,None]>=sh[...,None]*0.7,255,0)*np.ones(3)
        col=(a[...,None]*255+(1-a[...,None])*0)
        reg=np.zeros((H,W,4),np.float32);reg[:,:,:3]=np.clip(col,0,255);reg[:,:,3]=A*255
        img[y0:y1,x0:x1]=reg.astype(np.uint8)
    out=bytearray(d)
    for t,img in new.items():
        nm,s,e=files[t];b=d[s:e];nb=texpatch.flim_encode(b,img);nb=nb+b[len(nb):];assert len(nb)==e-s;out[s:e]=nb
    return bytes(out)
