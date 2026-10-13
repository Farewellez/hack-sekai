import json
import os
from pwn import *
from tqdm import tqdm
from Crypto.Util.Padding import pad, unpad

# host = "127.0.0.1"
host = "socket.cryptohack.org"
port = 13436

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

def decrypt_block(block, prev_block):
    pt = [0] * 16
    iv = [0] * 16
    for i in range(16):
        expected_padding = i+1
        for char in tqdm(range(256), desc=f"byte-{15-i}", leave=False):
            for v in range(15 - i + 1, 16):
                iv[v] = pt[v] ^ prev_block[v] ^ expected_padding
            iv[15 - i] = char ^ prev_block[15 - i] ^ expected_padding

            payload = bytes(iv) + block

            send({"ciphertext": payload.hex()})
            res = recv()["good_pad"]
            if res:
                pt[15 - i] = char
                break
    return bytes(pt)

ADMINS = "0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204"
pt = json.dumps({"user_id": ADMINS}).encode()
padded = pad(pt, 16)
print(f"pt: {padded.hex()}")

blocks = [padded[i:i+16] for i in range(0,len(padded),16)]
print(f"block length: {len(blocks)}")

forged_blocks = [None] * len(blocks)
forged_blocks[-1] = os.urandom(16)

for i in range(len(blocks) - 1, -1, -1):
    decrypted = decrypt_block(forged_blocks[i], b"\x00" * 16)
    if i > 0:
        forged_blocks[i - 1] = bytes(x ^ y for x,y in zip(decrypted, blocks[i]))
    else:
        iv = bytes(x ^ y for x, y in zip(decrypted, blocks[0]))

ct = iv + b''.join(forged_blocks)
send({"ciphertext": ct.hex()})
res = recv()
print(res)

conn.interactive()

conn.close()