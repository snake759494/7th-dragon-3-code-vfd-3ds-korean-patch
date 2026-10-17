# find aligned UTF-16LE null-terminated Japanese strings in binary files; capacity = bytes up to next nonzero (aligned)
import sys,os,re,json
def okch(c):
    o=ord(c)
    return (0x20<=o<0x7f) or o in(0x0a,0x08,0x01,0x02) or 0x3000<=o<=0x30ff or 0x4e00<=o<=0x9fff or 0xff01<=o<=0xff9f or 0x2010<=o<=0x266f or o in(0xd7,0xf7,0xb1,0xb4,0xa8)
def isjp(c):
    o=ord(c);return 0x3040<=o<=0x30ff or 0x4e00<=o<=0x9fff or 0xff01<=o<=0xff5e
def scan(d,align=2,minjp=1):
    res=[];i=0;n=len(d)
    while i<n-2:
        if d[i+1]==0 and d[i]==0: i+=2;continue
        # read string
        j=i;s=[]
        while j<n-1:
            c=d[j]|(d[j+1]<<8)
            if c==0:break
            ch=chr(c)
            if not okch(ch):break
            s.append(ch);j+=2
        if j<n-1 and d[j]==0 and d[j+1]==0 and sum(map(isjp,s))>=minjp and (i==0 or not okch(chr(d[i-2]|(d[i-1]<<8))) or (d[i-2]==0 and d[i-1]==0)):
            k=j+2
            while k<n-1 and d[k]==0 and d[k+1]==0:k+=2
            res.append((i,''.join(s),k-i));i=j+2
        else:i+=2
    return res
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for p in sys.argv[1:]:
        d=open(p,'rb').read();r=scan(d)
        print('==',p,len(r))
        for o,s,c in r[:int(os.environ.get('N','30'))]:print(hex(o),c,repr(s[:70]))
