"""그래픽 텍스트 한글화: KALINK 메뉴 라벨/게임오버"""
import sys,os,struct,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from cdb import entries
from lz import dec,comp,comp_fit
from tim import parse
from PIL import Image,ImageDraw,ImageFont
G11='fonts/Galmuri11.ttf'; G9='fonts/Galmuri9.ttf'
def blobs(e):
    o=0;r=[]
    while o<len(e):
        try:d,o2=dec(e,o)
        except Exception:break
        if o2<=o:break
        r.append((o,o2,d));o=o2
    return r
def idx_of(t):
    d=np.frombuffer(t['data'],np.uint16).reshape(t['h'],t['w'])
    if t['bpp']==0: return np.stack([(d>>(4*i))&15 for i in range(4)],-1).reshape(t['h'],-1)
    return np.stack([d&255,d>>8],-1).reshape(t['h'],-1)
def set_idx(d,t,idx):
    h=t['h']
    if t['bpp']==0:
        v=idx.reshape(h,-1,4).astype(np.uint16); w=v[...,0]|v[...,1]<<4|v[...,2]<<8|v[...,3]<<12
    else:
        v=idx.reshape(h,-1,2).astype(np.uint16); w=v[...,0]|v[...,1]<<8
    p=t['ipos']+12; d[p:p+len(t['data'])]=w.astype('<u2').tobytes()
def label(t,d,text,font,size,fg,bg,dy=0,x0=0):
    idx=idx_of(t); W=idx.shape[1];H=idx.shape[0]
    f=ImageFont.truetype(font,size); im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    dr.text((x0,dy),text,font=f,fill=255)
    a=np.asarray(im)>127
    assert not a[:,W-1].any() or True
    bb=dr.textbbox((x0,dy),text,font=f)
    if bb[2]>W: print('경고: 폭 초과',text,bb,W)
    new=np.where(a,fg,bg).astype(np.uint8); set_idx(d,t,new)
def patch_entry(e,mods):
    """mods: {blob_index: fn(bytearray d,t)} -> 새 엔트리(위치 보존)"""
    e=bytearray(e); bl=blobs(bytes(e))
    for j,fn in mods.items():
        o,o2,d=bl[j]; d=bytearray(d); t=parse(bytes(d),0); fn(d,t)
        c=comp_fit(bytes(d),o2-o)
        e[o:o+len(c)]=c
    return bytes(e)
def most(idx,mask=None):
    v,c=np.unique(idx if mask is None else idx[mask],return_counts=True); return v[np.argsort(-c)]
def kalink():
    b=open('orig/DAT/ALLCAP/KALINK.CDB','rb').read(); ents=entries(b); out={}
    def ent(k): s,n=ents[k]; return b[s*2048:(s+n)*2048]
    L={2:'기억한다',3:'꿈이었다',4:'옵션 메뉴',5:'창 색상',6:'메시지 타입',7:'기억 회상'}
    def mk(text):
        def fn(d,t):
            idx=idx_of(t); bg=int(most(idx)[0]); fg=int(most(idx)[1])
            label(t,d,text,G11,12,fg,bg,dy=1)
        return fn
    out[3]=patch_entry(ent(3),{j:mk(s) for j,s in L.items()})
    out[0]=patch_entry(ent(0),{1:gameover})
    out[4]=patch_entry(ent(4),{j:card(*v) for j,v in CARDS.items()})
    return out
def gameover(d,t):
    idx=idx_of(t).copy(); H,W=idx.shape
    idx[37:78][idx[37:78]==7]=0
    sub=idx[78:110,138:]; sub[sub==12]=0; idx[73:78,140:][idx[73:78,140:]==12]=0
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im); f=ImageFont.truetype(G11,12)
    dr.text((10,38),'아하하~ 당신은',font=f,fill=255); dr.text((50,60),'죽어버렸어♪',font=f,fill=255)
    a=np.asarray(im)>127; idx[a]=7
    im=Image.new('L',(W,H)); ImageDraw.Draw(im).text((140,84),'하나코',font=f,fill=255)
    idx[np.asarray(im)>127]=12
    set_idx(d,t,idx)
CARDS={0:(None,'시작의 소문'),1:('첫 번째 소문','심령사진 양산 공원'),2:('두 번째 소문','음악실의 M.K'),
 3:('세 번째 소문','막차'),4:('네 번째 소문','히나시로 고교 7대 불가사의'),5:(None,'또 하나의 소문')}
def bands(m):
    rows=np.nonzero(m.any(1))[0]; out=[]; st=rows[0]; pv=rows[0]
    for r in rows[1:]:
        if r-pv>8: out.append((st,pv+1)); st=r
        pv=r
    out.append((st,pv+1)); return [b for b in out if b[1]-b[0]>6]
