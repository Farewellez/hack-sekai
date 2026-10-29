import json
from pwn import *
from Crypto.Util.number import bytes_to_long

host = "socket.cryptohack.org"
port = 13376

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

# get public variable
send({"option": "get_pubkey"})
pub_var = recv()

N = pub_var["N"]
e = pub_var["e"]
print(f"N: {N}")
print(f"e: {e}")

# testing signing feature with own message
m_testing = b"krgtw=True".hex()
send({"option": "sign", "msg": m_testing})

sign_testing = recv()["signature"]

print()
print(f"Testing message  :{m_testing}")
print(f"Testing signtaure:{sign_testing}")

# testing verify feature with testing signature
send({"option": "verify", "msg": m_testing, "signature": sign_testing})
res_test = recv()["response"]
print(F"Response: {res_test}")

# sekarang gimana cara ngakalin si admin=true
# known:
# N  = moduli
# e  = public exponent
# m1 = our input (hex)
# S1 = m1 ** d mod N
# S2 = m2 ** d mod N
# 
# interesting:
# S(m1*m2) = S1 * S2 mod N
# m_admin = b"admin=True" -> bytes to long
# m1 = 0x2
# m2 = m_admin * m1**-1 mod N
# 
# jadinya:
# S(m1*m2) = S1 * S2 mod N
# S(m1*m2) = (m1 ** d) * (m2 ** d) mod N
# S(m1*m2) = (0x2 ** d) * ((m_admin * m1**-1) ** d) mod N
# S(m1*m2) = (0x2 ** d) * (m_admin ** d) * (0x2**-1)**d mod N
# S(m1*m2) = (m_admin ** d) mod N
# S1 * S2  mod N = (m_admin ** d)

# crafting
m_admin = bytes_to_long(b"admin=True")
m1 = bytes([2]).hex()
m2 = m_admin * pow(int(m1,16),-1,int(N,16))

# get signature S1 and S2
send({"option": "sign", "msg": m1})
S1 = recv()["signature"]
send({"option": "sign", "msg": hex(m2)[2:]})
S2 = recv()["signature"]

print()
print(f"Signature 1: {S1}")
print(f"Signature 2: {S2}")

valid_signature = hex((int(S1,16) * int(S2,16)) % int(N,16))[2:]
valid_message = b"admin=True".hex()
send({"option": "verify", "msg": valid_message, "signature": valid_signature})

res = recv()["response"]
print(f"Flag: {res}")
# conn.interactive()

conn.close()