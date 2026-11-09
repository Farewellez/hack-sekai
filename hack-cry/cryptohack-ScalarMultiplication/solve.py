# E: Y^2 = X^3 + 497*X + 1768 mod 9739
a, b = 497, 1768
p = 9739

def point_addition(P, Q, a, b, p):
    # print(P)
    # print(Q)
    if P == Q:
        s = (3*(P[0]**2) + a) * pow(2*P[1],-1,p)
    else:
        s = (Q[1] - P[1]) * pow((Q[0] - P[0]),-1,p)
    
    x = (s**2 - P[0] - Q[0]) % p
    y = (s*(P[0] - x) - P[1]) % p
    return (x,y)

def scalar_multiplication(P, a, b, p, n):
    Q = P
    R = None
    
    while n > 0:
        if n % 2 == 1:
            if R == None:
                R = Q
            else:
                R = point_addition(R, Q, a, b, p)

        # print(Q)
        Q = point_addition(Q, Q, a, b, p)
        n = n // 2

        if n <= 0:
            break
    
    return R

# testing the algorithm
# Q = [n]*P
# [1337]X = P(1089,6931)
n = 1337
X = (5323,5438)

# testing X
R = scalar_multiplication(X, a, b, p, n)
assert R == (1089,6931)
print(f"Testing passed: {R}")

# challenge
P = (2339,2213)
n = 7863

Q = scalar_multiplication(P, a, b, p, n)
assert pow(Q[1],2,p) == (Q[0]**3 + 497*Q[0] + 1768) % p
print(f"Testing passed: {Q}")
print(f"Flag: crypto{{{Q[0]},{Q[1]}}}")