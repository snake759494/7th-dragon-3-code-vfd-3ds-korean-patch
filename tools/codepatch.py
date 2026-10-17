# code.bin patches (uncompressed code, VA = 0x100000 + offset)
B=0x100000
PATCHES=[
 # layout default font slot: load font/12font.bffnt instead of system shared font
 (0x10e2b4,bytes.fromhex('0020a0e3051d84e20400a0e1'),bytes.fromhex('051d84e2a82d4fe26f2042e2')),
]
def apply(code):
    c=bytearray(code)
    for va,orig,new in PATCHES:
        o=va-B;assert c[o:o+len(orig)]==orig,(hex(va),c[o:o+len(orig)].hex())
        c[o:o+len(new)]=new
    return bytes(c)
# in-place UTF-16 strings (Korean must not exceed original length)
STRS=[('削除','삭제'),('再ダウンロード','재다운로드'),('ヤマト','야마토'),('引換券の番号を入力してください','교환권 번호를 입력해 주세요'),
 ('購入','구입'),('残高の追加','잔액 추가'),('戻る','뒤로'),('リコ','리코'),('ナガミミ','나가미미')]
def apply_strings(code):
    c=bytearray(code)
    for jp,ko in STRS:
        jb=jp.encode('utf-16le')+b'\0\0';kb=ko.encode('utf-16le')
        assert len(kb)+2<=len(jb),jp
        i=c.find(jb);n=0
        while i>=0:
            if i%2==0:c[i:i+len(jb)]=kb+b'\0'*(len(jb)-len(kb));n+=1
            i=c.find(jb,i+1)
        assert n,jp
    return bytes(c)
def patch_icon(icon):
    d=bytearray(icon)
    t='7TH DRAGON Ⅲ code:VFD'.encode('utf-16le')
    o=8
    for a,n in((0,0x80),(0x80,0x100)):d[o+a:o+a+n]=t+b'\0'*(n-len(t))
    return bytes(d)
