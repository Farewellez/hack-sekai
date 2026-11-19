from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def bxor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def hash(data):
    data = pad(data, 16)
    out = b"\x00" * 16
    for i in range(0, len(data), 16):
        blk = data[i:i+16]
        out = bxor(AES.new(blk, AES.MODE_ECB).encrypt(out), out)
    return out

# simulation
key = b'A'*16
# server will produce:
# key(16) + (msg + padding)(16)
# 
# in here:
# blk = data[i:i+16]
# out = bxor(AES.new(blk, AES.MODE_ECB).encrypt(out), out)
# server just used secret key once, next block, it used out message
msg = b"admin"
sign = hash(msg)
print(f"Valid Sign: {sign.hex()}")

# now forge it
# new msg = b"admin=True"
extension = b"admin=True"
forged_msg = msg + (bytes([11])*11) + extension

forged_tag = sign
extension = pad(extension,16)
for i in range(0, len(extension), 16):
    blk = extension[i:i+16]
    forged_tag = bxor(AES.new(blk, AES.MODE_ECB).encrypt(forged_tag), forged_tag)

forged_tag.hex() == hash(forged_msg).hex()

import json
import re
from pwn import *

host, port = "socket.cryptohack.org",13388
conn = remote(host, port)
context.log_level = 'error'

conn.recvuntil(b"You'll never forge my signatures!\n")
def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

send({"option": "sign", "message": msg.hex()})
valid_tag = bytes.fromhex(recv()["signature"])
print(f"Collected valid tag: {valid_tag.hex()}")

forged_msg = msg + (bytes([11])*11) + extension

forged_tag = valid_tag
extension = pad(extension,16)
for i in range(0, len(extension), 16):
    blk = extension[i:i+16]
    forged_tag = bxor(AES.new(blk, AES.MODE_ECB).encrypt(forged_tag), forged_tag)
print(f"Collected forged tag: {forged_tag.hex()}")

send({"option": "get_flag", "signature": forged_tag.hex(), "message": forged_msg.hex()})
res = recv()["flag"]
match = re.search(r"crypto\{.*?\}", res)
if match:
    flag = match.group(0)
    print(f"Flag: {flag}")
# conn.interactive()

conn.close()