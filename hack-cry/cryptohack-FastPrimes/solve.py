import math
from Crypto.PublicKey import RSA

with open("./key_17a08b7040db46308f8b9a19894f9f95.pem", "r") as f:
    data = RSA.import_key(f.read())

N = data.n
e = data.e
print(f"N: {N}")
print(f"e: {e}")


primes = []


def sieve(maximum=10000):
    # In general Sieve of Sundaram, produces primes smaller
    # than (2*x + 2) for a number given number x. Since
    # we want primes smaller than maximum, we reduce maximum to half
    # This array is used to separate numbers of the form
    # i+j+2ij from others where 1 <= i <= j
    marked = [False]*(int(maximum/2)+1)

    # Main logic of Sundaram. Mark all numbers which
    # do not generate prime number by doing 2*i+1
    for i in range(1, int((math.sqrt(maximum)-1)/2)+1):
        for j in range(((i*(i+1)) << 1), (int(maximum/2)+1), (2*i+1)):
            marked[j] = True

    # Since 2 is a prime number
    primes.append(2)

    # Print other primes. Remaining primes are of the
    # form 2*i + 1 such that marked[i] is false.
    for i in range(1, int(maximum/2)):
        if (marked[i] == False):
            primes.append(2*i + 1)

def get_primorial(n):
    result = 1
    for i in range(n):
        result = result * primes[i]
    return result

sieve()
M = get_primorial(40)
print(f"Primes: {primes}")
print(f"M: {M}")