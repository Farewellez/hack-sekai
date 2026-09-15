from pwn import *
import json

from Crypto.Util.strxor import strxor
def xor(a, b):
    b = (b * (len(a) // len(b) + 1))[:len(a)]
    return strxor(a, b)

conn = remote('socket.cryptohack.org', 13421)
# conn = remote('127.0.0.1', 13421)

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

conn.recvline() # the before_input

import time
start_time = time.perf_counter()

send({'option': 'encrypt'})
ct = recv()['ct']
ct = bytes.fromhex(ct)

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
            send({'option': 'unpad', 'ct': payload.hex()})
            res = recv()['result']
            # print(res)

            if res:
                pt[15 - i] = char
                # print('\npt is now', pt)
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
