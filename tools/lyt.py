# BCLYT txt1 text extraction (3DS layout)
import struct,sys,os,glob
sys.path.insert(0,os.path.dirname(__file__))
import sarc
def txt1s(b):
    """yield (abs_text_off, maxlen_bytes, curlen_bytes, text, pane_name, font_idx) for each txt1"""
    assert b[:4]==b'FLYT',b[:4]
    hl=struct.unpack_from('<H',b,6)[0];n=struct.unpack_from('<H',b,0x10)[0];o=hl
    fonts=[]
    for i in range(n):
        mg=b[o:o+4];sz=struct.unpack_from('<I',b,o+4)[0]
        if mg==b'fnl1':
            cnt=struct.unpack_from('<I',b,o+8)[0]
            for k in range(cnt):
                no=struct.unpack_from('<I',b,o+12+4*k)[0];fonts.append(b[o+12+no:].split(b'\0')[0].decode())
        if mg==b'txt1':
            name=b[o+0x0c:o+0x0c+0x18].split(b'\0')[0].decode('ascii','replace')
            p=o+0x54
            maxl,curl,mat,font,anchor,align,_,rot,toff=struct.unpack_from('<HHHHBBHfI',b,p)
            t=o+toff
            txt=b[t:t+curl].decode('utf-16le','replace')
            yield t,maxl,curl,txt,name,fonts[font] if font<len(fonts) else font
        o+=sz
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    import collections;C=collections.Counter();n=0;U={}
    for p in sorted(glob.glob('cpk/ui/**/*.arc',recursive=True)):
        d=open(p,'rb').read()
        if d[:4]!=b'SARC':continue
        for nm,s,e in sarc.parse(d):
            if not nm.endswith('.bflyt'):continue
            for t,mx,cl,txt,pn,fnt in txt1s(d[s:e]):
                C[fnt]+=1
                if any(0x3040<=ord(c)<=0x9fff for c in txt):
                    n+=1;U.setdefault(txt,[]).append((os.path.basename(p),nm,pn,mx))
    print(C);print(n,len(U))
    for k,v in list(U.items())[:400]:print(repr(k),v[0],len(v))
def set_curlen(d,s,t,n):
    """d: bytearray of arc, s: bflyt start, t: text offset within bflyt; set textStrBytes=n"""
    b=bytes(d[s:s+struct.unpack_from('<I',d,s+0xc)[0]])
    hl=struct.unpack_from('<H',b,6)[0];cnt=struct.unpack_from('<H',b,0x10)[0];o=hl
    for i in range(cnt):
        mg=b[o:o+4];sz=struct.unpack_from('<I',b,o+4)[0]
        if mg==b'txt1' and o+struct.unpack_from('<I',b,o+0x64)[0]==t:
            struct.pack_into('<H',d,s+o+0x56,n);return True
        o+=sz
    return False
