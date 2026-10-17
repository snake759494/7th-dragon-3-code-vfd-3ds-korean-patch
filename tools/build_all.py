# Full build: translations -> CPK -> Korean .3ds
import sys,os,json,glob,re,collections,struct
sys.stdout.reconfigure(encoding='utf-8')
T=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,T)
import mess,texts,mkffnt,cpkpack,build,codepatch,sarc,lyt,texpatch,areaimg,ffnt
W=os.path.join(T,'..');GAME=os.path.join(W,'..')
ROM=os.path.join(GAME,'7th Dragon III Code - VFD (Japan).3ds')
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(GAME,'7th Dragon III Code - VFD (Korean).3ds')
BD=os.path.join(W,'build');os.makedirs(BD,exist_ok=True)
TTF=os.path.join(GAME,'NanumSquareNeo-cBd.ttf')
dec=lambda s:s.replace('{P1}','\x08\x01').replace('{P2}','\x08\x02')
# ---- translations
cat=json.load(open(os.path.join(W,'tr','catalog.json'),encoding='utf-8'))
ko={}
for f in sorted(glob.glob(os.path.join(W,'tr','out','*.json'))):
    for k,v in json.load(open(f,encoding='utf-8')).items():ko[int(k)]=v
FIX=[('붉은 말뚝의 탑','홍항의 탑'),('지도리가후치','치도리가후치')]
TR={}
for e in cat:
    if e['id'] in ko:
        v=ko[e['id']]
        if v.strip()=='-' and not re.search(r'[぀-ヿ]',e['jp']):continue
        for a,b in FIX:v=v.replace(a,b)
        TR[dec(e['jp'])]=dec(v)
