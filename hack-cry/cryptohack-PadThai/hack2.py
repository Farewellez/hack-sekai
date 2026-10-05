from pwnlib.context import context
from pwn import *

host = "socket.cryptohack.org"
port = 13421
context.log_level = 'debug'

io = remote(host, port)
