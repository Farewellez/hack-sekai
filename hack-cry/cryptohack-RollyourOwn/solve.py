import json
from pwnlib.tubes.remote import remote
from sympy import isprime
from pwn import *

# host = "127.0.0.1" # local
host = "socket.cryptohack.org"
port = 13403

conn = remote(host, port)
context.log_level = 'debug'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

q = conn.recvline().decode()[17:-1].strip().strip('"')
n = int(q,16)*int(q,16)
g = int(q,16) + 1 

print(f"n: {n}")
print(f"g: {g}")
assert pow(g,int(q,16),n) == 1

send({"g": hex(g), "n": hex(n)})
conn.recvuntil(b'Generated my public key: "')
pubkey = conn.recvuntil(b'\n', drop=True).decode().strip().strip('"')
print(f"Public key: {pubkey}")

x = (int(pubkey, 16)- 1) // int(q,16)
conn.recvuntil(b'What is my private key: ')
send({"x": hex(x)})
conn.interactive()

conn.close()