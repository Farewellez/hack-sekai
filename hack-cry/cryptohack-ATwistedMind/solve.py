from sage.all import GF, EllipticCurve, factor, crt 

# Parameters
p = 2**192 - 237
a = -3
b = 1379137549983732744405137513333094987949371790433997718123
order = 6277101735386680763835789423072729104060819681027498877478

F = GF(p)
E = EllipticCurve(F, [a,b])

# quadratic twist
Et = EllipticCurve(F, [a,-b])
x0 = F(1)
xt = -x0

# Mencari koordinat y pada twist
rhs = xt**3 + a*xt - b
yt = rhs.sqrt()

# Membentuk titik
Pt = Et(xt, yt)

n = Pt.order()
factors = factor(n)

q = list(factor(n))[-1][0]
P_small = q * Pt

m = P_small.order()
x0_query = -P_small[0]

assert not (x0_query**3 + a*x0_query + b).is_square()
print("safe...")

import json
from pwn import *

host, port = "socket.cryptohack.org", 13416
conn = remote(host,port)
context.log_level = 'error'

conn.recvuntil(b'You have 120 seconds to submit the private key in decimal format.\n')

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# ambil titik 1 dulu
send({"option": "get_pubkey", "x0": str(x0_query)})
Q1 = recv()["pubkey"]
Q1xt = F(-Q1)

# Mencari koordinat y pada twist
rhs = Q1xt**3 + a*Q1xt - b
assert rhs.is_square()

Q1yt = rhs.sqrt()
print(f"recovered point 1...")

# Membentuk titik
Q1t = Et(Q1xt, Q1yt)
assert m * Q1t == Et(0)

d1 = Q1t.log(P_small)
print(d1)

Pe = E.lift_x(F(2))
nE = E.order()

factors = factor(nE)

qE = list(factor(nE))[-1][0]
P_Esmall = qE * Pe

mE = P_Esmall.order()

assert mE > 1
x1_query = P_Esmall[0]

# ambil titik 2
send({"option": "get_pubkey", "x0": str(x1_query)})
Q2x = F(recv()["pubkey"])

rhs = Q2x**3 + a*Q2x + b
assert rhs.is_square()

Q2y = rhs.sqrt()
print(f"recovered point 2...")

Q2 = E(Q2x, Q2y)
assert mE * Q2 == E(0)

d2 = Q2.log(P_Esmall)

from itertools import product
from sage.all import ZZ, lcm

bound = ZZ(order) // 2
M = lcm(m, mE)

print("Combined modulus bits:", M.nbits())
print("Private key bound bits:", bound.nbits())

candidates = set()

for s1, s2 in product([1, -1], repeat=2):
    r1 = (s1 * d1) % m
    r2 = (s2 * d2) % mE

    candidate = ZZ(crt(r1, r2, m, mE)) % M

    if 0 <= candidate <= bound:
        candidates.add(candidate)

assert len(candidates) == 1, "ambiguous candidates..."

privkey = candidates.pop()

send({"option": "get_flag","privkey": str(privkey)})

res = recv()["flag"]
print(f"Flag: {res}")

conn.close()