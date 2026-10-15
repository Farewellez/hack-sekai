e = 65537 
p = 17
q = 23
m = 12

N = p*q
c = pow(m,e,N)
print(c)
