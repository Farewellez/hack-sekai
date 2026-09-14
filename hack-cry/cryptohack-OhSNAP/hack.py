from requests import session
from rich import box
from tqdm import tqdm
import requests

# TEST = "a8a60da95e156750c60b52b7853a2184"
# PT = 'A'.encode()*16
# NONCE = 'A'.encode().hex()*16
# MOD = 256
BASE_URL = "https://aes.cryptohack.org/oh_snap"
session = requests.Session()

# def reverse_keystream(ciphertext, plaintext):
#     res = [c for c in ciphertext]
#     ks = []

#     for i, c in enumerate(plaintext):
#         print(c, res[i])
#         val = ("%02X" % (c ^ res[i]))
#         ks.append(val)
#     return ''.join(ks)

def get_ks(ct, nonce):
    raw_data = session.get(f"{BASE_URL}/send_cmd/{ct.hex()}/{nonce.hex()}/")
    stream = raw_data.json()["error"]
    data = stream.split("Unknown command: ")[-1]
    return data

# reference: https://github.com/manojpandey/rc4/blob/master/rc4-3.py
# predict_length = 40
predict_length = 35 # i have already run the code
FLAG = []
for A in range(predict_length):
    prob = [0] * 256
    
    for V in tqdm(range(256), total=256, desc="trying possible candidate "):
        nonce = bytes([A + 3, 255, V])

        ct = bytes([0])
        pt_hex = get_ks(ct,nonce)
        pt = bytes.fromhex(pt_hex)
        ks_byte = pt[0] ^ ct[0]

        current_key = list(nonce) + FLAG

        j = 0
        S = list(range(256))

        for i in range(A + 3):
            j = (j + S[i] + current_key[i]) % 256
            S[i], S[j] = S[j], S[i]

            if i == 1:
                original0 = S[0]
                original1 = S[1]

        i = A + 3
        z = S[1]

        if z + S[z] == A + 3:
            if (original0 != S[0] or original1 != S[1]):
                continue
            keyByte = (ks_byte - j - S[i]) % 256
            prob[keyByte] += 1

    cand = prob.index(max(prob))
    FLAG.append(cand)
    print(f"Flag so far: {bytes(FLAG)}")
