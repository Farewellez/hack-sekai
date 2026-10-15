def generate_basis(n):
    basis = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if basis[i]:
            basis[i*i::2*i] = [False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3, n, 2) if basis[i]]


def miller_rabin(n, b):
    """
    Miller Rabin test testing over all
    prime basis < b
    """
    basis = generate_basis(b)
    if n == 2 or n == 3:
        return basis

    if n % 2 == 0:
        return 0

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for b in basis:
        x = pow(b, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return 0
    return basis

# https://github.com/jvdsn/crypto-attacks/blob/master/attacks/pseudoprimes/miller_rabin.py
import logging
import os
import sys
from math import gcd

from sage.all import is_prime
from sage.all import kronecker
from sage.all import next_prime

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__)))))
if sys.path[1] != path:
    sys.path.insert(1, path)

def _generate_s(A, k):
    S = []
    for a in A:
        # Possible non-residues mod 4a of potential primes p
        Sa = set()
        for p in range(1, 4 * a, 2):
            if kronecker(a, p) == -1:
                Sa.add(p)

        # Subsets of Sa that meet the intersection requirement
        Sk = []
        for ki in k:
            assert gcd(ki, 4 * a) == 1
            Sk.append({pow(ki, -1, 4 * a) * (s + ki - 1) % (4 * a) for s in Sa})

        S.append(Sa.intersection(*Sk))

    return S

def fast_crt(X, M):
    x, m = X[0], M[0]
    for xi, mi in zip(X[1:], M[1:]):
        g = gcd(m, mi)
        if (xi - x) % g != 0:
            raise ValueError("Inconsistent")
        l = m * mi // g
        inv = pow(m // g, -1, mi // g)
        t = ((xi - x) // g * inv) % (mi // g)
        x = (x + m * t) % l
        m = l
    return x, m

# Brute forces a combination of residues from S by backtracking
# X already contains the remainders mod each k
# M already contains each k
def _backtrack(S, A, X, M, i):
    if i == len(S):
        return fast_crt(X, M)

    M.append(4 * A[i])
    for za in S[i]:
        X.append(za)
        try:
            fast_crt(X, M)
            z, m = _backtrack(S, A, X, M, i + 1)
            if z is not None and m is not None:
                return z, m
        except ValueError:
            pass
        X.pop()

    M.pop()
    return None, None


def generate_pseudoprime(A, k2=None, k3=None, min_bit_length=0):
    """
    Generates a pseudoprime of the form p1 * p2 * p3 which passes the Miller-Rabin primality test for the provided bases.
    More information: R. Albrecht M. et al., "Prime and Prejudice: Primality Testing Under Adversarial Conditions"
    :param A: the bases
    :param k2: the k2 value (default: next_prime(A[-1]))
    :param k3: the k3 value (default: next_prime(k2))
    :param min_bit_length: the minimum bit length of the generated pseudoprime (default: 0)
    :return: a tuple containing the pseudoprime n, as well as its 3 prime factors
    """
    A.sort()
    if k2 is None:
        k2 = int(next_prime(A[-1]))
    if k3 is None:
        k3 = int(next_prime(k2))
    while True:
        logging.info(f"Trying {k2 = } and {k3 = }...")
        X = [pow(-k3, -1, k2), pow(-k2, -1, k3)]
        M = [k2, k3]
        S = _generate_s(A, M)
        logging.info(f"{S = }")
        z, m = _backtrack(S, A, X, M, 0)
        if z and m:
            logging.info(f"Found residue {z} and modulus {m}")
            i = (2 ** (min_bit_length // 3)) // m
            while True:
                p1 = int(z + i * m)
                p2 = k2 * (p1 - 1) + 1
                p3 = k3 * (p1 - 1) + 1
                if is_prime(p1) and is_prime(p2) and is_prime(p3):
                    return p1 * p2 * p3, p1, p2, p3

                i += 1
        else:
            k3 = int(next_prime(k3))

basis = generate_basis(64)
p, p1, p2, p3 = generate_pseudoprime(basis, min_bit_length=615)
print(f"p : {p}")
print(f"p1: {p1}")
print(f"p2: {p2}")
print(f"p3: {p3}")

assert 600 < p.bit_length() <= 900, "bit length outside server window"

x1 = pow(p1, p-1, p)
x2 = pow(p2, p-1, p)
x3 = pow(p3, p-1, p)

x = {}
x[x1] = p1
x[x2] = p2
x[x3] = p3

a = x[max(x1,x2,x3)]

assert 1 <= a <= p

import json
import time
from pwn import *

# host = "127.0.0.1"
host = "socket.cryptohack.org"
port = 13385
context.log_level = 'error'

conn = remote(host, port)
conn.recvline()

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

send({"prime": p, "base": a})
conn.interactive()

conn.close()