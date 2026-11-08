# E: Y**2 = X**3 + 497X + 1768 mod 9739
P=(493,5564)
Q=(1539,4742)
R=(4403,5202)
a, b = 497, 1768
p = 9739

def calculate_s(P, Q, a, b, p):
    if P == Q:
        s = (3*(P[0]**2) + a) * pow(2*P[1],-1,p)
        return s % p
    else:
        s = (Q[1] - P[1]) * pow((Q[0] - P[0]),-1,p)
        return s % p

# P + P = 2P (Point Doubling)
s = calculate_s(P,P, a, b, p)
xpp = (s**2 - P[0] - P[0]) % p
ypp = (s*(P[0] - xpp) - P[1]) % p
P_P = (xpp, ypp)
# print(P_P)

# Q + R = Q_R (Point Addition)
s = calculate_s(Q, R, a, b, p)
xqr = (s**2 - Q[0] - R[0]) % p
yqr = (s*(Q[0] - xqr) - Q[1]) % p
Q_R = (xqr, yqr)

s = calculate_s(P_P, Q_R, a, b, p)
Sx = (s**2 - P_P[0] - Q_R[0]) % p
Sy = (s*(P_P[0] - Sx) - P_P[1]) % p
S = (Sx, Sy)

assert pow(Sy,2,p) == (Sx**3 + a*Sx + b) % p, "somethings wrong..."
flag = f"crypto{{{S[0]},{S[1]}}}"
print(flag)