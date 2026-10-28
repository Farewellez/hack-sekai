import json
from pwn import *
from Crypto.Util.number import bytes_to_long
from pkcs1 import emsa_pkcs1_v15

host = "socket.cryptohack.org"
port = 13391

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

# get signature
send({"option": "get_signature"})
data = recv()

N = data["N"]
e = data["e"]
sign = data["signature"]
print()
print(f"N        : {N}")
print(f"e        : {e}")
print(f"signature: {sign}")

# known
# MSG = 'We are hyperreality and Jack and we own CryptoHack.org'
# DIGEST = [0x00] [0x01] [0xFF] ... [0xFF] [0x00] [MSG]
# signature = DIGEST ** D mod N
# calculated_digest = signature ** e mod N
# 
# in the other side
# message = input kita
# n, e = input kita
# DIGEST_input = [0x00] [0x01] [0xFF] ... [0xFF] [0x00] [message]
#
# interesting part
# misal e input = 1
# jadinya:
# target_digest = [0x00] [0x01] [0xFF] ... [0xFF] [0x00] [message_target]
# calculated_digest = SIGNATURE ** 1 mod N
# calculated_digest - SIGNATURE = k*N
# 
# target_digest equal SIGNATURE mod N
# target_digest - SIGNATURE = N
# SIGNATURE = target_digest + N
# N = target
target_msg = "I am Mallory and we own CryptoHack.org"
target_digest = emsa_pkcs1_v15.encode(target_msg.encode(), 256)

target_N = hex(int(sign,16) - bytes_to_long(target_digest))
target_e = 1

print()
print(f"target e     : {target_e}")
print(f"target digest: {bytes_to_long(target_digest)}")
print(f"target N     : {target_N}")

send({"option":"verify", "msg":target_msg , "N": target_N, "e": hex(target_e)})

res = recv()["msg"]
print(f"Flag: {res}")

conn.close()