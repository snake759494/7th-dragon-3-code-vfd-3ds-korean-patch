import sys,os,json,glob;sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,'tools')
import texts,mess,scan16
cat={};order=[]
def add(s,src,cap=None):
    if not any(scan16.isjp(c) for c in s):return
    if s not in cat:cat[s]={'id':len(order),'jp':s,'cap':None,'src':src};order.append(s)
    if cap is not None:
        c=cat[s]['cap'];cat[s]['cap']=cap if c is None else min(c,cap)
for f in texts.DATS:
    for s in mess.load(os.path.join(texts.CPK,'text','JP',f))[2]:add(s,f)
for f in texts.TBL:
    for i,s in texts.tbl_load(texts.rd(f)):add(s,f)
for s in texts.bb_load(texts.rd('db/b_battle1.bin'))[2]:add(s,'b_battle1')
for o,s,c in texts.item_slots(texts.rd('item/itemData.bin')):add(s,'itemData',c//2-1)
for o,s,c in texts.enemy_slots(texts.rd('btparam/enemy_list.bin')):add(s,'enemy_list',c//2-1)
L=[cat[s] for s in order]
enc=lambda s:s.replace('\x08\x01','{P1}').replace('\x08\x02','{P2}')
for e in L:e['jp']=enc(e['jp'])
json.dump(L,open('tr/catalog.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(L),sum(len(e['jp']) for e in L))
import collections;print(collections.Counter(e['src'] for e in L))
# chunks
os.makedirs('tr/in',exist_ok=True);os.makedirs('tr/out',exist_ok=True)
ch=[];cur=[];n=0
for e in L:
    if e['src']=='MessDeBug.dat':continue
    cur.append({'id':e['id'],'jp':e['jp'],**({'max':e['cap']} if e['cap'] else {})});n+=len(e['jp'])
    if n>=8000:ch.append(cur);cur=[];n=0
if cur:ch.append(cur)
for i,c in enumerate(ch):json.dump(c,open('tr/in/%03d.json'%i,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('chunks',len(ch))
