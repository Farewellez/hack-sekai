import json
from pwn import *

host, port = "socket.cryptohack.org",13405
conn = remote(host, port)
context.log_level = 'error'

# banner
conn.recvuntil(b'Please send two hex encoded messages m1, m2 formatted in JSON: ')

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

bs = 32
m1 = b'a'
m2 = b'a' + (bytes([31])*31)

send({"m1":m1.hex(),"m2":m2.hex()})
res = recv()["flag"]
match = re.search(r'crypto\{.*?\}', res)
if match:
    flag = match.group(0)
    print(f"Flag: {flag}")
conn.close()