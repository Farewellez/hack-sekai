from Crypto.Util.number import long_to_bytes
from hashlib import sha256

with open("./output_1091e36a2522c149f174d6721df7ab02.txt", "r") as f:
    challenges = [eval(line) for line in f if line.strip()]

def hash256(data):
    return sha256(data).digest()

def merge_nodes(a, b):
    return hash256(a+b)

biner = ""
for chall in challenges:
    a = bytes.fromhex(chall[0])
    b = bytes.fromhex(chall[1])
    c = bytes.fromhex(chall[2])
    d = bytes.fromhex(chall[3])
    
    bias = b""
    left = merge_nodes(a, b+bias)
    right = merge_nodes(c, d)
    root = merge_nodes(left, right)
    
    if root.hex() == chall[4]:
        biner += str(1)
    else:
        biner += str(0)

flag = long_to_bytes(int(biner,2))
print(f"Flag: {flag.decode()}")