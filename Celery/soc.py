import socket
import math

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(2)

while True:
    conn, addr = sock.accept()
    print('connected:', addr)
    while True:
        data = conn.recv(2024)
        if not data:
            break
        s=data.decode("utf-8")
        n=int(s)
        n=math.log(n,10)
        s=str(n)
        print(s)

        conn.send(s.encode('utf-8'))
conn.close()

