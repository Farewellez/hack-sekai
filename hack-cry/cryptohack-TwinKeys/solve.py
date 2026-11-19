# h1 = md5(k1)
# h2 = md5(k2)

# h1 = magic1 XOR (h2 XOR (XOR(h2, XOR(h1,h2)), h2))
# h1 = magic1 XOR (h2 XOR (XOR(h2, XOR(h1,h2)), h2))

# from pathlib import Path

# KEY_START = b"CryptoHack Secure Safe"
# assert len(KEY_START) == 22

# p1 = bytes([KEY_START[0] ^ 1])
# p2 = KEY_START

# def align(data):
#     return data + b"\x00" * (-len(data) % 64)

# Path("p1.bin").write_bytes(align(p1))
# Path("p2.bin").write_bytes(align(p2))

with open("./ipc_workdir/collision1.bin", "rb") as f1:
    coll1 = f1.read()

with open("./ipc_workdir/collision2.bin", "rb") as f2:
    coll2 = f2.read()

print(coll1)
print(coll2)
print(coll1 == coll2)

import json
import re
from pwn import *

host, port = "socket.cryptohack.org", 13397
conn = remote(host, port)
context.log_level = 'error'

# banner
conn.recvuntil(b'Can you help find our lost keys to unlock the safe?\n')
def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

send({"option": "insert_key", "key": coll1.hex()})
res = recv()["msg"]
if "inserted" in res:
    send({"option": "insert_key", "key": coll2.hex()})

send({"option": "unlock"})
conn.recvline()
res = recv()["msg"]
print(res)
match = re.search(r"crypto\{.*?\}",res)
if match:
    flag = match.group(0)
    print(f"Flag: {flag}")
# conn.interactive()

conn.close()