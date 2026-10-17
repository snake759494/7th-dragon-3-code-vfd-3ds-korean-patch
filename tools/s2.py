# key presses + capture of the 7th Dragon window (PrintWindow)
import sys,os,time,ctypes,ctypes.wintypes as WT
sys.path.insert(0,os.path.dirname(__file__))
from emu import *
def findwin():
    res=[]
    @ctypes.WINFUNCTYPE(WT.BOOL,WT.HWND,WT.LPARAM)
    def cb(h,l):
        if u.IsWindowVisible(h) and 'Azahar' in title(h) and 'DRAGON' in title(h): res.append(h)
        return True
    u.EnumWindows(cb,0);return res[0] if res else None
h=findwin()
if not h: print('NOWIN');sys.exit(1)
import emu
CH=[h]+children(h)
_k=key
def key(hh,k,hold=0.08):
    vk=KEYS.get(k,k) if isinstance(k,str) else k;sc=u.MapVirtualKeyW(vk,0)
    for c in CH:u.PostMessageW(c,WM_KEYDOWN,vk,1|(sc<<16))
    time.sleep(hold)
    for c in CH:u.PostMessageW(c,WM_KEYUP,vk,1|(sc<<16)|(0xC0<<24))
for s in sys.argv[2:]:
    if s.startswith('w'): time.sleep(float(s[1:]));continue
    k,_,n=s.partition('*')
    for i in range(int(n or 1)): key(h,k);time.sleep(0.35)
import glob,shutil
from ctrlkey import ctrl_key
B=os.path.join(os.path.dirname(__file__),'..')
old=set(glob.glob(os.path.join(B,'shots','*.png')))
key(h,0x7B)
for i in range(40):
    time.sleep(0.25);new=set(glob.glob(os.path.join(B,'shots','*.png')))-old
    if new: break
f=list(new)[0];time.sleep(0.3);shutil.move(f,sys.argv[1]);print('saved',sys.argv[1])
