import json
import os
from pwn import *
from Crypto.Util.Padding import pad
from tqdm import tqdm

# local
# host = "127.0.0.1"
# remote
host = "socket.cryptohack.org"
port = 13437

conn = remote(host, port)
context.log_level = 'info'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

token_line = conn.recvline()
token_data = json.loads(token_line.decode())
original_ct = bytes.fromhex(token_data["token"])
C1 = original_ct[:16]   # blok pertama ciphertext asli

def decrypted(block, prev):
    pt = [0] * 16
    iv = [0] * 16
    
    for i in range(16):
        expected = i + 1
        for char in tqdm(range(256), desc=f"byte-{15-i}", leave=False):
            for v in range(15 - i + 1, 16):
                iv[v] = pt[v] ^ prev[v] ^ expected
            iv[15 - i] = char ^  prev[15 - i] ^ expected

            payloads = bytes(iv) + block
            send({"ciphertext": payloads.hex()})
            
            res = recv()["good_pad"]
            if res:
                pt[15 - i] = char
                break
    
    return bytes(pt)


ADMIN = "0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204"

suffix = b'", "user_id": "' + ADMIN.encode() + b'"}'
padded = pad(suffix, 16)

print(f"padded suffix (raw): {padded}")
print(f"padded suffix (hex): {padded.hex()}")

blocks = [padded[i:i+16] for i in range(0,len(padded),16)]
print(f"block pt's length: {len(blocks)}")

forged_blocks = [None] * (len(blocks) + 1)
forged_blocks[-1] = os.urandom(16)

for i in range(len(blocks) - 1, -1, -1):
    decrypt = decrypted(forged_blocks[i + 1], b"\x00" * 16)
    forged_blocks[i] = bytes(x ^ y for x,y in zip(decrypt, blocks[i]))
    log.info(f"block saat ini: {forged_blocks[i].hex()}")

ct = C1 + b''.join(forged_blocks)
send({"ciphertext": ct.hex()})
res = recv()
print(res)

conn.close()