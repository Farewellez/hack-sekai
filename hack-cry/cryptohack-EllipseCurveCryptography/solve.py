# Ellipse Curve Cryptography
# ===================================
# KNOWN VARIABLES
#
# p      = modulus
# D      = scalar
# A      = Alice's public key
# B      = Bob's public key
# ct     = iv and ciphertext
# G      = generator point
# source:
# https://chat.deepseek.com/share/5w6hbt4fkx9xf3epjp
# https://en.wikipedia.org/wiki/Pell%27s_equation
# https://github.com/pwang00/Cryptographic-Attacks/blob/master/Public%20Key/Diffie%20Hellman/pohlig_hellman.sage
# https://en.wikipedia.org/wiki/Pollard%27s_p_%E2%88%92_1_algorithm
# ===================================
from collections import namedtuple
# Create a simple Point class to represent the affine points.
Point = namedtuple("Point", "x y")

p = 173754216895752892448109692432341061254596347285717132408796456167143559
D = 529
G = Point(29394812077144852405795385333766317269085018265469771684226884125940148,
        94108086667844986046802106544375316173742538919949485639896613738390948)
A = Point(x=155781055760279718382374741001148850818103179141959728567110540865590463, y=73794785561346677848810778233901832813072697504335306937799336126503714)
B = Point(x=171226959585314864221294077932510094779925634276949970785138593200069419, y=54353971839516652938533335476115503436865545966356461292708042305317630)
ct = {'iv': '64bc75c8b38017e1397c46f85d4e332b', 'encrypted_flag': '13e4d200708b786d8f7c3bd2dc5de0201f0d7879192e6603d7c5d6b963e1df2943e3ff75f7fda9c30a92171bbbc5acbf'}

# ======================================================================
# SANITY CHECK
# - checking if D has a root (perfect square)
# - checking if p - 1 is smooth by factoring p - 1; all prime factors
#   of p - 1 are <= 988228543 ~ 2^30, so it is potentially exploitable
#   with Pohlig-Hellman
# ======================================================================
from math import sqrt
d_root = int(sqrt(D))
print(f"D's root: {d_root}")

from sympy import factorint
f: dict = factorint(p-1)
max_prime = max(f.keys())
print(f"factor p - 1: {f}")
print(f"max prime   : {max_prime}")

if max_prime < pow(2, 40):
    print("potential")
else:
    print("too big")
    exit()

# ======================================================================
# MAP CONIC POINTS INTO F_p^*
# Since D is a perfect square, the conic is isomorphic to F_p^*, so it is
# possible to convert scalar multiplication into ordinary exponentiation
# in F_p^*
# ======================================================================
def phi(P):
    return (P.x + 23*(P.y)) % p

# ======================================================================
# SOLVE DLP WITH BSGS + POHLIG-HELLMAN
# Recover Alice's private key n_a from her public key A = n_a * G by
# solving the DLP in F_p^* using Pohlig-Hellman (per-prime-factor BSGS)
# and CRT to combine the residues.
# note: this script must be run with SageMath (.sage file)
# ======================================================================
def BSGS(g, A, n, G):
    m = ceil(sqrt(n)) + 1
    log_table = {}

    cur = G(1)                          # g^0 = 1 in field G
    for j in range(m):
        log_table[cur] = j
        cur = cur * g

    inv = g ** (-m)
    y = G(A)                            # ensure it is a field element

    for i in range(m):
        if y in log_table:              # O(1) lookup, not a loop
            return i * m + log_table[y]
        y = y * inv

    return None

def pohlig_hellman(g, A, F, debug=True):
    """ Attempts to use Pohlig-Hellman to compute discrete logarithm of A = g^a mod p"""
    
    # This code is pretty clunky, naive, and unoptimized at the moment, but it works.

    p = F.order() 
    factors = [p_i ^ e_i for (p_i, e_i) in factor(F.order() - 1)]
    crt_array = []

    if debug:
        print("[x] Factored |F_p| = p - 1 into %s" % factors)

    for p_i in factors:
        g_i = F(pow(g,(p - 1) // p_i, p))
        h_i = F(pow(A, (p - 1) // p_i, p))
        x_i = BSGS(g_i, h_i, p_i, F)
        if debug and x_i != None:
            print("[x] Found discrete logarithm %d for factor %d" % (x_i, p_i))
            crt_array += [x_i]
        elif x_i == None:
            print("[] Did not find discrete logarithm for factor %d" % p_i)


    return crt(crt_array, factors)

g = phi(G)
a = phi(A)
F = GF(p)
n_a = pohlig_hellman(g, a, F)
print(f"Got Alice's secret key: {n_a}")

# ======================================================================
# RECOVER SHARED SECRET
# using functions from the challenge source code
# ======================================================================
def point_addition(P, Q):
    Rx = (P.x*Q.x + D*P.y*Q.y) % p
    Ry = (P.x*Q.y + P.y*Q.x) % p
    return Point(Rx, Ry)

def scalar_multiplication(P, n):
    Q = Point(1, 0)
    while n > 0:
        if n % 2 == 1:
            Q = point_addition(Q, P)
        P = point_addition(P, P)
        n = n//2
    return Q

def gen_shared_secret(P, d):
    return scalar_multiplication(P, d).x

from hashlib import sha1
from Crypto.Cipher import AES

shared_secret = gen_shared_secret(B, n_a)
key = sha1(str(shared_secret).encode('ascii')).digest()[:16]
iv = bytes.fromhex(ct['iv'])

# ======================================================================
# DECRYPT AND PRINT THE FLAG
# ======================================================================
cipher = AES.new(key, AES.MODE_CBC, iv)
pt = cipher.decrypt(bytes.fromhex(ct['encrypted_flag']))
print(f"Flag: {pt.decode()[:-1]}")