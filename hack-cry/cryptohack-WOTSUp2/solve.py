import json
import hashlib

with open("./data_c1cf7f9624cc5c43e06c5c10b551a0e3.json", "r") as f:
    output = json.load(f)

for key in output.keys():
    signature1 = output["signatures"]
    pubkey = output["public_key"]
    iv = output["iv"]
    ct = output["enc"]

print(f"Signature 1:")
messages = []
signatures = []
for data in signature1:
    messages.append(data["message"])
    signatures.append(data["signature"])

for i in range(len(messages)):
    print(f"{i+1}. message: {messages[i]} = {signatures[i]}")
    print()
    

print()
print(f"Public key : {pubkey}")
print(f"IV         : {iv}")
print(f"Ciphertext : {ct}")


# sign method will always return 32 signature
# example:
# message2 = f"{w.pub_key[0].hex()} sent 999999 WOTScoins to me".encode()
# then:
# signature 2 = {s0, s1, s2, s3, ..., s31}
# 
# we know that sign method:
# si = Hash^{255 - bi}(ski)
# bi = SHA256(message)[i]
# 
# also verify method:
# Hash^{bi + 1}(si)
# 
# then:
# Hash^{bi + 1}(si)
# Hash^{bi + 1}(Hash^{255 - bi}(ski))
# Hash^{256}(ski)
# 
# for example:
# we try to search s0:
# example, b0 = 200, then:
# s0 = Hash^{255 - 200}(sk0)
# s0 = Hash^{55}(sk0)

# now lets try to search bi = SHA256(message 2)[i]
def hash(data):
    return hashlib.sha256(data).digest()

message2 = f"{pubkey[0]} sent 999999 WOTScoins to me".encode()
tag_msg2 = hash(message2)
print()
print(f"Message    2: {message2}")
print(f"Hashed msg 2: {tag_msg2.hex()}")

# try to search 32 signature
BYTE_MAX = 255
KEY_LEN = 32

print(f"=============== ITERASI MESSAGE 1 ===============")
count_signature_1 = []
for index in range(len(messages)):
    print(f"{index+1}. message: {messages[index]} = {signatures[index]}")
    print()
    for i in range(KEY_LEN):
        data_hash_bytes = bytearray(hash(messages[index].encode()))
        sig = []
        int_val = data_hash_bytes[i]
        hash_iters = BYTE_MAX - int_val
        if len(count_signature_1) <= i:
            count_signature_1.append((hash_iters, signatures[index][i]))
        elif count_signature_1[i]:
            if hash_iters < count_signature_1[i][0]:
                count_signature_1[i] = (hash_iters, signatures[index][i])
        print(f"Signature-{i}: {hash_iters}")

print(f"=============== ITERASI MESSAGE 2 ===============")
for i in range(KEY_LEN):
    data_hash_bytes = bytearray(tag_msg2)
    int_val = data_hash_bytes[i]
    hash_iters = BYTE_MAX - int_val
    print(f"Signature-{i}: {hash_iters}")

# di sini salah, aku belum punya privkey lol dan gada signature dari message 2, jadi perlu balik ke message 1
# misal, target = signature dari message 2
# target0 = Hash^{255 - bi}(sk0)
# 
# Di lain sisi, known = signature dari message 1
# known1 = Hash^{255 - bi}(sk0)
# 
# contoh:
# target0 = Hash^{255 - 191}(sk0)
# target0 = Hash^{64}(sk0)
# 
# known0 = Hash^{255 - 240}(sk0)
# known0 = Hash^{15}(sk0)
# 
# now, what if:
# target0 = known0
# Hash^{64}(sk0) = Hash^{49}(Hash^{15}(sk0))
# target0 = Hash^{49}(known0)

print(f"All Counted Signature 1:")
print(f"count_signature_1: {count_signature_1}")

# time to shine..
signature = []
for i in range(KEY_LEN):
    # target val
    data_hash_bytes2 = bytearray(tag_msg2)
    int_val2 = data_hash_bytes2[i]
    hash_iters2 = BYTE_MAX - int_val2
    
    # known val
    hash_iters1 = count_signature_1[i][0]
    
    hash_iters = hash_iters2 - hash_iters1
    assert hash_iters >= 0
    
    verify_item = bytes.fromhex(count_signature_1[i][1])
    # print(verify_item, type(verify_item))
    for _ in range(hash_iters):
        verify_item = hash(verify_item)
    signature.append(verify_item)

from Crypto.Cipher import AES
print()
print(f"recovered signature: {signature}")

aes_key = bytes([s[0] for s in signature])
aes_iv = bytes.fromhex(iv)
cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
flag = cipher.decrypt(bytes.fromhex(ct))
print(f"Flag: {flag.decode()}")