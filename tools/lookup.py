import json,glob,os,sys
sys.stdout.reconfigure(encoding='utf-8')
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
cat=json.load(open(os.path.join(B,'tr','catalog.json'),encoding='utf-8'))
ko={}
for f in glob.glob(os.path.join(B,'tr','out','*.json')):
    for k,v in json.load(open(f,encoding='utf-8')).items():ko[int(k)]=v
TR={e['jp']:ko.get(e['id']) for e in cat}
def find(q,n=5):
    ex=TR.get(q)
    if ex:return [(q,ex)]
    return [(k,v) for k,v in TR.items() if q in k and v][:n]
if __name__=='__main__':
    for q in sys.argv[1:]:print(q,'=>',find(q,3))
