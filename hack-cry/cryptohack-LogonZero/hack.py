import json
from pwn import *
from tqdm import tqdm

host = "socket.cryptohack.org"
port = 13399
context.log_level = "error"

class Remote:
    def __init__(self):
        self.io = remote(host, port)
        self.io.recvuntil(b"Please authenticate to this Domain Controller to proceed\n")
    
    def auth(self, password):
        # self.io.recvuntil(b'{"msg": "Password has been correctly reset."}\n')
        payloads = {
            "option": "authenticate",
            "password": password
            }
        self.io.sendline(json.dumps(payloads).encode())
        return self.io.recvline()

    def reset_conn(self):
        payloads = {
            "option": "reset_connection"
            }
        self.io.sendline(json.dumps(payloads).encode())
        return self.io.recvline()
    
    def reset_pw(self, token):
        payloads = {
            "option": "reset_password",
            "token": token
            }
        self.io.sendline(json.dumps(payloads).encode())
        return self.io.recvline()
    
    def close_conn(self):
        self.io.close()

# https://www.huntress.com/threat-library/vulnerabilities/cve-2020-1472
# https://github.com/dirkjanm/CVE-2020-1472/blob/master/cve-2020-1472-exploit.py

MAX_ATTEMP = 2000
pbar = tqdm(range(0, MAX_ATTEMP), total=MAX_ATTEMP)
spoofed_token = b'\x00' * 32
spoofed_password = ""

conn = Remote()
for i in tqdm(range(MAX_ATTEMP), total=MAX_ATTEMP, desc="try to get 1-in-256 chance just like my chances of getting her 🥀️🥀️ "):
    reset = conn.reset_pw(spoofed_token.hex())
    
    if b'{"msg": "Password has been correctly reset."}' in reset:        
        result = conn.auth(spoofed_password)

        if b'admin' in result:
            flag = result.decode().split("flag: ")[-1][:-3]
            conn.close_conn()
            break
    
    connection = conn.reset_conn()
    if b'{"msg": "Connection has been reset."}' in connection:
        continue

print(f"Flag: {flag}")