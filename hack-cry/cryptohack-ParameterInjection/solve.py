import json
from pwn import *

host = "socket.cryptohack.org"
port = 13371

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# Alice public key
conn.recvuntil(b'Intercepted from Alice: ')
resA = recv()

p = resA["p"]
g = resA["g"]
A = resA["A"]

print(F"Alice public key")
print(f"p: {p}")
print(f"g: {g}")
print(f"A: {A}")

# trying to be a good boy
send({"p": p, "g": g, "A": A})

# Bob public key
conn.recvuntil(b'Intercepted from Bob: ')
resB = recv()

print(F"Bob public key")
print(resB["B"])
resB["B"] = "0x1"

# trying to be a bad boy
send(resB)

# s = 1
conn.recvuntil(b"Intercepted from Alice: ")
res = recv()
s = 1
iv = res["iv"]
ct = res["encrypted_flag"]

conn.close()

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
        return unpad(plaintext, 16).decode('ascii')
    else:
        return plaintext.decode('ascii')

message = decrypt_flag(s, iv, ct)
print(f"Flag: {message}")