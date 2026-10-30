from primefac import primefac
p = 28151
totient = p - 1
totient_factors = set(primefac(totient))

# all primes q such that q|(p−1) -> q membagi (p-1), artinya q itu factor dari (p - 1)
# print(totient_factors)

# alpha**(p-1/q) != 1 mod p
choosen = None
for alpha in range(2,p):
    is_prime = True

    for q in totient_factors:
        if pow(alpha,(p-1)//q,p) == 1:
            is_prime = False
            break
    
    if is_prime:
        choosen = alpha
        break

print(choosen)