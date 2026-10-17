import struct
def load(p):
    d=open(p,'rb').read();a,b,c,z=struct.unpack_from('<4I',d,0)
    n=(b-a)//4;offs=struct.unpack_from('<%dI'%n,d,a)
    S=[]
    for o in offs:
        s=c+o*2;e=s
        while d[e:e+2]!=b'\0\0':e+=2
        S.append(d[s:e].decode('utf-16le'))
    return d,(a,b,c,z),S
def save(p,d,hdr,S):
    a,b,c,z=hdr;body=bytearray();offs=[];cache={}
    for s in S:
        if s in cache:offs.append(cache[s]);continue
        cache[s]=len(body)//2;offs.append(cache[s]);body+=s.encode('utf-16le')+b'\0\0'
    out=bytearray(d[:c]);struct.pack_into('<%dI'%len(offs),out,a,*offs)
    open(p,'wb').write(bytes(out)+bytes(body))
