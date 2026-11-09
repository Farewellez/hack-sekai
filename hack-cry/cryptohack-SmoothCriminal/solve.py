from collections import namedtuple
from Crypto.Util.number import inverse
from sage.all import EllipticCurve,GF

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

# Define the curve
p = 310717010502520989590157367261876774703
a = 2
b = 3

E = EllipticCurve(GF(p), [a,b])
print(E.order())

# Generator
g_x = 179210853392303317793440285562762725654
g_y = 105268671499942631758568591033409611165
G = E(g_x, g_y)
print(G.x, G.y)

p_x = 280810182131414898730378982766101210916
p_y = 291506490768054478159835604632710368904
P = E(p_x, p_y)

b_x = 272640099140026426377756188075937988094
b_y = 51062462309521034358726608268084433317
B = (b_x, b_y)

n = P.log(G)
s = scalar_multiplication(B, a, b, p, n)

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib


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
        return unpad(plaintext, 16).decode('ascii')
    else:
        return plaintext.decode('ascii')

data = {'iv': '07e2628b590095a5e332d397b8a59aa7', 'encrypted_flag': '8220b7c47b36777a737f5ef9caa2814cf20c1c1ef496ec21a9b4833da24a008d0870d3ac3a6ad80065c138a2ed6136af'}
flag = decrypt_flag(s[0], data["iv"], data["encrypted_flag"])
print(f"Flag: {flag}")