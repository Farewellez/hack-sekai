from sage.all import *
from string import ascii_lowercase, ascii_uppercase

# x = var('x', domain=ZZ)
# leq1 = x + 2*x**2 + x**3
# leq2 = x + x**2 + x**3

# # nihil
# # eq_sol = solve(leq2==100, x)
# # print(eq_sol)

# for i in range(-6,6):
#     print(leq2(x=i), "for", "i =", i)

x0 = var('x0', domain=ZZ)
eq0 = x0**4 - 150*x0**3 + 4389*x0**2 - 43000*x0**1 + 131100
eq0 = solve(eq0==0, x0)
# print(eq0)

x1 = var('x1', domain=ZZ)
eq1 = x1**10 - 177*x1**9 + 9143*x1**8 - 228909*x1**7 + 3264597*x1**6 - 28298835*x1**5 + 152170893*x1**4 - 502513551*x1**3 + 974729862*x1**2 - 995312448*x1**1 + 396179424
eq1 = solve(eq1==0, x1)
# print(eq1)

x2 = var('x2', domain=ZZ)
eq2 = x2**10 - 196*x2**9 + 12537*x2**8 - 397764*x2**7 + 7189071*x2**6 - 77789724*x2**5+ 506733203*x2**4 - 1941451916*x2**3 + 4165661988*x2**2 - 4501832400*x2 + 1841875200
eq2 = solve(eq2==0, x2)
# print(eq2)

x3 = var('x3', domain=ZZ)
eq3 = x3**5 - 153*x3**4 + 5317*x3**3 - 77199*x3**2 + 510274*x3**1 - 1269840
eq3 = solve(eq3==0, x3)
# print(eq3)

x4 = var('x4', domain=ZZ)
eq4 = x4**8 - 194*x4**7 + 11791*x4**6 - 352754*x4**5 + 6011644*x4**4 - 61295576*x4**3 + 370272864*x4**2 -  1222050816*x4**1 + 1696757760
eq4 = solve(eq4==0, x4)
# print(eq4)

x5 = var('x5', domain=ZZ)
eq5 = x5**6 - 169*x5**5 + 7702*x5**4 - 153082*x5**3 + 1477573*x5**2 - 6672349*x5**1 + 11042724 
eq5 = solve(eq5==0, x5)
# print(eq5)

x6 = var('x6', domain=ZZ)
eq6 = x6**8 - 202*x6**7 + 12936*x6**6 - 406082*x6**5 + 7170059*x6**4 - 74124708*x6**3 + 439747164*x6**2 - 1365683328*x6**1 + 1701311040
eq6 = solve(eq6==0, x6)
# print(eq6)

x7 = var('x7', domain=ZZ)
eq7 = x7**9 - 206*x7**8 + 13919*x7**7 - 467924*x7**6 + 8975099*x7**5 - 102829454*x7**4 + 699732361*x7**3 - 2673468816*x7**2 + 4956440220*x7**1 - 2888395200
eq7 = solve(eq7==0, x7)
# print(eq7)

eq = eq0 + eq1 + eq2 + eq3 + eq4 + eq5 + eq6 + eq7
# print(eq)

printtable = [ord(c) for c in (ascii_lowercase + ascii_uppercase)]
secret = ""
for num in eq:
    if num in printtable:
        secret += chr(num)

print(f"Secret: {secret}")