from collections import namedtuple

Point = namedtuple("Point", "x y")

gx = 8742397231329873984594235438374590234800923467289367269837473862487362482
gy = 225987949353410341392975247044711665782695329311463646299187580326445253608
G = Point(gx, gy)

P = Point(x=2582928974243465355371953056699793745022552378548418288211138499777818633265, y=2421683573446497972507172385881793260176370025964652384676141384239699096612)
p = 4368590184733545720227961182704359358435747188309319510520316493183539079703

# y^2 = x^3 + ax + b mod p
# eq -> # y^2 - x^3 mod p = ax + b
eqG = (pow(G.y,2,p) - pow(G.x,3,p)) % p
eqP = (pow(P.y,2,p) - pow(P.x,3,p)) % p

# elimination b
a = ((eqG - eqP) * pow(G.x - P.x, -1, p)) % p
print(f"a = {a}")

# substitution a
b = (eqG - (a*G.x)) % p
print(f"b = {b}")

# calculate discriminant
discriminant = (-16 * (4*pow(a,3,p) + 27*pow(b,2,p))) % p
assert discriminant == 0, "its safe..."

from sage.all import GF, PolynomialRing, discrete_log
from Crypto.Util.number import long_to_bytes

R = PolynomialRing(GF(p), 'x')
x = R.gen(0)
f = x**3 + a*x + b
roots = f.roots()
r1 = int(roots[0][0])
r2 = int(roots[1][0])
print(f"roots f: {roots}")

F = GF(p)
d = F(r2 - r1)

if d.is_square():
    print("Split node → grup ≅ F_p^*, orde p−1")
    sd = F(d).sqrt()

    def phi(x, y):
        num = F(y) + sd * (F(x) - r2)
        den = F(y) - sd * (F(x) - r2)
        return num / den
    tG, tP = phi(gx, gy), phi(P.x, P.y)
else:
    print("Non-split node → grup ≅ norm-1 di F_{p²}^*, orde p+1")
    # F_{p²} dengan generator w, w² = d
    R = PolynomialRing(F, 'w')
    w = R.gen()
    
    F2 = GF(p**2, 'w', modulus=w**2 - d)
    w = F2.gen()

    def phi(x, y):
        X, Y = F2(x), F2(y)
        return (Y + w*(X - r2)) / (Y - w*(X - r2))
    tG, tP = phi(gx, gy), phi(P.x, P.y)

k = discrete_log(tP, tG)
print("k =", k)
print(long_to_bytes(int(k)))