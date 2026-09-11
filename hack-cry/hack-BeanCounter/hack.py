import requests
import os

BASE_URL = "https://aes.cryptohack.org/bean_counter"

def get_cipher():
    data = requests.get(f"{BASE_URL}/encrypt/")
    cipher = data.json()["encrypted"]
    return cipher

ciphertext = bytes.fromhex(get_cipher())
with open("flag.png", "wb") as f:
    f.write(ciphertext)

if os.path.isfile("flag.png"):
    print("File berhasil disimpan")
    os.system("ls -la ./flag.png")
else:
    print("File gagal disimpan")