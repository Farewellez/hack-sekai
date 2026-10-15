from math import isqrt
from fpylll import IntegerMatrix, LLL

x = 1350995397927355657956786955603012410260017344805998076702828160316695004588429433
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103]

SCALE = 16**64 
n = len(PRIMES)
W = 1000

alpha = [isqrt(p * (SCALE * W) ** 2) for p in PRIMES]

M = IntegerMatrix(n + 1, n + 1)

for i in range(n):
    M[i, i] = W
    M[i, n] = alpha[i]

M[n, n] = -x * W

LLL.reduction(M)
for i in range(n + 1):
    r = [M[i, j] for j in range(n + 1)]
    for sign in (1, -1):
        coeffs = [sign * v // W for v in r[:n]]
        if all(0 <= c <= 255 for c in coeffs) and any(coeffs):
            print(bytes(coeffs))