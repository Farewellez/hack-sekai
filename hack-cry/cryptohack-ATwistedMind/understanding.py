from sage.all import GF, EllipticCurve, is_prime, factor

# Parameters
p = 2**192 - 237
a = -3
b = 1379137549983732744405137513333094987949371790433997718123
order = 6277101735386680763835789423072729104060819681027498877478

F = GF(p)
E = EllipticCurve(F, [a,b])

print("Curve:", E)
print("p is prime:", is_prime(p))
print("Group order:", E.order())
print("Given order:", order)
print("Same?", E.order() == order)

print()

x0 = F(1)
rhs = x0**3 + x0*a + b

print("x0:", x0)
print("RHS:", rhs)
print("Is square?", rhs.is_square())

x0 = F(2)
rhs = x0**3 + x0*a + b

print("x0:", x0)
print("RHS:", rhs)
print("Is square?", rhs.is_square())

print()

Et = EllipticCurve(F, [a, -b])

x0 = F(1)

# Cek kurva asli
rhs = x0**3 + a*x0 + b
print("Original curve:", rhs.is_square())

# Cek quadratic twist
# f(x) itu bukan QR, jadi -f(x) itu QR
xt = -x0
rhs_twist = xt**3 + a*xt - b
print("Twist:", rhs_twist.is_square())

yt = rhs_twist.sqrt()
Pt = Et(xt, yt)
print("Point on twist:", Pt)
print("Point order:", Pt.order())

print()

# Quadratic twist
Et = EllipticCurve(F, [a, -b])

x0 = F(1)
xt = -x0

# Mencari koordinat y pada twist
rhs = xt**3 + a*xt - b
yt = rhs.sqrt()

# Membentuk titik
Pt = Et(xt, yt)

n = Pt.order()
factors = factor(n)

print("Point:", Pt)
print("Point order:", n)
print("Factorization:", factor(n))
print("Point order bits:", n.nbits())

for prime, exponent in list(factor(n)):
    print(
        f"Prime: {prime}, "
        f"Exponent: {exponent}, "
        f"Bits: {prime.nbits()}"
    )

print()

q = list(factor(n))[-1][0]
P_small = q * Pt

m = n // q

print("Original order:", n)
print("New order:", P_small.order())
print("Expected order:", m)
print("New factorization:", factor(m))
print("Order bits:", m.nbits())

assert P_small.order() == m


Psmall = q * Pt
m = Psmall.order()

x0_query = -Psmall[0]

print()

print("Psmall:", Psmall)
print("Point order:", m)
print("x0 for server:", int(x0_query))

rhs = x0_query**3 + a*x0_query + b

assert not rhs.is_square()
