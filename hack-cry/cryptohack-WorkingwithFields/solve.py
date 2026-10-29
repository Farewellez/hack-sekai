p = 991
g = 209

# g*d eqv 1 mod p
# d eqv g**-1 mod p
d = pow(g,-1,p)
print(d)