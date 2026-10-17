# strict NCSD/NCCH validator (what real hardware / GodMode9 checks)
import struct,hashlib,sys
MU=0x200
def al(x,a):return (x+a-1)//a*a
def check(path):
    f=open(path,'rb');import os;size=os.path.getsize(path)
    ncsd=f.read(0x4000);ok=True
    def bad(m):
        nonlocal ok;ok=False;print('  FAIL',m)
    assert ncsd[0x100:0x104]==b'NCSD'
    media=struct.unpack_from('<I',ncsd,0x104)[0]*MU
    parts=struct.unpack_from('<16I',ncsd,0x120)
    print(path,'size',size,'ncsd media',media,'cardinfo filled(0x300)',hex(struct.unpack_from('<I',ncsd,0x300)[0]))
    for i in range(8):
        o,s=parts[2*i]*MU,parts[2*i+1]*MU
        if not s:continue
        f.seek(o);h=f.read(0x200)
        if h[0x100:0x104]!=b'NCCH':bad('part%d not NCCH'%i);continue
        g=lambda x:struct.unpack_from('<I',h,x)[0]
        ncsz=g(0x104)*MU
        if ncsz!=s:bad('part%d size %x vs ncsd %x'%(i,ncsz,s))
        flags=h[0x188:0x190]
        print(' part',i,'off',hex(o),'size',hex(s),'flags',flags.hex(),'id',h[0x150:0x160].rstrip(b'\0'))
        exs=g(0x180)
        if exs:
            f.seek(o+0x200);ex=f.read(0x400)
            if hashlib.sha256(ex).digest()!=h[0x160:0x180]:bad('exheader hash')
            print('  exheader flags byte 0xd',hex(ex[0xd]),'text',hex(struct.unpack_from('<I',ex,0x18)[0]))
        exo,exsz,exhr=g(0x1a0)*MU,g(0x1a4)*MU,g(0x1a8)*MU
        if exsz:
            f.seek(o+exo);eh=f.read(exhr)
            if hashlib.sha256(eh).digest()!=h[0x1c0:0x1e0]:bad('exefs superblock hash (region %x)'%exhr)
            f.seek(o+exo);e=f.read(exsz)
            for k in range(10):
                n,oo,ss=struct.unpack_from('<8sII',e,k*16)
                if not ss:continue
                d=e[0x200+oo:0x200+oo+ss]
                if len(d)<ss:bad('exefs %s truncated'%n);continue
                hh=e[0x200-32*(k+1):0x200-32*k]
                if hashlib.sha256(d).digest()!=hh:bad('exefs section %s hash'%n)
                print('  exefs',n.rstrip(b'\0'),hex(oo),hex(ss))
            if exo+exsz>ncsz:bad('exefs beyond ncch')
        ro,rs,rhr=g(0x1b0)*MU,g(0x1b4)*MU,g(0x1b8)*MU
        if rs:
            f.seek(o+ro);sb=f.read(rhr)
            if hashlib.sha256(sb).digest()!=h[0x1e0:0x200]:bad('romfs superblock hash (region %x)'%rhr)
            f.seek(o+ro);iv=f.read(0x60)
            if iv[:4]!=b'IVFC':bad('no IVFC');continue
            mh=struct.unpack_from('<I',iv,8)[0]
            L=[struct.unpack_from('<QQI',iv,0xc+0x18*k) for k in range(3)]
            bs=[1<<x[2] for x in L]
            hdrsz=struct.unpack_from('<I',iv,0x54)[0]
            print('  ivfc master',hex(mh),'levels',[(hex(a),hex(b),c) for a,b,c in L],'hdr',hex(hdrsz))
            f.seek(o+ro+0x60);master=f.read(mh)
            l3start=al(0x60+mh,bs[2])
            # physical layout: level3 first, then level1, level2
            p3=o+ro+l3start;p1=al(p3+L[2][1],bs[2]);p2=al(p1+L[0][1],bs[0])
            def lvl(p,n):f.seek(p);return f.read(n)
            l1=lvl(p1,L[0][1]);l2=lvl(p2,L[1][1])
            def hs(data,b):
                out=bytearray()
                for x in range(0,len(data),b):
                    blk=data[x:x+b];blk+=b'\0'*(b-len(blk));out+=hashlib.sha256(blk).digest()
                return bytes(out)
            if hs(l1,bs[0])[:mh]!=master:bad('master hash != H(level1)')
            if hs(l2,bs[1])!=l1[:len(hs(l2,bs[1]))]:bad('level1 != H(level2)')
            # level3 hashed in chunks
            f.seek(p3);n=L[2][1];b=bs[2];idx=0;errs=0
            while idx*b<n:
                blk=f.read(b)
                if len(blk)<b:blk+=b'\0'*(b-len(blk))
                if hashlib.sha256(blk).digest()!=l2[idx*32:idx*32+32]:
                    errs+=1
                    if errs<3:bad('level2 != H(level3) block %d'%idx)
                idx+=1
            if errs:bad('level3 bad blocks %d/%d'%(errs,idx))
            if p2+L[1][1]>o+ro+rs:bad('ivfc beyond romfs size')
            if ro+rs>ncsz:bad('romfs beyond ncch')
    print(' RESULT','OK' if ok else 'NG')
    return ok
if __name__=='__main__':
    for p in sys.argv[1:]:check(p)
