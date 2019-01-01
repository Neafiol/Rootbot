import socket
from array import array

sock = socket.socket()
sock.connect(('localhost', 9090))
a=132231
b=12

sock.send(str(a).encode('utf-8'))
d1 = sock.recv(1024)

sock.send(str(b).encode('utf-8'))
d2 = sock.recv(1024)


d1=d1.decode("utf-8")
d2=d2.decode("utf-8")
print (float(d1)/float(d2))
sock.close()