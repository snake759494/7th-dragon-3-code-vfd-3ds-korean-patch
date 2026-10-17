import sys,os,numpy as np;sys.path.insert(0,os.path.dirname(__file__));import texpatch,tut
from PIL import Image
fs=sys.argv[1:];ims=[]
for f in fs:
    img,_=texpatch.flim_decode(open('cpk/ui/tutorial/'+f,'rb').read());img=tut.apply(f,img)
    ims.append(Image.fromarray(img[:240,:400],'RGBA').convert('RGB'))
S=Image.new('RGB',(810,250*((len(ims)+1)//2)),'white')
for i,im in enumerate(ims):S.paste(im,((i%2)*410,(i//2)*250))
S.save('img/prev.png')
