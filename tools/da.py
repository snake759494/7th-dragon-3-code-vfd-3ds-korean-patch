import sys;sys.path.insert(0,__import__('os').path.dirname(__file__));import arm
md=arm.md
def d(va,n):
    for k in range(n):
        a=va+4*k;b=arm.C[a-0x100000:a-0x100000+4]
        l=list(md.disasm(b,a))
        if l:
            i=l[0];s='%08x: %-8s %s'%(a,i.mnemonic,i.op_str)
            if i.mnemonic.startswith('ldr') and '[pc, #' in i.op_str:
                o=int(i.op_str.split('#')[1].rstrip(']'),0);v=arm.u32(a+8+o);s+='   ; =%08x'%v
                if 0x100000<=v<0x100000+len(arm.C):
                    t=arm.C[v-0x100000:v-0x100000+40].split(b'\0')[0]
                    if t and all(32<=c<127 for c in t): s+=' "%s"'%t.decode()
            print(s)
        else: print('%08x: .word %08x'%(a,arm.u32(a)))
if __name__=='__main__': d(int(sys.argv[1],16),int(sys.argv[2]))
