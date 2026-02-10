import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 7500))
print("Listening on 127.0.0.1:7500")

while True:
    data, addr = sock.recvfrom(4096)
    print(f"From {addr}: {data!r}")