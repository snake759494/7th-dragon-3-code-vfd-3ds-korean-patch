import sys,re;sys.stdout.reconfigure(encoding='utf-8')
d=open(sys.argv[1],'rb').read();n=int(sys.argv[2]) if len(sys.argv)>2 else 40
pat=re.compile(rb'(?:[\x00-\xff][\x00-\xff]){2,}?\x00\x00')
i=0;c=0
for m in re.finditer(rb'(?:(?:[\x20-\x7e]\x00)|(?:[\x00-\xff][\x30-\x9f\xff]))+?\x00\x00',d):
    if m.start()%2:continue
    try:s=m.group()[:-2].decode('utf-16le')
    except:continue
    if any(0x3040<=ord(ch)<=0x9fff or 0xff00<=ord(ch)<=0xffef for ch in s) and len(s)>=2:
        print(hex(m.start()),repr(s[:80]));c+=1
        if c>=n:break
