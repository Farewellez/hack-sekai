# ==================================================================================
# KNOWN EQUATION
# -> x ≡ 2 mod 5
# -> x ≡ 3 mod 11
# -> x ≡ 5 mod 17
# 
# KNOWN VAR:
# a = 2, 3, 5
# m = 5, 11, 17
# source solution: https://www.youtube.com/watch?v=e8DtzQkjOMQ&t=6s
# ==================================================================================
ai = [2, 3, 5]
mi = [5, 11, 17]

# ==================================================================================
# FINDING M, M1, M2, M3
# M  = m1 x m2 x m3 x ... x mi
# M1 = M/m1
# M2 = M/m2
# M3 = M/m3
# ==================================================================================
M = 1
Mi = []
for m in mi:
    M *= m
print(f"M: {M}")

for m in mi:
    Mi.append(M//m)
print(f"Mi: {Mi}")

# ==================================================================================
# FINDING M_i inverse
# M_i inverse = Mi x Mi^-1 = 1 mod mi for i in range mi and Mi
# ==================================================================================
Mi_inverse = []
for i in range(len(Mi)):
    Mi_inverse.append(pow(Mi[i], -1, mi[i]))
print(f"Mi inverse: {Mi_inverse}")

# ==================================================================================
# FINDING X VALUE
# X = sigma(ai.Mi.Mi_inverse) mod M
# ==================================================================================
flag = 0
for i in range(len(ai)):
    res = ai[i]*Mi[i]*Mi_inverse[i]
    flag += res

flag = flag % M
assert flag == 872, "wrong answer!!!"

print(f"correct answer: {flag}")