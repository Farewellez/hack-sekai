from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

def is_pkcs7_padded(message):
    padding = message[-message[-1]:]
    return all(padding[i] == len(padding) for i in range(0, len(padding)))

def decrypt_flag(shared_secret: int, iv: str, ciphertext: str):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Decrypt flag
    ciphertext = bytes.fromhex(ciphertext)
    iv = bytes.fromhex(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    if is_pkcs7_padded(plaintext):
        return unpad(plaintext, 16)
    else:
        return plaintext

import json
from pwn import *

host = "socket.cryptohack.org"
port = 13380

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# public key Alice
conn.recvuntil(b'Intercepted from Alice: ')
resA = recv()
p = resA["p"]
g = resA["g"]
A = resA["A"]
print(f"p: {p}")
print(f"g: {g}")
print(f"A: {A}")

# public key Bob
conn.recvuntil(b'Intercepted from Bob: ')
resB = recv()
B = resB["B"]
print(f"B: {B}")

# ciphertext
conn.recvuntil(b'Intercepted from Alice: ')
resC = recv()
iv = resC["iv"]
ct = resC["encrypted"]
print(f"iv: {iv}")
print(f"ct: {ct}")

# conn.interactive()

conn.close()

a = int(A,16) * pow(int(g,16),-1,int(p,16))
s = (a * int(B,16)) % int(p,16)

# decrypt ct
message = decrypt_flag(s, iv, ct)
print(f"Flag: {message.decode()}")