print('translated',len(TR),'/',len(cat))
# ---- font charset normalisation
orig_font=ffnt.read(open(os.path.join(W,'cpk','font','12font.bffnt'),'rb').read())
iscjk=mkffnt.iscjk
base_chars=set(c for c in orig_font['cmap'] if not iscjk(c))|set(ord(x) for x in mkffnt.ksx1001())
NORM={'⋯':'…','♥':'♡','·':'・','―':'ー','‧':'・','〜':'～','~':'～'}
def norm(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if o in base_chars or o<0x20 or iscjk(o):out.append(ch)
        elif ch in NORM and ord(NORM[ch]) in base_chars:out.append(NORM[ch])
        elif 0xac00<=o<=0xd7a3 or 0x3131<=o<=0x318e:out.append(ch)
        else:out.append(ch)
    return ''.join(out)
for k in TR:TR[k]=norm(TR[k])
tr=lambda s:TR.get(s,s)
R={}
used=collections.Counter()
def track(S):
    for s in S:used.update(s)
# ---- MESS dat
for f in texts.DATS:
    p=os.path.join(W,'cpk','text','JP',f);d,h,S=mess.load(p)
    S2=[tr(s) for s in S];track(S2)
    o=os.path.join(BD,f);mess.save(o,d,h,S2);R['text/JP/'+f]=open(o,'rb').read()
# ---- tables
for f in texts.TBL:
    E=[(i,tr(s)) for i,s in texts.tbl_load(texts.rd(f))];track(s for i,s in E);R[f]=texts.tbl_save(E)
h,ids,S=texts.bb_load(texts.rd('db/b_battle1.bin'));S=[tr(s) for s in S];track(S);R['db/b_battle1.bin']=texts.bb_save(h,ids,S)
def slots(path,fn):
    d=texts.rd(path);sl=fn(d);t={}
    for o,s,cap in sl:
        v=tr(s)
        if len(v.encode('utf-16le'))+2>cap:print('TRUNC',path,repr(v),cap);v=v[:cap//2-1]
        t[s]=v;used.update(v)
    tt={s:t[s] for o,s,c in sl}
    R[path]=texts.slots_save(d,[(o,s,c) for o,s,c in sl],{s:tt[s] for s in tt})
slots('item/itemData.bin',texts.item_slots)
slots('btparam/enemy_list.bin',texts.enemy_slots)
# ---- layouts (static texts) + images inside arcs
LYT={'リトライ':'재도전','タイトルに戻る':'타이틀로','ページ\n':'페이지\n','配信日':'배포일','必要ブロック数':'필요 블록 수','価格':'가격',
 'ブロック\n':'블록\n','円':'엔','残高':'잔액','購入済み\n':'구입완료\n','ダウンロード済み':'다운로드 완료','再ダウンロード':'재다운로드',
 '追加コンテンツ購入\n\n':'추가 콘텐츠 구입\n\n','購入・引換済み追加コンテンツ\n\n':'구입·교환한 추가 콘텐츠\n\n','体験版セーブデータ':'체험판 세이브',
 'デジタルワークスエンターテインメント':'디지털 웍스 엔터테인먼트','○効果音の音量設定\n\n':'효과음 음량 설정\n\n','ボイスタイプA':'음성 타입A'}
import arcimg
for p in sorted(glob.glob(os.path.join(W,'cpk','ui','layout','*.arc'))):
    import loca
    lk=loca.build_ko(p) if 'locationtitle' in p else None
    d=bytearray(lk if lk else open(p,'rb').read());ch=bool(lk)
    for nm,s,e in sarc.parse(bytes(d)):
        if nm.endswith('.bflyt'):
            b=bytes(d[s:e])
            for t,mx,cl,txt,pn,fnt in lyt.txt1s(b):
                key=txt.rstrip('\0')
                if not re.search(r'[぀-ヿ一-鿿]',key):continue
                if key not in LYT:
                    LYT[key]='\n'.join(('사무라이' if 'サムライ' in l else '아틀란티스' if 'アトランティス' in l else ('가나다라마바사아자차'*6)[:max(1,len(l))]) if l else '' for l in key.split('\n'))
                if True:
                    v=LYT[key]
                    while len(v.encode('utf-16le'))+2>mx and v:v=v[:-1]
                    nb=v.encode('utf-16le')+b'\0\0';used.update(v)
                    if len(nb)>mx:print('LYT too long',key);continue
                    d[s+t:s+t+mx]=nb+b'\0'*(mx-len(nb))
                    assert lyt.set_curlen(d,s,t,len(nb))
                    ch=True;used.update(LYT[key])
        if nm.endswith('.bflim'):
            nb=arcimg.patch(os.path.basename(p),nm,bytes(d[s:e]))
            if nb is not None:
                assert len(nb)==e-s;d[s:e]=nb;ch=True
    if ch:R['ui/layout/'+os.path.basename(p)]=bytes(d)
# ---- area / chapter images
for l in open(os.path.join(W,'tr','area.txt'),encoding='utf-8'):
    k,l2,l3=l.rstrip('\n').split('\t')
    fn=(k if k.startswith('map') else 'areatitle_'+k)+'.bflim'
    b=open(os.path.join(W,'cpk','ui','areatitlelist',fn),'rb').read();img,fmt=texpatch.flim_decode(b)
    new=areaimg.light(img,l2,l3) if img.shape[0]==32 else areaimg.dark(img,l2,l3)
    nb=texpatch.flim_encode(b,new)
    R['ui/areatitlelist/'+fn]=nb+b[len(nb):]
for k,v in areaimg.CHAPTER.items():
    b=open(os.path.join(W,'cpk','ui','chaptertitlelist',k+'.bflim'),'rb').read();img,fmt=texpatch.flim_decode(b)
    nb=texpatch.flim_encode(b,areaimg.chapter(img,v));R['ui/chaptertitlelist/'+k+'.bflim']=nb+b[len(nb):]
import tut
for fn in [k for k in tut.SPEC if k.startswith('tr_')]:
    b=open(os.path.join(W,'cpk','ui','tutorial',fn),'rb').read();img,fmt=texpatch.flim_decode(b)
    nb=texpatch.flim_encode(b,tut.apply(fn,img));R['ui/tutorial/'+fn]=nb+b[len(nb):]
# ---- font
allc=set(ord(c) for c in used)
kan=collections.Counter({ord(c):n for c,n in used.items() if iscjk(ord(c))})
nonk=len([c for c in orig_font['cmap'] if not iscjk(c)])
han=set(ord(x) for x in mkffnt.ksx1001())|set(c for c in allc if 0xac00<=c<=0xd7a3 or 0x3131<=c<=0x318e)
room=4380-nonk-len(han)
keep=set(c for c,n in kan.most_common(max(0,room)))
miss=[chr(c) for c in allc if c>=0x20 and c not in base_chars and not iscjk(c) and not 0xac00<=c<=0xd7a3]
print('kanji used',len(kan),'kept',len(keep),'missing glyphs',''.join(sorted(set(miss)))[:200])
n,per,img=mkffnt.build(os.path.join(W,'cpk','font','12font.bffnt'),TTF,12,keep,sorted(han),os.path.join(BD,'12font.bffnt'),4,0)
print('font glyphs',n,per)
R['font/12font.bffnt']=open(os.path.join(BD,'12font.bffnt'),'rb').read()
# ---- pack
cpkpack.pack(os.path.join(W,'ext','romfs','cpk','eden_files.cpk'),os.path.join(BD,'eden_files.cpk'),R)
code=codepatch.apply_strings(codepatch.apply(open(os.path.join(W,'code.bin'),'rb').read()))
icon=codepatch.patch_icon(open(os.path.join(W,'ext','exefs','icon'),'rb').read())
build.build(ROM,OUT,{'cpk/eden_files.cpk':os.path.join(BD,'eden_files.cpk')},newcode=code,newicon=icon)
os.remove(os.path.join(BD,'eden_files.cpk'))
print('built',OUT,os.path.getsize(OUT))
