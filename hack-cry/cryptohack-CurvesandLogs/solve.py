# E: Y^2 = X^3 + 497*X + 1768 mod 9739
# G:(1804,5368)
# QA=(815,3190)
# nB=1829

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

G = (1804,5368)
QA = (815,3190)
nB = 1829
a = 497
b = 1768
p = 9739

s = scalar_multiplication(QA, a, b, p, nB)
assert pow(s[1],2,p) == (s[0]**3 + a*s[0] + b) % p

from hashlib import sha1
obj = sha1(str(s[0]).encode())
flag = f"crypto{{{obj.hexdigest()}}}"
print(f"Flag: {flag}")