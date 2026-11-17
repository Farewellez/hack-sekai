from hashlib import md5
from difflib import ndiff

# https://www.johndcook.com/blog/2024/03/20/md5-hash-collision/
def showdiff(a, b):
    for i,s in enumerate(ndiff(a, b)):
        if s[0]==' ': continue
        elif s[0]=='-':
            print(u'Delete "{}" from position {}'.format(s[-1],i))
        elif s[0]=='+':
            print(u'Add "{}" to position {}'.format(s[-1],i))    

a = "TEXTCOLLBYfGiJUETHQ4hAcKSMd5zYpgqf1YRDhkmxHkhPWptrkoyz28wnI9V0aHeAuaKnak"
b = "TEXTCOLLBYfGiJUETHQ4hEcKSMd5zYpgqf1YRDhkmxHkhPWptrkoyz28wnI9V0aHeAuaKnak"

showdiff(a, b)

ahash = md5(a.encode('utf-8')).hexdigest()
bhash = md5(b.encode('utf-8')).hexdigest()
assert(ahash == bhash)

import json
import re
from pwn import *

host, port = "socket.cryptohack.org", 13389
conn = remote(host,port)
context.log_level = 'error'

def send(obj):
    obj = json.dumps(obj).encode()
    conn.sendline(obj)

def recv():
    line = conn.recvline()
    line = json.loads(line.decode())
    return line

conn.recvuntil(b'Give me a document to store\n')
send({"document": a.encode().hex()})

res = recv()
if "success" in res:
    send({"document": b.encode().hex()})
    msg = recv()["error"]

match = re.search(r'crypto\{.*?\}', msg)
if match:
    flag = match.group(0)

conn.close()

print(f"Flag: {flag}")