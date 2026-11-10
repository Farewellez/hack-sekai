from sage.all import *

# Efficient key exchange
nbits = 64
pbits = 256

def recover_small_dlog(Q, G, B=1<<nbits):
    for Qtry in (Q, -Q):
        try:
            return discrete_log(Qtry, G,ord=G.order(),operation='+',bounds=(0, B))
        except Exception:
            pass
    raise ValueError("bagaimana mungkin...")

# Curve parameters
p = 99061670249353652702595159229088680425828208953931838069069584252923270946291
a = 1
b = 4
E = EllipticCurve(GF(p), [a,b])
G = E(
    GF(p)(43190960452218023575787899214023014938926631792651638044680168600989609069200),
    GF(p)(20971936269255296908588589778128791635639992476076894152303569022736123671173)
)
Ax = 87360200456784002948566700858113190957688355783112995047798140117594305287669
Bx = 6082896373499126624029343293750138460137531774473450341235217699497602895121

# Elliptic Curve defined by 
# y^2 = x^3 + x + 4 over Finite Field of size 99061670249353652702595159229088680425828208953931838069069584252923270946291
eqA = (pow(Ax, 3, p) + Ax + 4) % p
Ay = pow(eqA, ((p+1)//4), p)
QA = E(Ax, Ay)
print(f"Public key alice: {QA}") 

eqB = (pow(Bx, 3, p) + Bx + 4) % p
By = pow(eqB, ((p+1)//4), p)
QB = E(Bx, By)
print(f"Public key bob: {QB}") 

# QA = [nA]*G
nA = recover_small_dlog(QA, G)
print(f"Secret key Alice: {nA}")

s = nA*QB
print(f"Shared Secret: {s}")

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

data = {'iv': 'ceb34a8c174d77136455971f08641cc5', 'encrypted_flag': 'b503bf04df71cfbd3f464aec2083e9b79c825803a4d4a43697889ad29eb75453'}
flag = decrypt_flag(tuple(s)[0], data["iv"], data["encrypted_flag"])
print(f"Flag: {flag}")