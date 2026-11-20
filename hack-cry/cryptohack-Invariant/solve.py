# M = input
# h = ENC(h XOR M) XOR M
# 
# target h = 0
# 0 = ENC(h XOR M) XOR M
# M = ENC(h XOR M)

import itertools
import json
from hashlib import sha512

class MyCipher:
    __NR = 31
    __SB = [13, 14, 0, 1, 5, 10, 7, 6, 11, 3, 9, 12, 15, 8, 2, 4]
    __SR = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

    def __init__(self, key):
        self.__RK = int(key.hex(), 16)
        self.__subkeys = [[(self.__RK >> (16 * j + i)) & 1 for i in range(16)]
                          for j in range(self.__NR + 1)]

    def __xorAll(self, v):
        res = 0
        for x in v:
            res ^= x
        return res

    def encrypt(self, plaintext):
        assert len(plaintext) == 8, "Error: the plaintext must contains 64 bits."

        S = [int(_, 16) for _ in list(plaintext.hex())]

        for r in range(self.__NR):
            S = [S[i] ^ self.__subkeys[r][i] for i in range(16)]
            S = [self.__SB[S[self.__SR[i]]] for i in range(16)]
            X = [self.__xorAll(S[i:i + 4]) for i in range(0, 16, 4)]
            S = [X[c] ^ S[4 * c + r]
                 for c, r in itertools.product(range(4), range(4))]

        S = [S[i] ^ self.__subkeys[self.__NR][i] for i in range(16)]
        return bytes.fromhex("".join("{:x}".format(_) for _ in S))


class MyHash:
    def __init__(self, content):
        self.cipher = MyCipher(sha512(content).digest())
        self.h = b"\x00" * 8
        self._update(content)

    def _update(self, content):
        while len(content) % 8:
            content += b"\x00"

        for i in range(0, len(content), 8):
            # print(f"Before XOR     : {self.h}")
            self.h = bytes(x ^ y for x, y in zip(self.h, content[i:i+8]))
            # print(f"After h XOR msg: {self.h.hex()}")
            
            # print(f"\nBefore ENC  : {self.h.hex()}")
            self.h = self.cipher.encrypt(self.h)
            # print(f"After ENC   : {self.h.hex()}")
            
            # print(f"\nBefore XOR     : {self.h.hex()}")
            self.h = bytes(x ^ y for x, y in zip(self.h, content[i:i+8]))
            # print(f"After h XOR msg: {self.h.hex()}")

    def digest(self):
        return self.h

    def hexdigest(self):
        return self.h.hex()

class Challenge:
    def __init__(self):
        self.counter = 0
        self.before_input = "Can you cryptanalyse this cryptohash?\n"
        self.exit = True

    def hash(self, data):
        self.counter += 1
        return MyHash(data).digest()

# outputnya unik
c = Challenge()
msg = bytes.fromhex("6677666677776776")
tag = c.hash(msg)
print(tag.hex())

print(f"Start BF,,,")
target = None
for mask in range(1 << 32):
    nibble = [] 
    for i in range(32): # need 8 byte of input
        bit = (mask >> i) & 1
        value = 6 | bit
        nibble.append(str(value))
    
    msg = bytes.fromhex("".join(nibble))
    
    tag = MyHash(msg).digest()
    if tag == (b'\x00'*8):
        print(f"Found Message: {msg.hex()}")
        target = msg
        break

from pwn import *

host, port = "socket.cryptohack.org", 13393
conn = remote(host, port)
context.log_level = 'error'

# banner
conn.recvuntil(b'Can you cryptanalyse this cryptohash?\n')
def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

send({"option": "hash", "data": target.hex()})
res = recv()
hash = res["hash"]
info = res["info"]
flag = res["flag"]
print(f"Hash: {hash}")
print(f"Info: {info}")
print(f"Flag: {flag}")

# conn.interactive()

conn.close()