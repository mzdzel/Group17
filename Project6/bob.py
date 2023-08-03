import hashlib
import socket
import time

host = 'localhost'
port = 12345

start_time = time.time()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)

conn, addr = sock.accept()

v = conn.recv(64).decode('utf-8')
age = int(conn.recv(64).decode('utf-8'))

r = 54321
v_prime = hashlib.sha256(str(age + r).encode('utf-8')).hexdigest()

if v == v_prime:
    print("Alice's age has been verified!")
else:
    print("Alice's age could not be verified.")

conn.close()
sock.close()

end_time = time.time()

print("Bob's runtime:", end_time - start_time, "seconds")
