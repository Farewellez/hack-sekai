from sage.all import *

P = 2
N = 50
E = 31337

def load_matrix(fname):
    data = open(fname, 'r').read().strip()
    rows = [list(map(int, row)) for row in data.splitlines()]
    return Matrix(GF(P), rows)

# C**L = Identity
C = load_matrix("./flag_403b981c77d39217c20390c1729b15f0.enc")
# print(C)
L = C.multiplicative_order()

if (C**L).is_one():
    print(f"we got mult order matrix C (ciphertext): {L}")

# E * D equivalent 1 mod L
# D = E**-1 mod L
D = inverse_mod(E, L)
print(f"D: {D}")

M = C**D
print(f"M: {M}")

bits = []
for col in range(N):
    for row in range(N):
        bits.append(int(M[row, col]))

bin_flag = "".join(str(b) for b in bits)
flag = b"".join([bytes([int(bin_flag[i:i+8],2)]) for i in range(0,len(bin_flag),8)])
print(flag)