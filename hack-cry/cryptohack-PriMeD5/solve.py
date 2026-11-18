import hashlib
from math import gcd
from Crypto.Util.number import long_to_bytes, bytes_to_long,isPrime

x = "4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa200a8284bf36e8e4b55b35f427593d849676da0d1555d8360fb5f07fea2"
y = "4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa202a8284bf36e8e4b55b35f427593d849676da0d1d55d8360fb5f07fea2"

print("x : ", bytes_to_long(bytes.fromhex(x)))

print("md5(x) : ", hashlib.md5(bytes.fromhex(x)).hexdigest())
print("md5(y) : ", hashlib.md5(bytes.fromhex(y)).hexdigest())

z = 1

xx = 0
yy = 0

while True:
    # append 1s till prime
    xx = bytes_to_long(bytes.fromhex(x) + long_to_bytes(z))
    yy = bytes_to_long(bytes.fromhex(y) + long_to_bytes(z))
    if isPrime(xx) and not isPrime(yy):
        break
    z += 2

print("x+z :", xx, xx.bit_length())
print("y+z :", yy, yy.bit_length())

print("md5(x+z) : ", hashlib.md5(long_to_bytes(xx)).hexdigest())
print("md5(y+z) : ", hashlib.md5(long_to_bytes(yy)).hexdigest())

for q in [3, 5, 7, 11, 13, 17, 19, 23, 31]:
    if yy % q == 0 and yy != q:
        a = yy // q
        print("Found divisor:", q)
        print("gcd =", gcd(a, yy))
        break

import json
from pwn import *

host, port = "socket.cryptohack.org", 13392
conn = remote(host, port)
context.log_level = 'error'

# banner
conn.recvuntil(b'Primality checking is expensive so I made a service that signs primes, allowing anyone to quickly check if a number is prime\n')
def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

send({"option": "sign", "prime":str(xx)})
sign = recv()["signature"]
print(f"signature: {sign}")

send({"option": "check", "signature": sign, "prime":str(yy), "a": str(a)})
res = recv()["msg"]

match = re.search(r'crypto\{.*?\}', res)
if match:
    flag = match.group(0)
    print(f"Flag: {flag}")

# conn.interactive()

conn.close()