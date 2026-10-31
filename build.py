# 트와일라잇 신드롬 ~탐색편~ 한글패치 빌드
import sys,os,json,struct,shutil
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'tools'))
os.chdir(HERE)
from ents import SCRIPTS
from cdb import entries,parts
from script import blocks,toks
from tok import parse
from lz import comp,dec
from enc import tokens,plain
from ptrs import exe_ptrs,assign,script_entries
from xref import consts
from font import TABS
import kfont
from disc import Writer
ROOT=os.path.dirname(HERE)
ORIG=os.path.join(ROOT,'Twilight Syndrome - Tansaku-hen (Japan).bin')
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'test.bin')
CAPS=['CAP0','CAP1','CAP2','CAP3','CAP4','CAPX']
FONT_ENTRY={'CAP0':0,'CAP1':3,'CAP2':1,'CAP3':5,'CAP4':2,'CAPX':7}
FONT_MAX=0x17000            # 46섹터 (CAP1 원본 크기) — 0x80031200 까지
def name(cap,f,k): return '%s_%s_%d'%(cap,os.path.basename(f).split('.')[0],k)
def load_ko(n):
    p='text/ko/%s.json'%n
    if not os.path.exists(p): return {}
    return {x['id']:x['ko'] for x in json.load(open(p,encoding='utf-8')) if x.get('ko')}
def pack_cdb(orig,newparts):
    """CDB 재구성: 헤더(엔트리 표) + 섹터 정렬 데이터"""
    ents=entries(orig); hdr=bytearray(orig[:2048]); body=bytearray(); sec=1
    out=[]
    for i,(s,n) in enumerate(ents):
        d=newparts.get(i)
        if d is None: d=orig[s*2048:(s+n)*2048]
        nn=(len(d)+2047)//2048
        struct.pack_into('<HH',hdr,4*i,sec if nn or True else s,nn)
        body+=d.ljust(nn*2048,b'\0'); sec+=nn
    # 원본에서 n==0 인 엔트리의 시작값 보존 규칙: 다음 엔트리 시작과 동일
    return bytes(hdr)+bytes(body)
def main():
    se=script_entries()
    cdbs={}      # 경로 -> {entry: bytes}
    exe_patch={c:{} for c in CAPS}   # 주소 -> 4바이트
    charsets={c:{} for c in CAPS}
    kos={}
    for cap,f,k in SCRIPTS:
        ko=load_ko(name(cap,f,k)); kos[(cap,f,k)]=ko
        for s in ko.values():
            for ch in plain(s):
                if ch not in '\n　': charsets[cap][ch]=charsets[cap].get(ch,0)+1
    cmaps={}; fonts={}
    for cap in CAPS:
        chars=sorted(charsets[cap],key=lambda c:(-charsets[cap][c],c))
        data,cm=kfont.build(cap,chars)
        print(cap,'glyphs',len(chars),'font bytes',hex(len(data)))
        assert len(data)<=FONT_MAX,(cap,hex(len(data)))
        cmaps[cap]=cm; fonts[cap]=data
    # 스크립트 재구성
    for cap,f,k in SCRIPTS:
        path='orig/'+f; orig=open(path,'rb').read()
        e=parts(orig)[k]; bl=blocks(e); ko=kos[(cap,f,k)]
        newe=bytearray(); remap={}
        for n,(o,o2,dat) in enumerate(bl):
            remap[o]=len(newe)
            if n in ko:
                p=parse(toks(dat))
                head=[v for kd,v in p if kd=='H']; tail=[v for kd,v in p if kd in('E','X')]
                tk=head+tokens(ko[n],cmaps[cap])+tail
                raw=struct.pack('<%dH'%len(tk),*tk)
                z=comp(raw); assert dec(z)[0]==raw
                newe+=z
            else:
                newe+=e[o:o2]
        assert len(newe)<=0xe800,(f,k,hex(len(newe)))
        cdbs.setdefault(f,{})[k]=bytes(newe)
        # EXE 포인터 갱신
        res,_=assign(cap,se)
        b=open('orig/%s.EXE'%cap,'rb').read(); base=struct.unpack_from('<I',b,0x18)[0]-0x800
        for a,key,v in res:
            if key==('orig/'+f,k):
                exe_patch[cap][a]=struct.pack('<I',0x801f0000+remap[v])
    # 폰트: KFONT.CDB 엔트리 교체
    cdbs.setdefault('DAT/FONT/KFONT.CDB',{})
    for cap in CAPS: cdbs['DAT/FONT/KFONT.CDB'][FONT_ENTRY[cap]]=fonts[cap]
    import gfxpatch
    for f,d in gfxpatch.all_patches().items(): cdbs.setdefault(f,{}).update(d)
    # EXE 폰트 테이블 참조/디코더 호출 패치
    T=kfont.BASE+kfont.TAB_OFF
    for cap in CAPS:
        b=open('orig/%s.EXE'%cap,'rb').read(); base=struct.unpack_from('<I',b,0x18)[0]-0x800
        tb,_=TABS[cap]
        refs=[(a,v,h) for a,m,v,h in consts('orig/%s.EXE'%cap) if tb<=v<tb+8]
        assert len(refs)==3,(cap,refs)
        for a,v,h in refs:
            nv=T+(v-tb); hi=(nv+0x8000)>>16; lo=nv&0xffff
            ins=struct.unpack_from('<I',b,h-base)[0]; exe_patch[cap][h]=struct.pack('<I',(ins&0xffff0000)|hi)
            ins=struct.unpack_from('<I',b,a-base)[0]; exe_patch[cap][a]=struct.pack('<I',(ins&0xffff0000)|lo)
            if v==tb:
                j=a+0xc; ins=struct.unpack_from('<I',b,j-base)[0]
                assert ins>>26==3,(cap,hex(j))
                exe_patch[cap][j]=struct.pack('<I',(3<<26)|((kfont.EXPAND_ADDR>>2)&0x3ffffff))
    # 디스크 쓰기
    shutil.copyfile(ORIG,OUT)
    w=Writer(OUT)
    for cap in CAPS:
        b=bytearray(open('orig/%s.EXE'%cap,'rb').read()); base=struct.unpack_from('<I',b,0x18)[0]-0x800
        for a,d in exe_patch[cap].items(): b[a-base:a-base+4]=d
        w.replace('/%s.EXE'%cap,bytes(b),allow_move=False)
    for f,np_ in cdbs.items():
        orig=open('orig/'+f,'rb').read()
        nb=pack_cdb(orig,np_)
        lba=w.replace('/'+f,nb)
        print(f,len(orig),'->',len(nb),'lba',lba)
    for f,data in gfxpatch.sinkou().items():
        print(f,w.replace('/'+f,data))
    cue=os.path.splitext(OUT)[0]+'.cue'
    open(cue,'w').write('FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'%os.path.basename(OUT))
    print('done',OUT)
if __name__=='__main__': main()
