from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util import number
from sympy import isprime
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

# generating p-smooth
p_smooth = 2
while p_smooth.bit_length() < 2048 - 16:
    p_smooth *= number.getPrime(16)

while True:
    q = number.getPrime(16)
    if isprime(p_smooth * q + 1):
        p_payload = p_smooth * q + 1
        break

print(f"Payload: {hex(p_payload)}")

import json
from pwn import *

host = "socket.cryptohack.org"
port = 13378

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
print("Intercepting Alice...")
conn.recvuntil(b'Intercepted from Alice: ')
resA = recv()
p = resA["p"]
g = resA["g"]
A = resA["A"]
print(f"p: {p}")
print(f"g: {g}")
print(f"A: {A}")

# public key Bob
print("Intercepting Bob...")
conn.recvuntil(b'Intercepted from Bob: ')
resB = recv()
B = resB["B"]
print(f"B: {B}")

# ciphertext
print("Intercepting Alice...")
conn.recvuntil(b'Intercepted from Alice: ')
resC = recv()
iv = resC["iv"]
ct = resC["encrypted"]
print(f"iv: {iv}")
print(f"ct: {ct}")

# sending param to Bob
print("Sending to Bob...")
print("Send: ", {"p": hex(p_payload), "g": g, "A": {A}})
conn.recvuntil(b'Bob connects to you, send him some parameters: ')
send({"p": hex(p_payload), "g": g, "A": A})

# public key Bob
print("Bob replying (public key)...")
conn.recvuntil(b'Bob says to you: ')
resB2 = recv()
B2 = int(resB2["B"],16)
print(f"B2: {B2}")

# Bob reply ciphertext
print("Bob replying (ciphertext)...")
conn.recvuntil( b'Bob says to you: ')
resC2 = recv()
iv2 = resC2["iv"]
ct2 = resC2["encrypted"]
print(f"iv2: {iv2}")
print(f"ct2: {ct2}")

# conn.interactive()

conn.close()

from sage.all import discrete_log, Mod
b = discrete_log(Mod(B2, p_payload), Mod(2, p_payload))
s1 = pow(int(A,16),b,int(p,16))
s2 = pow(int(A,16),b,p_payload)

# message 1
message1 = decrypt_flag(s1, iv, ct)
print(message1)

# message 2
message2 = decrypt_flag(s2, iv2, ct2)
print(message2)