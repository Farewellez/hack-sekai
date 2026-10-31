from sage.all import *
import random

P = 2
N = 50
E = 31337

FLAG = b'crypto{??????????????????????????}'

def bytes_to_binary(s):
    bin_str = ''.join(format(b, '08b') for b in s)
    bits = [int(c) for c in bin_str]
    return bits

# while True:
print(f"flag length: {len(FLAG)}")
msg = bytes_to_binary(FLAG)
msg_old = msg
print(f"message length: {len(msg)} ({len(FLAG)} * {8})")
print(f"multiple value: {N*N - len(msg)}")
msg += [random.randint(0, 1) for _ in range(N*N - len(msg))]
print(f"new message value: {len(msg)} ({len(msg_old)} + {N*N - len(msg_old)})")
# mat = generate_mat()
