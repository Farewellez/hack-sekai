import json
from pwn import *
from math import gcd
from Crypto.Util.number import long_to_bytes, bytes_to_long

host = "socket.cryptohack.org"
port = 13375

conn = remote(host,port)
context.log_level = 'error'

# banner
conn.recvline()

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

# alice public key
N = 22266616657574989868109324252160663470925207690694094953312891282341426880506924648525181014287214350136557941201445475540830225059514652125310445352175047408966028497316806142156338927162621004774769949534239479839334209147097793526879762417526445739552772039876568156469224491682030314994880247983332964121759307658270083947005466578077153185206199759569902810832114058818478518470715726064960617482910172035743003538122402440142861494899725720505181663738931151677884218457824676140190841393217857683627886497104915390385283364971133316672332846071665082777884028170668140862010444247560019193505999704028222347577
e = 3

# testing vote
testing_vote  = b'VOTE FOR PEDRO'.hex()
send({"option": "vote", "vote": testing_vote})

# interesting:
# P = b'VOTE FOR PEDRO'
# s = vote (input kita)
# 
# verified_vote = s ** 3 mod N
# verified_vote (long/int) -> bytes
# verified_vote harus berakhiran | b"\x00" | b'VOTE FOR PEDRO'

# crafting
P = b'VOTE FOR PEDRO'
L = len(P)

# 1 byte null sebelum P
k = 8 * (L + 1)
mod = 1 << k # 2**k

# now we got:
# P = s ** 3 mod N
# P = s ** 3 mod (2**k)
# s ** 3 = P mod (2**k)
# s ** 3 = q * mod (2**k) + P

P = bytes_to_long(P)
assert gcd(P,1<<k) == 1

# https://en.wikipedia.org/wiki/Carmichael_function
# Sekarang, gimana cara dapat s yang valid tapi cuma diketahui s**3 dan P
# fakta dari Carmichael function: untuk setiap a ganjil,
# a^λ ≡ 1  (mod 2**k),   dengan λ = 2**(k-2)  (k ≥ 3)
# 
# sekarang perlu buat skenario:
# λ = 2**(k-2)
# 3.d ≡ 1  (mod 2**(k-2))
# d = 3**-1 (mod 2**(k-2))
# 
# 3.d ≡ 1  (mod 2**(k-2))
# 3.d = 1 * t + λ
# 
# target d ini buat apa? buat ini:
# kita mau s = P**d itu memenuhi s**3 ≡ P
# s = P**d mod 2**k
# 
# jadinya:
# s**3 = P**(d*3) = P**(1 * t + λ) = P**(1 * t) = P

lambda_ = 1 << (k-2)
d0 = pow(e,-1,lambda_)
s0 = pow(P, d0, mod)

assert pow(s0,e,mod) == P

# for t in range(1000): kalau maw, opsional aja, harusnya dengan s0 dan d0 aja udah cukup, tp kalau mau cari t juga bisa

send({"option": "vote", "vote": hex(s0)[2:]})
conn.recvline()
res = recv()["flag"]
print(f"Flag: {res}")

# conn.interactive()
conn.close()