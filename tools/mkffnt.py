# Build Korean 12font.bffnt: keep non-kanji glyphs (+ selected kanji), add Hangul rendered from TTF
import sys,os,struct,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import ffnt
from tex import tile4
from PIL import Image,ImageDraw,ImageFont
def ksx1001():
    s=[]
    for hi in range(0xb0,0xc9):
        for lo in range(0xa1,0xff):
            try:s.append(bytes([hi,lo]).decode('euc-kr'))
            except:pass
    return s
iscjk=lambda c:0x3400<=c<=0x9fff or 0xf900<=c<=0xfaff
def render(ch,font,cw,ch_h,box,thr=0):
    x0,y0,x1,y1=box;S=4
    big=Image.new('L',(cw*S,ch_h*S));d=ImageDraw.Draw(big)
    d.text((0,0),ch,font=font,fill=255)
    a=np.array(big);ys,xs=np.nonzero(a>0)
    if len(xs)==0:return np.zeros((ch_h,cw),np.uint8)
    # place by font-wide reference so all hangul share baseline
    return a
def build(src,ttf,size,keep_kanji,extra,out,yoff=0,xoff=0,adv=12):
    b=open(src,'rb').read();f=ffnt.read(b)
    cw,chh,cols,rows,sw,sh=f['cw'],f['ch'],f['cols'],f['rows'],f['sw'],f['sh'];per=cols*rows
    im=ffnt.images(f)[0]
    def cell(i):r,c=divmod(i,cols);return im[r*(chh+1):r*(chh+1)+chh,c*(cw+1):c*(cw+1)+cw]
    glyphs={}
    for c,i in f['cmap'].items():
        if iscjk(c) and c not in keep_kanji:continue
        glyphs[c]=(cell(i).copy(),f['widths'].get(i,f['dw']))
    font=ImageFont.truetype(ttf,size)
    asc,desc=font.getmetrics()
    ref=font.getbbox('한')
    hang=sorted(set(ord(x) for x in ksx1001())|set(c for c in extra if 0xac00<=c<=0xd7a3 or 0x3131<=c<=0x318e))
    for c in hang:
        g=Image.new('L',(cw,chh));d=ImageDraw.Draw(g)
        bb=font.getbbox(chr(c));w=bb[2]-bb[0]
        ox=xoff+(adv-w)//2-bb[0]
        oy=yoff-ref[1]
        d.text((ox,oy),chr(c),font=font,fill=255)
        glyphs[c]=(np.array(g),(0,adv,adv))
    codes=sorted(glyphs)
    assert len(codes)<=per,(len(codes),per)
    img=np.zeros((sh,sw),np.uint8)
    for k,c in enumerate(codes):
        r,cc=divmod(k,cols);img[r*(chh+1):r*(chh+1)+chh,cc*(cw+1):cc*(cw+1)+cw]=glyphs[c][0]
    sheet=tile4(img)
    tg=0x34;so=f['so']
    hdrblk=bytearray(b[:so])
    struct.pack_into('<B',hdrblk,tg+0x8+2,1)
    tglp_size=so-tg+len(sheet);struct.pack_into('<I',hdrblk,tg+4,tglp_size)
    cwdh_off=so+len(sheet)
    cwdh=bytearray(b'CWDH'+b'\0'*4+struct.pack('<HHI',0,len(codes)-1,0))
    for c in codes:cwdh+=struct.pack('<bBB',*glyphs[c][1])
    while len(cwdh)%4:cwdh+=b'\0'
    struct.pack_into('<I',cwdh,4,len(cwdh))
    cmap_off=cwdh_off+len(cwdh)
    cmap=bytearray(b'CMAP'+b'\0'*4+struct.pack('<HHHHI',codes[0],codes[-1],2,0,0)+struct.pack('<H',len(codes)))
    for k,c in enumerate(codes):cmap+=struct.pack('<HH',c,k)
    while len(cmap)%4:cmap+=b'\0'
    struct.pack_into('<I',cmap,4,len(cmap))
    fi=0x14
    struct.pack_into('<III',hdrblk,fi+20,tg+8,cwdh_off+8,cmap_off+8)
    alt=codes.index(0xff1f) if 0xff1f in codes else codes.index(ord('?'))
    struct.pack_into('<H',hdrblk,fi+14,alt)
    total=cmap_off+len(cmap)
    struct.pack_into('<I',hdrblk,0xc,total);struct.pack_into('<H',hdrblk,0x10,4)
    data=bytes(hdrblk)+sheet+bytes(cwdh)+bytes(cmap);assert len(data)==total
    open(out,'wb').write(data)
    return len(codes),per,img
if __name__=='__main__':
    n,per,img=build('cpk/font/12font.bffnt',sys.argv[1],int(sys.argv[2]),set(),[],'test.bffnt',int(sys.argv[3]),0)
    print(n,per);Image.fromarray(img).save('test_font.png')
