# parse/rebuild all text containers
import struct,os,sys,glob
sys.path.insert(0,os.path.dirname(__file__))
import mess,scan16
CPK=os.path.join(os.path.dirname(__file__),'..','cpk')
def cstr(d,o):
    e=o
    while d[e:e+2]!=b'\0\0':e+=2
    return d[o:e].decode('utf-16le')
# --- id/offset table (TownText, questText1, staffrollText)
def tbl_load(d):
    n=struct.unpack_from('<I',d,0)[0];base=4+n*8
    ents=[struct.unpack_from('<II',d,4+i*8) for i in range(n)]
    return [(i,cstr(d,base+o)) for i,o in ents]
def tbl_save(ents):
    n=len(ents);out=bytearray(struct.pack('<I',n));body=bytearray();cache={}
    for i,s in ents:
        if s not in cache:cache[s]=len(body);body+=s.encode('utf-16le')+b'\0\0'
        out+=struct.pack('<II',i,cache[s])
    return bytes(out+body)
# --- b_battle1: u16 n, u16 pad, u32 ids[n], u16 offs[n], strings
def bb_load(d):
    n=struct.unpack_from('<H',d,0)[0];ids=struct.unpack_from('<%dI'%n,d,4);ob=4+4*n
    offs=struct.unpack_from('<%dH'%n,d,ob);base=ob+2*n
    return d[:4],ids,[cstr(d,base+o) for o in offs]
def bb_save(head,ids,S):
    n=len(ids);body=bytearray();offs=[];cache={}
    for s in S:
        if s not in cache:cache[s]=len(body);body+=s.encode('utf-16le')+b'\0\0'
        offs.append(cache[s])
    assert len(body)<0x10000
    return head+struct.pack('<%dI'%n,*ids)+struct.pack('<%dH'%n,*offs)+bytes(body)
# --- in-place slots
def item_slots(d):
    G=[struct.unpack_from('<HHIII',d,i*16) for i in range(6)]
    offs=[g[2] for g in G]+[len(d)]
    sl=[]
    found={o:(s,c) for o,s,c in scan16.scan(d,minjp=1)}
    for gi,(cat,n,o,a,b) in enumerate(G):
        rs=(offs[gi+1]-o)//n
        for k in range(n):
            r0=o+k*rs
            for q,cap in((0,32),(32,96)):
                s=cstr(d,r0+q)
                if any(scan16.isjp(c) for c in s):sl.append((r0+q,s,cap))
            for oo,(s,c) in found.items():
                if r0+64<=oo<r0+rs:sl.append((oo,s,min(c,len(s)*2+2)))
    return sl
def enemy_slots(d):
    i=d.index(b'\xff\xfe\xd6\x30') if False else 0x1b80
    sl=[];p=0x1b80
    while p<len(d):
        assert d[p:p+2]==b'\xff\xfe',hex(p)
        s=cstr(d,p+2);e=p+2+len(s)*2+2
        q=e
        while q<len(d) and d[q:q+2]==b'\0\0':q+=2
        if any(scan16.isjp(c) for c in s):sl.append((p+2,s,q-(p+2)))
        p=q
    return sl
def slots_save(d,sl,tr):
    d=bytearray(d)
    for o,s,cap in sl:
        t=tr.get(s,s);b=t.encode('utf-16le')
        assert len(b)+2<=cap,(s,t,cap)
        d[o:o+cap]=b+b'\0'*(cap-len(b))
    return bytes(d)
DATS=sorted(os.path.basename(p) for p in glob.glob(os.path.join(CPK,'text','JP','*.dat')))
TBL=['db/TownText.bin','db/questText1.bin','db/staffrollText.bin']
def rd(p):return open(os.path.join(CPK,p),'rb').read()