def card(head,title):
    def fn(d,t):
        idx=idx_of(t); H,W=idx.shape; m=(idx!=15)&(idx!=0)
        bs=bands(m); lines=[x for x in (head,title) if x]
        assert len(bs)==len(lines),(title,bs)
        out=np.full((H,W),15,np.uint8); rng=np.random.default_rng(len(title))
        for (y0,y1),s in zip(bs,lines):
            xs=np.nonzero(m[y0:y1].any(0))[0]; x0,x1=xs.min(),xs.max()+1
            size=int((y1-y0)*1.15)
            while True:
                f=ImageFont.truetype(SERIF,size); bb=f.getbbox(s)
                if bb[2]-bb[0]<=min(W-8,max(x1-x0,0)+60) or size<10: break
                size-=1
            w=bb[2]-bb[0]; cx=min(max((x0+x1)//2,w//2+4),W-4-w//2)
            im=Image.new('L',(W,H)); ImageDraw.Draw(im).text((cx-w//2-bb[0],(y0+y1)//2-(bb[1]+bb[3])//2),s,font=f,fill=255)
            a=np.asarray(im).astype(float)/255
            a*=np.where(rng.random(H)<0.25,0.55,1.0)[:,None]   # 원본처럼 가로 줄무늬 잡음
            lv=np.clip((a*14).astype(int),0,14); mm=lv>1
            out[mm]=15-lv[mm]
        set_idx(d,t,out)
    return fn
def all_patches():
    return {'DAT/ALLCAP/KALINK.CDB':kalink(),'DAT/SINKOU/ALLLINK.CDB':chapter_labels()}
if __name__=='__main__':
    from tim import image
    p=all_patches()['DAT/ALLCAP/KALINK.CDB'][3]
    ims=[image(parse(d,0)) for _,_,d in blobs(p)[2:8]]
    W=Image.new('RGB',(140,6*20));[W.paste(im,(0,i*20)) for i,im in enumerate(ims)]
    W.resize((560,480),0).save('shots/m.png')
SERIF='../SeoulHangangM.ttf'
def lum(v): return ((v&31)*3+((v>>5)&31)*6+((v>>10)&31))/10
def vtext(W,H,text,size,font=SERIF,spacing=0):
    """세로쓰기 L 이미지(폭 W)"""
    f=ImageFont.truetype(font,size); im=Image.new('L',(W,H)); y=0
    for ch in text:
        if ch==' ': y+=size//3; continue
        g=Image.new('L',(size+8,size+8)); ImageDraw.Draw(g).text((4,4),ch,font=f,fill=255)
        if ch in '「」':
            g=g.rotate(-90)
        bb=g.getbbox()
        if bb is None: y+=size//2; continue
        if ch in '「」':
            c=g.crop(bb); im.paste(c,((W-c.size[0])//2,y+(2 if ch=='「' else 0)),c); y+=c.size[1]+4
        else:
            c=g.crop((0,bb[1],size+8,bb[3])); cb=c.getbbox(); c=c.crop((cb[0],0,cb[2],c.size[1]))
            im.paste(c,((W-c.size[0])//2,y),c); y+=size+spacing
    return im,y
def chapter_labels():
    b=open('orig/DAT/SINKOU/ALLLINK.CDB','rb').read(); s,n=entries(b)[0]; e=b[s*2048:(s+n)*2048]
    L={50:(None,'시작의 소문',17),56:('첫 번째 소문','「심령사진 양산 공원」',12),62:('두 번째 소문','「음악실의 M·F」',14),
       68:('세 번째 소문','「막차」',16),74:('네 번째 소문','「히나시로고교 7대 불가사의」',11),80:(None,'또 하나의 소문',17)}
    def mk(head,title,size):
        def fn(d,t):
            idx=idx_of(t); H,W=idx.shape; box=np.ones_like(idx,bool)
            pal=[int(x) for x in t['clut'][0]]; ls=np.array([lum(v) for v in pal[1:15]])
            order=1+np.argsort(ls)  # 어두운->밝은
            out=np.where(box,15,0).astype(np.uint8)
            if head:
                hi,hy=vtext(14,H,head,11,spacing=1); tl,ty=vtext(26,H,title,size,spacing=1)
                img=Image.new('L',(W,H)); img.paste(hi,(W-15,4)); img.paste(tl,(2,4+hy//3))
            else:
                tl,ty=vtext(W,H,title,size,spacing=2); img=Image.new('L',(W,H)); img.paste(tl,(0,(H-ty)//2))
            a=np.asarray(img).astype(float)/255
            lv=np.clip((a*len(order)).astype(int)-1,-1,len(order)-1)
            m=(lv>=0)&box
            out[m]=order[lv[m]]
            if (a>0.1)[~box].any(): print('경고: 상자 밖',title)
            set_idx(d,t,out)
        return fn
    return {0:patch_entry(e,{j:mk(*v) for j,v in L.items()})}
NANUM='../NanumSquareNeo-cBd.ttf'
def draw_lines(W,H,lines,font,size,center=True,lh=None,dy=0):
    f=ImageFont.truetype(font,size); im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    lh=lh or H//len(lines)
    for i,s in enumerate(lines):
        bb=dr.textbbox((0,0),s,font=f); w=bb[2]-bb[0]
        x=(W-w)//2-bb[0] if center else 1-bb[0]
        if w>W: print('경고: 폭 초과',s,w,W)
        y=i*lh+(lh-size)//2+dy
        dr.text((x,y),s,font=f,fill=255)
    return im
def relabel(lines,font=None,size=12,center=True,dy=0,thresh=False):
    font=font or G11
    def fn(d,t):
        idx=idx_of(t); H,W=idx.shape
        pal=[int(x) for x in t['clut'][0]]
        used,cnt=np.unique(idx,return_counts=True)
        bg=int(used[np.argmax(cnt)])
        others=[int(u) for u in used if u!=bg]
        if not others: return
        lb=lum(pal[bg])
        # 배경 대비 가장 먼 색 = 글자색, 나머지는 중간톤
        others.sort(key=lambda u:abs(lum(pal[u])-lb))
        img=draw_lines(W,H,lines,font,size,center,dy=dy)
        a=np.asarray(img).astype(float)/255
        out=np.full((H,W),bg,np.uint8)
        if thresh:
            out[a>0.5]=others[-1]
        else:
            levels=[(abs(lum(pal[u])-lb),u) for u in others]
            mx=levels[-1][0] or 1
            for yy,xx in zip(*np.nonzero(a>0.15)):
                tgt=a[yy,xx]*mx
                out[yy,xx]=min(levels,key=lambda l:abs(l[0]-tgt))[1]
        set_idx(d,t,out)
    return fn
def patch_file(b,mods):
    return patch_entry(b,mods)
MENU={0:['전리품 보기'],1:['창 색상'],2:['타이틀로'],
 3:['첫 번째 소문  심령사진 양산 공원'],4:['두 번째 소문  음악실의 M.F'],5:['세 번째 소문  막차'],
 6:['네 번째 소문  히나시로고교 7대 불가사의'],
 10:['I 공원  고베 다리'],11:['I 공원  화장실 앞'],12:['I 공원  한밤중의 큰 도리이'],13:['I 공원  주차장'],
 14:['M역 구내  여자 화장실'],15:['M역 구내  남자 화장실'],16:['M역 구내  육교'],17:['M역 구내  소바 가게'],
 18:['M역 구내  3번 홈'],19:['M역 구내  자판기'],20:['M역 구내  4번 홈'],21:['M역 구내  유야미가오카행'],
 22:['히나시로 고교  체육관 기구실'],23:['정수장에서 본 거리'],25:['조각관의 소리'],26:['고베 다리의 소리'],
 27:['한밤의 교내 방송'],28:['한밤의 피아노'],29:['도서실의 소리'],30:['방공호의 소리'],31:['I 공원  한낮의 큰 도리이']}
MEM={0:['세이브에 실패했습니다.'],1:['로드에 실패했습니다.'],2:['초기화에 실패했습니다.'],
 3:['메모리 카드에','1블록의','빈 공간이 없습니다'],4:['메모리 카드를','인식할 수 없습니다'],5:['메모리 카드를','교체해 주세요'],
 6:['이 메모리 카드는','사용할 수 없습니다'],7:['메모리 카드에','액세스 중입니다'],
 8:['메모리 카드가','초기화되지 않았습니다','초기화하시겠습니까?'],9:['예'],10:['아니요'],
 11:['이 메모리 카드에는','「트와일라잇 신드롬」','탐색편의 세이브 데이터가','없습니다'],
 12:['이대로 계속하면','메모리 카드에','액세스할 수 없습니다'],13:['메모리 카드를','교체하시겠습니까?'],
 14:['메모리 카드를','넣으시겠습니까?'],15:['메모리 카드를','넣어 주세요'],16:['탐색 준비 중'],17:['탐색 기록 중']}
def sinkou():
    out={}
    b=open('orig/DAT/SINKOU/MENUDAT.BIN','rb').read()
    mods={j:relabel(v) for j,v in MENU.items()}
    mods[7]=relabel(['시작'],SERIF,20); mods[8]=relabel(['준비'],SERIF,20)
    mods[9]=relabel(['『사진』'],SERIF,16); mods[24]=relabel(['『녹음』'],SERIF,16)
    out['DAT/SINKOU/MENUDAT.BIN']=patch_entry(b,mods)
    b=open('orig/DAT/SINKOU/MEMDAT.BIN','rb').read()
    out['DAT/SINKOU/MEMDAT.BIN']=patch_entry(b,{j:relabel(v) for j,v in MEM.items()})
    return out
