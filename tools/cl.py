import sys,socket
code=open(sys.argv[1],encoding='utf-8').read() if len(sys.argv)>1 and sys.argv[1]!='-' else sys.stdin.read()
c=socket.create_connection(('127.0.0.1',5577)); c.sendall(code.encode('utf-8')+b'\0')
d=b''
while True:
    k=c.recv(65536)
    if not k: break
    d+=k
sys.stdout.buffer.write(d)
