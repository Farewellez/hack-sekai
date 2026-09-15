from Crypto.Util.Padding import unpad
from invoke.completion.complete import print_task_names
from progressbar import progressbar
from plumbum.cli.progress import ProgressBase
from plumbum.cli import progress
from pip._vendor.msgpack import fallback
import json
from pwn import *

host = "socket.cryptohack.org"
port = 13421
context.log_level = 'debug'

class Remote:    
    def __init__(self):
        self.io = remote(host, port)
        self.io.recvuntil(b"Let's practice padding oracle attacks! Recover my message and I'll send you a flag.\n")
    
    def get_ct(self,option):
        payload = {"option": option}
        self.io.sendline(json.dumps(payload).encode())
        return self.io.recvline()

    def unpad(self, option, ciphertext):
        # self.io.recvline()
        payload = {
            "option": option,
            "ct": ciphertext,
            }
        self.io.sendline(json.dumps(payload).encode())
        return self.io.recvline()
    
    def get_message(self, option, msg):
        payload = {
            "option": option,
            "message": msg
        }
        self.io.sendline(json.dumps(payload).encode())
        return self.io.recvline()
    
    def close_conn(self):
        self.io.close()

def xor(a, b) :
    return bytes(x ^ y for x, y in zip(a, b))

# trying to get the ciphertext sample
conn = Remote()
raw_ct = conn.get_ct("encrypt").decode().split('{"ct": "')[-1][:-3]
ct = bytes.fromhex(raw_ct)[16:].hex()
iv = bytes.fromhex(raw_ct)[:16].hex()
print(f"Got ciphertext: {ct} with {len(bytes.fromhex(ct))} bytes of length")
print(f"Got iv        : {iv} with {len(bytes.fromhex(iv))} bytes of length")

c_hex = binascii.hexlify(bytes.fromhex(ct))
c_blk = [c_hex[i:i+32] for i in range(0,len(c_hex),32)]

combined_result = b""
bar = progressbar.ProgressBar(maxval=len(c_blk))

bar.start()
for i_blk in range(len(c_blk)):
    if i_blk+2 <= len(c_blk):
        c1 = binascii.unhexlify(c_blk[-2-i_blk])
        c2 = binascii.unhexlify(c_blk[-1-i_blk])
    else:
        c1 = bytes.fromhex(iv)
        c2 = binascii.unhexlify(c_blk[0])

    blk_result = b""
    for i in range(16):
        count = 0
        found_str = b''

        for j in range(256):
            blk1 = b'\x00'*(15-i)+(i+1).to_bytes(1,'big')*(i+1)
            blk2 = b'\x00'*(15-i)+j.to_bytes(1,'big')+blk_result 

            concat = xor(xor(c1, blk1), blk2) + c2
            print(concat)
            payload = bytes.fromhex(iv) + concat

            if "True" in conn.unpad("unpad", payload.hex()).decode() or "true" in conn.unpad("unpad", payload.hex()).decode():
                count += 1
                
                if i != j:
                    found_str = j.to_bytes(1, 'big')
        
        if count > 1 or (count == 1 and found_str != b''):
            blk_result = found_str + blk_result
        elif count == 0:
            print("Decryption failed")
            break
        else:
            blk_result = (i+1).to_bytes(1,'big')+blk_result
    
    combined_result=blk_result + combined_result
    bar.update(i_blk)

bar.finish()
print(combined_result)

clean_pt = combined_result.decode('ascii')
last_payload = conn.get_message("check", clean_pt).decode()
print(last_payload)

conn.close_conn()