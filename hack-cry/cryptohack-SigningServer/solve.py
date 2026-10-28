import json
from pwn import *
from Crypto.Util.number import long_to_bytes

host = "socket.cryptohack.org"
port = 13374

conn = remote(host,port)
context.log_level = 'error'

# banner
conn.recvline()

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# get public key
send({"option": "get_pubkey"})
pub_data = recv()

N = pub_data["N"]
e = pub_data["e"]
print(f"N: {N}")
print(f"e: {e}")

# get secret
send({"option": "get_secret"})
secret = recv()["secret"]
print(f"c: {secret}")

# interesting
# signature = S (hex)
# message = m (hex)
# m_secret = secret**e mod N
# what if:
# X = k**e mod N; k = 7
# m1 = X * m_secret mod N
# how we build X scenario?
# m1 = (k**e) * m_secret mod N
# m1 = (k**e) * (secret**e) mod N
# m1 = (k * secret)**e mod N
# 
# S1 = m1**D mod N
# S1 = ((k * secret)**e) ** D mod N
# S1 = (k * secret) mod N
# S1 = (7 * secret) mod N
# S1 * 7**-1 = secret mod N
k = 7
X = pow(k,int(e,16),int(N,16))
m1 = (X * int(secret,16)) % int(N,16)

send({"option": "sign","msg": hex(m1)})
S1 = recv()["signature"]
print(f"S1: {S1}")

m = (int(S1,16) * pow(7,-1,int(N,16))) % int(N,16)
print(f"secret: {m}")

flag = long_to_bytes(m)
print(f"Flag: {flag.decode()}")

conn.close()