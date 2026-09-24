from sage.all import false
from matplotlib.style import context
import json
from pwn import *

host = "socket.cryptohack.org"
port = 13422

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

conn.recvline()

import time
start_time = time.perf_counter()

send({'option': 'encrypt'})
ct = recv()['ct']
ct = bytes.fromhex(ct)
# print(ct)

from tqdm import tqdm

def decrypt_block(block, prev_block, possible_char=b'0123456789abcdef'):
    pt = [0] * 16
    iv = [0] * 16
    for i in range(16):
        expected_padding = i+1
        found = False
        for char in tqdm(possible_char):
            for v in range(15 - i + 1, 16):
                iv[v] = pt[v] ^ prev_block[v] ^ expected_padding
            iv[15 - i] = char ^ prev_block[15 - i] ^ expected_padding
            # print(iv, chr(char))
            payload = bytes(iv) + block
            # send({'option': 'unpad', 'ct': payload.hex()})
            # validate = recv()['result']

            res = True
            for _ in range(15):
                send({'option': 'unpad', 'ct': payload.hex()})
                if not recv()['result']:
                    res = false
                    break
            
            if res:
                pt[15 - i] = char
                found = True
                break
            
        if not found:
            print('bagaimana mungkin')
            break
    return bytes(pt)

iv = ct[:16]
first = ct[16:32]
second = ct[32:]

pt1 = decrypt_block(first, iv)
pt2 = decrypt_block(second, first)

send({'option': 'check', 'message': (pt1+pt2).decode()})
print(recv())

end_time = time.perf_counter()
execution_time = end_time - start_time
print(f"Took {execution_time:.2f} seconds")

conn.close()