import requests
from Crypto.Util.number import bytes_to_long
from tqdm import tqdm

BASE_URL = "https://aes.cryptohack.org/ctrime"
KNOWN = "crypto{"
WORDS = "}_cryptoCYPTOetainshrdluETAINSHRDLU0123456789bfgjkmqvwxzBFGJKMQVWXZ!$'-."

def encrypt(msg):
    data = requests.get(f"{BASE_URL}/encrypt/{msg}/")  
    # print(data)
    ciphertext = data.json()["ciphertext"]
    return ciphertext

def attack():
    tmp = KNOWN.encode()
    while True:
        if b"}" in tmp:
            break
        cand = None
        best = None
        pbar = tqdm(range(len(WORDS)), total=len(WORDS))
        for i in pbar:
            ct = bytes.fromhex(encrypt((tmp.hex() + WORDS[i].encode().hex())*2))
            size = len(ct)
            pbar.set_description(f"Trying {WORDS[i]} ({size})")
            if best == None or size < best:
                best = size
                cand = WORDS[i]
                continue
        tmp += cand.encode()
        print(tmp)

attack()