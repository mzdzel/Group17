import hashlib
import socket
import time

host = 'localhost'
port = 12345

age = 25
r = 12345

start_time = time.time()

v = hashlib.sha256(str(age + r).encode('utf-8')).hexdigest()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

sock.sendall(v.encode('utf-8'))
sock.sendall(str(age).encode('utf-8'))

sock.close()

end_time = time.time()

print("Alice's runtime:", end_time - start_time, "seconds")
