from sage.all import GF,Zmod, is_prime, factor, EllipticCurve, ZZ, inverse_mod

# Parameters
modulus = 13407807929942597099574024998205846127479365820592393377723561443721764030029777567070168776296793595356747829017949996650141749605031603191442486002224009
a = -3
b = 152961
order = 115792089237316195423570985008687907853233080465625507841270369819257950283813

if not is_prime(modulus):
    p = ZZ(factor(modulus)[0][0])
    print(f"Factors p: {p}")

Fn = Zmod(modulus)
Fp = GF(p)

En = EllipticCurve(Fn, [a,b])
Ep = EllipticCurve(Fp, [a,b])

def hensel_y(x):
    x = ZZ(x) % modulus
    rhs = x**3 + a*x + b

    assert Fp(rhs).is_square()

    y = ZZ(Fp(rhs).sqrt())
    assert y % p != 0

    t = (((rhs - y**2)//p) * inverse_mod(2*y, p)) % p
    y = (y + t*p) % modulus

    assert (y**2 - rhs) % modulus == 0
    return y

x0 = ZZ(1)
y0 = hensel_y(x0)

P = En(x0,y0)

import json
from pwn import *

host, port = "socket.cryptohack.org", 13417
conn = remote(host,port)
context.log_level = 'error'

conn.recvuntil(b'You have 30 seconds to submit the private key in decimal format.\n')

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

send({"option": "get_pubkey", "x0": str(x0)})
Q_x = ZZ(recv()["pubkey"])
# print(Q1,type(Q1))
# print(Q_x)

Q_y = hensel_y(Q_x)

Q = En(Q_x, Q_y)
print("recovered point Q...")

n = Ep.order()
assert n == order

P_kernel = n*P
Q_kernel = n*Q
print(f"P_kernel: {P_kernel}")
print(f"Q_kernel: {Q_kernel}")

Xp, Yp, Zp = map(ZZ, P_kernel)
Xq, Yq, Zq = map(ZZ, Q_kernel)

assert Xp % p == 0
assert Xp % modulus != 0

up = (Xp//p) % p
uq = (Xq//p) % p
print(f"found up and uq:")
print(f"up: {up}")
print(f"uq: {uq}")

k = (uq * pow(up,-1,p)) % p
d = min(k, p - k)
print(f"recovered d: {d}")

send({"option": "get_flag","privkey": int(d)})
flag = recv()["flag"]
print(f"Flag: {flag}")
# conn.interactive()

conn.close()