from pwn import *
from tqdm import tqdm
import json, time


rn = remote('socket.cryptohack.org', 13398)
rn.recvline()

def Measure(bit):
    st = time.time()
    for i in range(5):
        rn.send(json.dumps({'option': 'get_bit', 'i': bit}).encode())
        rn.recvline()
    ed = time.time()
    return ed - st

high = Measure(0)
low = Measure(7)
mid = high - (high - low) * 0.618
print(high, low, mid)

flag = ''
num_now = ''
for index in tqdm(range(8 * 43)):
    num_now += '01'[Measure(index) > mid]
    if index % 8 == 7:
        flag += chr(int(num_now[::-1], 2))
        num_now = ''
print(flag)