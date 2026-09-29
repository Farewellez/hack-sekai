# https://chat.deepseek.com/share/9agpamlvp0b8fnx8y5
from tqdm import tqdm
import requests

BASE_URL = "https://aes.cryptohack.org/paper_plane"
session = requests.Session()

def encrypt_flag():
    raw_data = session.get(f"{BASE_URL}/encrypt_flag")
    data = raw_data.json()
    c0 = data["c0"]
    ciphertext = data["ciphertext"]
    m0 = data["m0"]

    # print(ciphertext, m0, c0)
    # return data
    return ciphertext, m0, c0

def send_msg(ct, m0, c0):
    url = f"{BASE_URL}/send_msg/{ct}/{m0}/{c0}/"
    raw_data = session.get(url)
    data = raw_data.json()    
    return data.get("msg", data.get("error", ""))

def decrypt_block(target_ct, prev_pt, prev_ct, known=b""):
        pt = bytearray(16)

        for i in range(1, 17):
            padd_val = i
            found = False
            for char in tqdm(range(255, -1, -1), desc=f"i={i}", leave=False):
                if i == 0 and char == 0:
                    continue
                modiv_c0 = bytearray(prev_ct)
                for v in range(16 - i, 16):
                    if v == 16 - i:
                        modiv_c0[v] = char
                    else:
                        modiv_c0[v] = pt[v] ^ prev_ct[v] ^ padd_val
                
                res = send_msg(target_ct.hex(), prev_pt.hex(), modiv_c0.hex())
                if "Message received" in res:
                    if i == 1:
                        verif_c0 = bytearray(modiv_c0)
                        verif_c0[14] ^= 0xFF
                        verif_res = send_msg(target_ct.hex(), prev_pt.hex(), verif_c0.hex())

                        if "Message received" not in verif_res:
                            continue

                    pt[16 - i] = char ^ prev_ct[16 - i] ^ padd_val
                    # print(f"bytes ditemukan: {char}")
                    found = True
                    break

            if not found:
                print('bagaimana mungkin')
        return bytes(pt)

# collect variable
ct, m0, c0 = encrypt_flag()
print(len(bytes.fromhex(ct)))
print(ct, m0, c0)

# testing response
msg = send_msg(ct, m0, c0)
print(msg)

# try decrypt block
blocks = [bytes.fromhex(ct)[i:i+16] for i in range(0, len(bytes.fromhex(ct)), 16)]
prev_pt = bytes.fromhex(m0)
prev_ct = bytes.fromhex(c0)

# print(blocks)
pt = b""
for block in blocks:
    m = decrypt_block(block, prev_pt, prev_ct)
    if m is None:
        break
    pt += m
    prev_pt = m
    prev_ct = block

print(pt)