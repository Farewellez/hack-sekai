from sage.all import *

N = Integer(882564595536224140639625987659416029426239230804614613279163)
e = 65537
c = 77578995801157823671636298847186723593814843845525223303932

F = N.factor()
p,q = [f[0] for f in F]
print(f"p: {p}")
print(f"q: {q}")

assert p*q == N

phi_n = (p-1)*(q-1)
print(f"phi(N): {phi_n}")

d = pow(e,-1,phi_n)
m = pow(c,d,N)
print(f"Flag: {m}")