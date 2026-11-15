import json
import re
from fastecdsa.point import Point
from fastecdsa.curve import P256
from sage.all import *

def sign_point(g, d):
        return g * d

G = P256.G
N = P256.q
assert G.x, G.y == [0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                    0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5]

target_d = 2
target_host = "www.bing.com"
target_curve = "secp256r1"
target_generator = [G.x, G.y]
target_pubkey = Point(0x3B827FF5E8EA151E6E51F8D0ABF08D90F571914A595891F9998A5BD49DFA3531, 0xAB61705C502CA0F7AA127DEC096B2BBDC9BD3B4281808B3740C320810888592A, curve=P256)
newG = sign_point(target_pubkey, pow(target_d,-1,N))

from pwn import *

host, port = "socket.cryptohack.org", 13382
conn = remote(host, port)
context.log_level = 'error'

conn.recvuntil(b'Welcome to my secure search engine backed by trusted certificate library!\n')

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

obj = {
    "private_key": target_d,
    "host": target_host,
    "curve": target_curve,
    "generator": (newG.x,newG.y),
}

send(obj)
msg = conn.recvline()

conn.close()

match = re.search(rb"about (\S+)", msg)
flag = match.group(1).decode()[:-1]
print(f"Flag: {flag}")