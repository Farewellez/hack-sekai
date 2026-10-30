import json
from pwn import *

host = "socket.cryptohack.org"
port = 13379

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# pick supported DH-bit
conn.recvuntil(b"Intercepted from Alice: ")
print("Intercepting DH-bit choice...")
choice = recv()["supported"]
print(f"Normal choice: {choice}")

# ruin the choice
choice = list([choice[-1]])
print(f"Ruined choice: {choice}")
send({"supported": choice})

# Bob reply
conn.recvuntil(b"Intercepted from Bob: ")
chosen = recv()
send(chosen)

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
# public key Alice
conn.recvuntil(b'Intercepted from Alice: ')
resC = recv()
iv = resC["iv"]
ct = resC["encrypted_flag"]
print(f"iv: {iv}")
print(f"ct: {ct}")

conn.close()

from sympy.ntheory import discrete_log
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

a = discrete_log(int(p,16),int(A,16),int(g,16))
s = pow(int(B,16),a,int(p,16))

message = decrypt_flag(s, iv, ct)
print(f"Flag: {message.decode()}")