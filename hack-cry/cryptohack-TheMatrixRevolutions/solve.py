from sage.all import true, random_vector, column_matrix
from sage.all import Matrix, GF, minimal_polynomial

P = 2
N = 150

def load_matrix(fname):
    data = open(fname, 'r').read().strip()
    rows = [list(map(int, row)) for row in data.splitlines()]
    return Matrix(GF(P), rows)

KEY_LENGTH = 128

G = load_matrix("generator.txt")
print(f"Dimension of G: {G.dimensions()}")

# A_priv = getPrime(149)
# B_priv = getPrime(149)
# A_priv and B_priv or a and b are missing...(cause its private)

# A_pub = G^A_priv
# B_pub = G^B_priv
# need to load the matrix, cause G is Matrix dimension 150 x 150
# then, 150^a or 150^b make A and B are matrix 150x150 too...
A_pub = load_matrix("alice.pub")
B_pub = load_matrix("bob.pub")
print(f"Dimension of G: {A_pub.dimensions()}")
print(f"Dimension of G: {B_pub.dimensions()}")

# shared_secret = A_pub^B_priv
# B_priv is still missing, so we can't recover shared_secret immedietly

# key = derive_aes_key(shared_secret)
# iv = urandom(16)
# cipher = AES.new(key, AES.MODE_CBC, iv)
# plaintext = pad(FLAG, 16)
# ciphertext = cipher.encrypt(plaintext)
# key is missing, we need shared secret to recover key
data = {"iv": "43f14157442d75142d0d4993e99a9582", "ciphertext": "22abc3b347ffef55ec82488e5b4a338da5af7ef1918ac46f95029a4d94ace4cb2700fa9aeb31e6a4facee2601e99dabd6f9a81494c55f011e9227c9a6ae8d802"}
iv = data["iv"]
ct = data["ciphertext"]

# minimal polynomial matrix G
# https://doc.sagemath.org/html/en/reference/matrices/sage/matrix/compute_J_ideal.html
min_poly_G = minimal_polynomial(G)
factored_poly = min_poly_G.factor()
print(f"Factored minimal polynom matrix G")
print(factored_poly)
# seems not work
# (x^61 + x^57 + x^55 + x^53 + x^51 + x^50 + x^47 + x^46 + x^45 + x^44 + x^43 + x^40 + x^34 + x^32 + x^31 + x^30 + x^28 + x^23 + x^21 + x^19 + x^13 + x^12 + x^11 + x^7 + x^4 + x^3 + x^2 + x + 1) * 
# (x^89 + x^84 + x^82 + x^80 + x^77 + x^76 + x^75 + x^74 + x^68 + x^67 + x^66 + x^64 + x^63 + x^62 + x^57 + x^53 + x^52 + x^51 + x^50 + x^43 + x^40 + x^39 + x^38 + x^36 + x^34 + x^33 + x^32 + x^31 + x^27 + x^24 + x^18 + x^17 + x^16 + x^14 + x^13 + x^12 + x^10 + x^9 + x^8 + x^7 + x^4 + x^3 + 1)
# we got f61(x) * f89(x) (polynom of degree 61 and polynom of degree 89)

# now we can search polynom c(x), so then target matrix = c(G)
F = GF(P)["x"]
x = F.gen()

def find_polynom_representation(target_matrix):
    while true:
        v = random_vector(GF(P), N)

        K_cols = []
        curr_v = v
        for i in range(N):
            K_cols.append(curr_v.list())
            curr_v = G*curr_v

        K = column_matrix(K_cols)

        if K.is_invertible():
            # K * c = target_matrix * v
            target_v = target_matrix * v
            c_coeff = K.solve_right(target_v)
            
            # convert array coeffisien into polynom object
            poly = sum(c_coeff[i] * x**i for i in range(N))
            return poly

cA_poly = find_polynom_representation(A_pub)
cB_poly = find_polynom_representation(B_pub)
print(f"Polynom A_pub:\n{cA_poly}")
print(f"Polynom B_pub:\n{cB_poly}")

# try solving 2 mini DLP problem using CRT and pari in sage
# last time we got f61(x) * f89(x) (polynom of degree 61 and polynom of degree 89)
# GF(2^61)
# x = G
# A_pub = cA(x)
# 
# x^a1 ≡ cA(x) mod (f61(x))
# x^a2 ≡ cA(x) mod (f89(x))

from sage.all import pari, crt

f61 = factored_poly[0][0]
f89 = factored_poly[1][0]

# convert polynom public key Alice and polynom f61 into finite field
gen61 = pari.ffgen(pari(f61))
target61 = pari(cA_poly).Polrev().subst('x', gen61)

# convert polynom f89 into finite field
gen89 = pari.ffgen(pari(f89))
target89 = pari(cA_poly).Polrev().subst('x', gen89)

# running fflog to find a1 and a2
# gen61^a1 = target61
# gen89^a2 = target98
a1 = int(pari.fflog(target61, gen61))
a2 = int(pari.fflog(target89, gen89))
print(f"a1: {a1}")
print(f"a2: {a2}")

# CRT
# Apriv ≡ a1 mod (2^61 - 1)
# Apriv ≡ a2 mod (2^89 - 1)
order61 = 2**61 - 1
order89 = 2**89 - 1

A_priv = crt([a1, a2], [order61, order89])
print(f"A_priv: {A_priv}")

# derive AES matrix key
from Crypto.Hash import SHA256
def derive_aes_key(M):
    mat_str = ''.join(str(x) for row in M for x in row)
    return SHA256.new(data=mat_str.encode()).digest()[:KEY_LENGTH]

shared_secret = B_pub**A_priv
KEY = derive_aes_key(shared_secret)
print(f"Key: {KEY.hex()}")

# decrypting...
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
cipher = AES.new(KEY, AES.MODE_CBC, bytes.fromhex(iv))
plaintext = unpad(cipher.decrypt(bytes.fromhex(ct)), 16)
print(f"Flag: {plaintext.decode()}")