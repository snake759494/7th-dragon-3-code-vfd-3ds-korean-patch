# Repack CPK: append replaced files at end (before ETOC), patch TOC offsets/sizes and header in place
import struct,os,sys,shutil
sys.path.insert(0,os.path.dirname(__file__))
import cpk
SZ={0:1,1:1,2:2,3:2,4:4,5:4,6:8,7:8,8:4,0xa:4,0xb:8}
FM={0:'>B',1:'>b',2:'>H',3:'>h',4:'>I',5:'>i',6:'>Q',7:'>q',8:'>f'}
def utfpos(b,base):
    """returns rows: name->(value,abs_pos,type) for per-row columns of a plain @UTF table located at file offset base"""
    assert b[:4]==b'@UTF'
    tsz,ro,so,do,nameo,nc,rl,nr=struct.unpack('>IIIIIHHI',b[4:32])
    so+=8;ro+=8;do+=8
    def s(o):e=b.index(b'\0',so+o);return b[so+o:e].decode('cp932')
    cols=[];p=32
    for i in range(nc):
        fl=b[p];p+=1;nm=s(struct.unpack_from('>I',b,p)[0]);p+=4
        st=fl&0xf0;t=fl&0xf
        if st==0x30:p+=SZ[t]
        cols.append((nm,st,t))
    rows=[]
    for r in range(nr):
        q=ro+r*rl;d={}
        for nm,st,t in cols:
            if st==0x50:
                if t in FM:d[nm]=(struct.unpack_from(FM[t],b,q)[0],base+q,t)
                elif t==0xa:d[nm]=(s(struct.unpack_from('>I',b,q)[0]),base+q,t)
                else:d[nm]=(None,base+q,t)
                q+=SZ[t]
        rows.append(d)
    return rows
def pack(src,dst,repl):
    """repl: {'dir/name': bytes}"""
    f=open(src,'rb');h=f.read(0x800)
    hl=struct.unpack_from('<I',h,8)[0];H=utfpos(h[16:16+hl],16)[0]
    to=H['TocOffset'][0];f.seek(to);t=f.read(16);tl=struct.unpack_from('<I',t,8)[0]
    T=utfpos(f.read(tl),to+16)
    eo=H['EtocOffset'][0];es=H['EtocSize'][0]
    base=to;align=512
    shutil.copyfile(src,dst)
    out=open(dst,'r+b');out.truncate(eo)
    f.seek(eo);etoc=f.read(es)
    cur=eo;done=set()
    for r in T:
        key=((r['DirName'][0]+'/') if r['DirName'][0] and r['DirName'][0]!='<NULL>' else '')+r['FileName'][0]
        if key not in repl:continue
        data=repl[key];done.add(key)
        cur=(cur+align-1)//align*align;out.seek(cur);out.write(data)
        def put(name,v):
            val,pos,tp=r[name];out.seek(pos);out.write(struct.pack(FM[tp],v))
        put('FileOffset',cur-base);put('FileSize',len(data));put('ExtractSize',len(data))
        cur+=len(data)
    missing=set(repl)-done
    assert not missing,missing
    cur=(cur+2047)//2048*2048;out.seek(cur);out.write(etoc)
    def puth(name,v):
        val,pos,tp=H[name];out.seek(pos);out.write(struct.pack(FM[tp],v))
    puth('EtocOffset',cur);puth('ContentSize',cur-H['ContentOffset'][0])
    out.close()
if __name__=='__main__':
    pass
