from sage.all import GF, EllipticCurve
from math import gcd
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

def point_addition(P, Q, a, b, p):
    # print(P)
    # print(Q)
    if P == Q:
        s = (3*(P[0]**2) + a) * pow(2*P[1],-1,p)
    else:
        s = (Q[1] - P[1]) * pow((Q[0] - P[0]),-1,p)
    
    x = (s**2 - P[0] - Q[0]) % p
    y = (s*(P[0] - x) - P[1]) % p
    return (x,y)

def scalar_multiplication(P, a, b, p, n):
    Q = P
    R = None
    
    while n > 0:
        if n % 2 == 1:
            if R == None:
                R = Q
            else:
                R = point_addition(R, Q, a, b, p)

        # print(Q)
        Q = point_addition(Q, Q, a, b, p)
        n = n // 2

        if n <= 0:
            break
    
    return R

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
        return unpad(plaintext, 16).decode()
    else:
        return plaintext.decode()

# Define Curve params
p = 1331169830894825846283645180581
a = -35
b = 98
E = EllipticCurve(GF(p), [a,b])

G = E(479691812266187139164535778017, 568535594075310466177352868412,)
A = E(1110072782478160369250829345256, 800079550745409318906383650948)
B = E(1290982289093010194550717223760, 762857612860564354370535420319)
data = {'iv': 'eac58c26203c04f68d63dc2c58d79aca', 'encrypted_flag': 'bb9ecbd3662d0671fd222ccb07e27b5500f304e3621a6f8e9c815bc8e4e6ee6ebc718ce9ca115cb4e41acb90dbcabb0d'}

Gn = G.order()
k = 1
while p**k % Gn != 1:
    k += 1
print("Found k:", k)

Ek = EllipticCurve(GF(p ** k), [a, b])
Gk = Ek(G)
Ak = Ek(A)
Rk = Ek.random_point()

m = Rk.order()
d = gcd(m, Gn)
Tk = (m // d) * Rk
assert Tk.order() == d
assert (Gn*Tk).is_zero()

g = Gk.weil_pairing(Tk, Gn)
q = Ak.weil_pairing(Tk, Gn)

nA = q.log(g)
print(f"Alice private key: {nA}")

s = scalar_multiplication(B,a,b,p,nA)

flag = decrypt_flag(s[0], data["iv"], data["encrypted_flag"])
print(f"Flag: {flag}")