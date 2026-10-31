"""번역 검증: python tools/chk.py NN  (text/split/NN.json vs text/kop/NN.json)"""
import sys,os,json,re
sys.path.insert(0,os.path.dirname(__file__))
import kfont
LIMIT=272
_w={}
def cw(ch):
    if ch not in _w:
        if ch=='　': _w[ch]=16
        elif ord(ch)>=0x3000 and not (0xac00<=ord(ch)<=0xd7a3): _w[ch]=16
        else: _w[ch]=kfont.render(ch)[1]
    return _w[ch]
TAG=re.compile(r'\{[^}]*\}')
def check(ja,ko):
    errs=[]
    if TAG.findall(ja)!=TAG.findall(ko): errs.append('태그 불일치')
    if ja.count('\n')!=ko.count('\n'): errs.append('줄바꿈 수 불일치 ja=%d ko=%d'%(ja.count('\n'),ko.count('\n')))
    for seg in re.split(r'\n|\{8500\}|\{8600\}',ko):
        t=TAG.sub('',seg); w=sum(cw(c) for c in t)
        if w>LIMIT: errs.append('줄 너무 김(%dpx>%d): %s'%(w,LIMIT,t))
    if re.search(r'[\u3040-\u30fa\u30fc-\u30ff\u4e00-\u9fff]',TAG.sub('',ko)): errs.append('일본어 문자 남음')
    return errs
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    n=sys.argv[1]
    ja={x['id']:x['ja'] for x in json.load(open('text/split/%s.json'%n,encoding='utf-8'))}
    ko={x['id']:x['ko'] for x in json.load(open('text/kop/%s.json'%n,encoding='utf-8'))}
    bad=0
    for i in ja:
        if i not in ko: print(i,'누락'); bad+=1; continue
        e=check(ja[i],ko[i])
        for m in e: print(i,m)
        bad+=bool(e)
    print('문제 블록:',bad,'/',len(ja))
