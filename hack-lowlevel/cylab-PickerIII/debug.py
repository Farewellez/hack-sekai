USER_ALIVE = True
FUNC_TABLE_SIZE = 4
FUNC_TABLE_ENTRY_SIZE = 32
CORRUPT_MESSAGE = 'Table corrupted. Try entering \'reset\' to fix it'

func_table = \
'''\
print_table                     \
read_variable                   \
write_variable                  \
getRandomNumber                 \
'''
n = 1
func_name = ''
func_name_offset = n * FUNC_TABLE_ENTRY_SIZE
for i in range(func_name_offset, func_name_offset+FUNC_TABLE_ENTRY_SIZE):
    print(f"i: {i}")
    print(f"func_table[i]: {func_table[i]}")
    if( func_table[i] == ' '):
        print(f"func_name_offset: {func_name_offset}")
        print(f"func_table[func_name_offset:i]: {func_table[func_name_offset:i]}")
        func_name = func_table[func_name_offset:i]
        break