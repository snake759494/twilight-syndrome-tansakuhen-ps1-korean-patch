import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from lz import dec
from cdb import entries
TABS={'CAP0':(0x80093b34,0x224),'CAP1':(0x80090ae8,0x366),'CAP2':(0x8008c820,0x361),'CAP3':(0x80091f2c,0x30f),'CAP4':(0x80090bbc,0x359),'CAPX':(0x80083b48,0x236)}
def exe(cap):
    b=open('orig/%s.EXE'%cap,'rb').read(); return b,struct.unpack_from('<I',b,0x18)[0]-0x800
def table(cap):
    b,base=exe(cap); a,n=TABS[cap]
    return [struct.unpack_from('<II',b,a-base+8*i) for i in range(n)]
_k=None
def kfont_entry(i):
    global _k
    if _k is None: _k=open('orig/DAT/FONT/KFONT.CDB','rb').read()
    s,n=entries(_k)[i]; return _k[s*2048:(s+n)*2048]
def find_entry(cap):
    t=table(cap)
    for i in range(8):
        e=kfont_entry(i)
        try:
            ok=all(dec(e,p-0x8001a200)[0] for p,w in t[:5]) and max(p for p,w in t)-0x8001a200<len(e)
            # 마지막 글리프 해제 성공 확인
            p=max(p for p,w in t); dec(e,p-0x8001a200)
            if ok and len(e)-(p-0x8001a200)<0x900: return i
        except Exception: pass
def glyphs(cap):
    t=table(cap); e=kfont_entry(find_entry(cap)); res=[]
    for p,w in t:
        out,_=dec(e,p-0x8001a200); res.append((w,[(out[i//2]>>(4*(i&1)))&15 for i in range(256)]))
    return res
