# simulasi
import os
from hashlib import sha256

FLAG = b"crypto{???????????????????????????????}"

def _xor(a, b):
    return bytes([_a ^ _b for _a, _b in zip(a, b)])

def _and(a, b):
    return bytes([_a & _b for _a, _b in zip(a, b)])

def shuffle(mixed_and, mixed_xor):
    return bytes([mixed_xor[i%len(mixed_xor)] for i in mixed_and])

msg = b"\x00"*(len(FLAG))
mixed_and = _and(FLAG, msg)
print(mixed_and)

mixed_xor = _xor(_xor(FLAG, msg), os.urandom(len(FLAG)))
print(mixed_xor)

very_mixed = shuffle(mixed_and, mixed_xor)
print(very_mixed)

super_mixed = sha256(very_mixed).hexdigest()
print(super_mixed)

for i in range(256):
    guess = bytes([i])*len(FLAG)
    # not_mixed = shuffle(b"\x00"*len(FLAG), guess)
    tag = sha256(guess).hexdigest()
    if tag == super_mixed:
        print(f"Found {guess}")
        break

assert very_mixed == guess


import json
from pwn import *

host, port = "socket.cryptohack.org",13402
# host, port = "127.0.0.1",13402
conn = remote(host, port)
context.log_level = 'error'

conn.recvuntil(b"Oh no, how are you going to unmix this?\n")

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

N = len(FLAG)
flag = b""
for L in range(N):
    recovered = 0
    for bit in range(8):
        mask = 1 << bit

        msg = bytearray(N)
        msg[L] = mask

        send({"option": "mix", "data": msg.hex()})
        server_tag = recv()["mixed"]

        found = any(sha256(bytes([i])*N).hexdigest() == server_tag for i in range(256))
        if not found:
            recovered |= mask
            
    print(f"recovered biner: {recovered:08b} = {bytes([recovered])}")
    flag += bytes([recovered])
# conn.interactive()
conn.close()

print(f"Flag: {flag.decode()}")