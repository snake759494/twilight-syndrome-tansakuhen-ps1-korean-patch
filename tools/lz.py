# 게임 압축 (CAP*.EXE 0x8007681c)
def dec(b,o=0):
    out=bytearray()
    while True:
        c=b[o]; o+=1
        if c<0x80:
            n=c+1; out+=b[o:o+n]; o+=n
        elif c<0xc0:
            n=c-0x7d; out+=bytes([b[o]])*n; o+=1
        elif c<0xe0:
            n=c-0xbc; d=b[o]<<8|b[o+1]; o+=2; s=len(out)-d
            for k in range(n): out.append(out[s+k])
        elif c<0xf0:
            n=c-0xdc; st=b[o]; v=b[o+1]; o+=2
            for k in range(n): out.append(v&0xff); v+=st
        elif c==0xff: return bytes(out),o
def comp(data):
    # 리터럴/런/역참조 탐욕 압축
    out=bytearray(); lit=bytearray(); i=0; n=len(data)
    def flush():
        nonlocal lit
        while lit:
            k=lit[:128]; out.append(len(k)-1); out.extend(k); lit=lit[128:]
    while i<n:
        r=1
        while i+r<n and data[i+r]==data[i] and r<66: r+=1
        bl=0;bd=0
        lo=max(0,i-0xffff)
        if r<35:
            j=data.rfind(data[i:i+4],lo,i+3) if i+4<=n else -1
            # 간단 탐색
            for s in range(i-1,lo-1,-1):
                if data[s]!=data[i]: continue
                L=0
                while i+L<n and L<35 and data[s+L]==data[i+L]: L+=1
                if L>bl: bl=L;bd=i-s
                if bl==35: break
                if i-s>4096: break
        if r>=3 and r>=bl:
            flush(); out+=bytes([0x7d+r,data[i]]); i+=r
        elif bl>=4:
            flush(); out+=bytes([0xbc+bl,bd>>8,bd&0xff]); i+=bl
        else:
            lit.append(data[i]); i+=1
    flush(); out.append(0xff); return bytes(out)
def comp_fit(d,target):
    """압축 결과 길이를 정확히 target으로 맞춤(뒷부분 리터럴 패딩)"""
    c=comp(d)
    if len(c)==target: return c
    if len(c)>target: raise ValueError('too big')
    n=len(d)
    def mn(k):
        A=len(comp(d[:k]))-1 if k else 0; m=n-k
        return A,A+m+(m+127)//128+1
    lo,hi=0,n   # mn(k)<=target 인 가장 작은 k
    while lo<hi:
        mid=(lo+hi)//2
        if mn(mid)[1]<=target: hi=mid
        else: lo=mid+1
    for k in list(range(lo,min(n,lo+64)+1))+list(range(lo-1,max(-1,lo-64),-1)):
        A,mnv=mn(k); m=n-k
        if mnv<=target and A+2*m+1>=target:
            head=comp(d[:k])[:-1] if k else b''
            nch=(m+127)//128+(target-mnv)
            sizes=[1]*nch; rem=m-nch
            for j in range(nch):
                a=min(127,rem); sizes[j]+=a; rem-=a
            out=bytearray(head); i=0
            for s_ in sizes: out.append(s_-1); out+=d[k+i:k+i+s_]; i+=s_
            out.append(0xff); assert len(out)==target and dec(bytes(out))[0]==d
            return bytes(out)
    raise ValueError('fit fail')
