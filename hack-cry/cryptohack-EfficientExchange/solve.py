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

# E: Y^2 = X^3 + 497*X + 1768 mod 9739
# G:(1804,5368)
# x(QA​)=4726, with your secret integer nB=6534.
a = 497
b = 1768
p = 9739
x_Qa = 4726
nB = 6534

# Y^2 = r_eq
# p ≡ 3 mod 4
# then:
# y = +- r_eq^(p+1//4)
r_eq = (pow(x_Qa,3) + a*x_Qa + b) % p
y_Qa = pow(r_eq, ((p+1)//4), p)

QA = (x_Qa, y_Qa)
shared_secret = scalar_multiplication(QA, a, b, p, nB)[0]
iv = "cd9da9f1c60925922377ea952afc212c"
ciphertext = "febcbe3a3414a730b125931dccf912d2239f3e969c4334d95ed0ec86f6449ad8"
flag = decrypt_flag(shared_secret, iv, ciphertext)
print(f"Flag: {flag}")