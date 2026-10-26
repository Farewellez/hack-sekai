from sage.all import *
from Crypto.Util.number import long_to_bytes

n = Integer(984994081290620368062168960884976209711107645166770780785733)
e = 65537
ct = 948553474947320504624302879933619818331484350431616834086273

F = [f[0] for f in n.factor()]
p,q = F
print(f"N-bit          : {n.bit_length()}")
print(f"Factor         : {F}")
print(f"p              : {F[0]}")
print(f"q              : {F[1]}")

assert p*q == n

phiN = (p-1)*(q-1)
d = pow(e,-1,phiN)
m = pow(ct,d,n)
print(f"Flag: {long_to_bytes(m)}")