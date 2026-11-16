import json
import hashlib
from pwn import *
from Crypto.Util.number import bytes_to_long
from ecdsa.ecdsa import Public_key, Private_key, Signature, numbertheory, generator_192
from sage.all import *

g = generator_192
n = g.order()

host, port = "socket.cryptohack.org",13381
conn = remote(host,port)
context.log_level = 'error'

conn.recvuntil(b'Welcome to ProSign 3. You can sign_time or verify.\n')

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

obj1 = {"option": "sign_time"}
send(obj1)

res1 = recv()
msg1 = res1["msg"]
r1 = int(res1["r"],16)
s1 = int(res1["s"],16)
print(f"Message 1  : {msg1}")
print(f"Message int: {int.from_bytes(msg1.encode())}")
print(f"r1         : {r1}")
print(f"s1         : {s1}")

obj2 = {"option": "sign_time"}
send(obj2)

res2 = recv()
msg2 = res2["msg"]
r2 = int(res2["r"],16)
s2 = int(res2["s"],16)
print(f"Message 2: {msg2}")
print(f"Message int: {int.from_bytes(msg2.encode())}")
print(f"r2       : {r2}")
print(f"s2       : {s2}")

h1_bytes = hashlib.sha1(msg1.encode()).digest()
h2_bytes = hashlib.sha1(msg2.encode()).digest()

sig1 = Signature(r1, s1)
sig2 = Signature(r2, s2)

candidate_points = sig1.recover_public_keys(int.from_bytes(h1_bytes), g)
recovered_pubkey = None
for point in candidate_points:
    if point.verifies(int.from_bytes(h2_bytes,'big'), sig2):
        recovered_pubkey = point
        break

if recovered_pubkey:
    print("Public Key Successfully Recovered!")
    print(f"X: {hex(recovered_pubkey.point.x())}")
    print(f"Y: {hex(recovered_pubkey.point.y())}")
else:
    print("Failed to recover public key. Ensure m1 and m2 are hashed integers.")

privkey = None
for k in range(1, 60):
    d = ((s1 * k - int.from_bytes(h1_bytes, 'big')) * numbertheory.inverse_mod(r1, n)) % n

    if d * g == recovered_pubkey.point:
        privkey = Private_key(recovered_pubkey, d)
        print(f"Found k: {k}")
        print(f"Found d: {privkey}")
        break

target_msg = "unlock"
hsh = int.from_bytes(hashlib.sha1(target_msg.encode()).digest(),'big')
sig = privkey.sign(hsh, k)

last_obj = {"option": "verify", "msg": target_msg, "r": hex(sig.r)[2:], "s": hex(sig.s)[2:]}
send(last_obj)
flag = recv()["flag"]
# conn.interactive()

conn.close()

print(f"Flag: {flag}")