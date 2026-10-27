import json
from pwn import *
from Crypto.Util.number import long_to_bytes
from sage.all import PolynomialRing, Zmod

# host = "127.0.0.1"
host = "socket.cryptohack.org"
port = 13386

conn = remote(host, port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line


# encrypted_0 = pad_msg^e mod N
# encrypted_1 = N
# pad_var = (a, b)
# pad_msg = a*m+b

# ct0 = (a1*m+b1)^e mod N
# ct1 = (a2*m+b2)^e mod N
# karena m itu factor dari ct0 dan ct1, jadi kita bisa gcd(ct1,ct0) cuman pake versi polinomial gcd 
conn.recvline()
send({"option":"get_flag"})
res0 = recv()
ct0 = res0["encrypted_flag"]
N   = res0["modulus"]
padd0 = res0["padding"]
print()
print(f"ct0     : {ct0}")
print(f"N       : {N}")
print(f"padding : {padd0}")

send({"option":"get_flag"})

res1 = recv()
ct1 = res1["encrypted_flag"]
N   = res1["modulus"]
padd1 = res1["padding"]
print()
print(f"ct1     : {ct1}")
print(f"N       : {N}")
print(f"padding : {padd1}")

def poly_gcd(a,b):
    while b != 0:
        a,b = b, a % b
    return a.monic()

a1,b1 = padd0
a2,b2 = padd1

R = PolynomialRing(Zmod(N), 'm')
m = R.gen()

f = (a1*m+b1)**11 - ct0
g = (a2*m+b2)**11 - ct1

# di sini bentuknya itu x - m, jadi agar m (hasil polinomial gcd) positif maka perlu dikalikan -1
res = poly_gcd(f,g)
m = int(-res.coefficients()[0]) # kalikan minus
print(m, type(m))
print(long_to_bytes(m))

conn.close()