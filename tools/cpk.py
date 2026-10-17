import struct,os,sys
def dexor(b):
    if b[:4]==b'@UTF':return b
    o=bytearray(b);m=0x5f
    for i in range(len(o)):o[i]^=m;m=(m*0x15)&0xff
    return bytes(o)
def utf(b):
    b=dexor(b);assert b[:4]==b'@UTF',b[:8]
    tsz,ro,so,do,nameo,nc,rl,nr=struct.unpack('>IIIIIHHI',b[4:32])
    B=8;so+=B;do+=B;ro+=B
    def s(o):e=b.index(b'\0',so+o);return b[so+o:e].decode('cp932')
    cols=[];p=32
    for i in range(nc):
        fl=b[p];p+=1;nm=s(struct.unpack_from('>I',b,p)[0]);p+=4
        st=fl&0xf0;t=fl&0xf;const=None
        if st==0x30:const,p=val(b,p,t,s,do)
        cols.append((nm,st,t,const))
    rows=[]
    for r in range(nr):
        q=ro+r*rl;d={}
        for nm,st,t,const in cols:
            if st==0x50:d[nm],q=val(b,q,t,s,do)
            elif st==0x30:d[nm]=const
            else:d[nm]=None
        rows.append(d)
    return rows
def val(b,p,t,s,do):
    F={0:'>B',1:'>b',2:'>H',3:'>h',4:'>I',5:'>i',6:'>Q',7:'>q',8:'>f'}
    if t in F:v=struct.unpack_from(F[t],b,p)[0];return v,p+struct.calcsize(F[t])
    if t==0xa:return s(struct.unpack_from('>I',b,p)[0]),p+4
    if t==0xb:o,l=struct.unpack_from('>II',b,p);return b[do+o:do+o+l],p+8
    raise Exception(t)
def crilayla(d):
    if d[:8]!=b'CRILAYLA':return d
    usz,hoff=struct.unpack_from('<II',d,8)
    out=bytearray(usz+0x100);out[:0x100]=d[0x10+hoff:0x10+hoff+0x100]
    src=d[:0x10+hoff];pos=len(src)-1;bitpool=0;nb=0
    def bits(n):
        nonlocal pos,bitpool,nb
        v=0
        while n:
            if nb==0:bitpool=src[pos];pos-=1;nb=8
            k=min(n,nb);v=(v<<k)|((bitpool>>(nb-k))&((1<<k)-1));nb-=k;n-=k
        return v
    w=0;end=usz
    while w<end:
        if bits(1):
            off=bits(13)+3;l=3;lv=[2,3,5,8];i=0
            while True:
                x=bits(lv[min(i,3)]);l+=x
                if x!=(1<<lv[min(i,3)])-1:break
                i+=1
            for _ in range(l):
                out[0x100+usz-1-w]=out[0x100+usz-1-w+off];w+=1
        else:
            out[0x100+usz-1-w]=bits(8);w+=1
    return bytes(out)
def toc(path):
    f=open(path,'rb');h=f.read(0x800)
    hd=utf(h[16:16+struct.unpack_from('<I',h,8)[0]])[0]
    to=hd['TocOffset'];f.seek(to);t=f.read(16);n=struct.unpack_from('<I',t,8)[0];T=utf(f.read(n))
    base=min(to,hd['ContentOffset']) if hd.get('ContentOffset') else to
    return hd,T,base
if __name__=='__main__':
    hd,T,base=toc(sys.argv[1]);print(len(T),hd);
    if len(sys.argv)>2:
        f=open(sys.argv[1],'rb');out=sys.argv[2]
        for r in T:
            p=os.path.join(out,(r['DirName'] or ''),r['FileName']);os.makedirs(os.path.dirname(p),exist_ok=True)
            f.seek(base+r['FileOffset']);d=f.read(r['FileSize'])
            if r['FileSize']!=r['ExtractSize']:d=crilayla(d)
            open(p,'wb').write(d)
