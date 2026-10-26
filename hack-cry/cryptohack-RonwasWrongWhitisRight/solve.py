from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from math import gcd

keys = {}
for i in range(1,51):
    with open(f'./keys_and_messages/{i}.pem') as f:
        key = RSA.importKey(f.read())
        N = key.n
        e = key.e
        keys[i] = [N,e]

print(len(keys))

def get_pairs():
    pairs = []
    for k1 in keys:
        for k2 in keys:
            if k1 == k2:
                continue
            if gcd(keys[k1][0],keys[k2][0]) != 1:
                print(k1,k2)
                pairs.append((keys[k1][0], keys[k2][0]))
                pairs.append((keys[k1][1], keys[k2][1]))
                return pairs

pairs = get_pairs()
print(pairs)
p = gcd(pairs[0][0],pairs[0][1])
print(p)
q1 = pairs[0][0]//p
q2 = pairs[0][1]//p

with open("./keys_and_messages/21.ciphertext", "r") as ct:
    ct21 = bytes.fromhex(ct.read())

with open("./keys_and_messages/34.ciphertext", "r") as ct:
    ct34 = bytes.fromhex(ct.read())

phiN21 = (p-1)*(q1-1)
phiN34 = (p-1)*(q2-1)

d21 = pow(pairs[1][0],-1,phiN21)
d34 = pow(pairs[1][1],-1,phiN34)

key21 = RSA.construct((int(pairs[0][0]), int(pairs[1][0]), int(d21)))
key34 = RSA.construct((int(pairs[0][1]), int(pairs[1][1]), int(d34)))

cipher21 = PKCS1_OAEP.new(key21)
cipher34 = PKCS1_OAEP.new(key34)

m21 = cipher21.decrypt(ct21)
m34 = cipher34.decrypt(ct34)

print(m21.decode())
print(m34.decode())