# python3 -m venv env
# pip install pwntools 
# pip install tqdm
import json
import time
from pwn import *
from tqdm import tqdm

# host = "127.0.0.1"
host = "socket.cryptohack.org"
port = 13398
context.log_level = 'info'

while True:
    conn = remote(host, port)
    conn.recvline()

    def send(obj):
        obj = json.dumps(obj).encode()
        conn.sendline(obj)

    def check_bit(bit):
        st = time.perf_counter()
        for _ in range(7):
            send({"option": "get_bit", "i": bit})
            conn.recvline()
        ed = time.perf_counter()
        return ed - st

    high = check_bit(0)
    low = check_bit(7)

    mid = high - (high - low) * 0.618
    log.info(f"high   (1): {high}")
    log.info(f"low    (0): {low}")
    log.info(f"medium    : {mid}")

    bit_flag = ""
    flag = ""
    pbar = tqdm(total=8 * 43, leave=False)
    for i in range(8 * 43):
        bit_flag += "01"[check_bit(i) > mid]
        if i % 8 == 7:
            flag += chr(int(bit_flag[::-1], 2))
            print(f"progress: {flag}")
            bit_flag = ''
        pbar.update(1)

    if 'crypto' not in flag:
        conn.close()
        continue
    else:
        print(f"Flag: {flag}")
        conn.close()
        break
