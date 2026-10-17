# usage: python -I tools/check_tr.py NNN [NNN...]  -> validates tr/out/NNN.json against tr/in/NNN.json
import sys,json,re,os;sys.stdout.reconfigure(encoding='utf-8')
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
TAG=re.compile(r'<[^>]*>|\{P\d\}|#[a-z]+\b|#[A-Z]+(?:\([^)]*\))?|%[-0-9]*[sd]')
def w(s):
    s=re.sub(r'<[^>]*>','',s);s=s.replace('{P1}','ＮＡＭＥＸ').replace('{P2}','ＮＡＭＥＸ')
    return sum(0.5 if ord(c)<0x100 else 1 for c in s)
bad=0
for n in sys.argv[1:]:
    src=json.load(open(os.path.join(B,'tr','in',n+'.json'),encoding='utf-8'))
    try:out=json.load(open(os.path.join(B,'tr','out',n+'.json'),encoding='utf-8'))
    except Exception as e:print(n,'JSON ERROR',e);bad+=1;continue
    for e in src:
        k=str(e['id']);jp=e['jp']
        if k not in out:print(n,k,'MISSING');bad+=1;continue
        ko=out[k]
        if sorted(TAG.findall(jp))!=sorted(TAG.findall(ko)):print(n,k,'TAG MISMATCH',TAG.findall(jp),TAG.findall(ko));bad+=1
        jl=jp.split('\n');kl=ko.split('\n')
        lim=max(25,max(w(x) for x in jl))
        if len(kl)>max(len(jl),1) and not (len(jl)<=2 and len(kl)<=3 and lim>=25):print(n,k,'TOO MANY LINES',len(jl),len(kl));bad+=1
        for x in kl:
            if w(x)>lim:print(n,k,'LINE TOO LONG %.1f>%.1f'%(w(x),lim),repr(x));bad+=1
        if 'max' in e and len(ko)>e['max']:print(n,k,'OVER MAX',len(ko),e['max']);bad+=1
        if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',re.sub(r'<[^>]*>','',ko)):print(n,k,'JAPANESE LEFT',repr(ko));bad+=1
    extra=set(out)-set(str(e['id']) for e in src)
    if extra:print(n,'EXTRA KEYS',sorted(extra)[:5]);bad+=1
print('problems:',bad)
