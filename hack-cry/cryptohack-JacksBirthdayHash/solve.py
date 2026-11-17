n = 11
all_possibility = 1 << n
print(f"n   = {n}") # 11
print(f"2^n = {all_possibility}") # 2048

# possibility 1 try correct:
# 1/2048

# possibility 1 try incorrect
# 1 - 1/2048
# 2047/2048

# possibility 1 try incorrect after n times
# (2047/2048)^n

# possibility 1 try correct after n times incorrect
# 1 - (2047/2048)^n

# possibility 1 try correct after n times incorrect that > 50% probability 
# 1 - (2047/2048)^n > 50%
# 1 - (2047/2048)^n > 0.5
# -1 + 1 - (2047/2048)^n > -1 + 0.5
# -(2047/2048)^n > -0.5
# (2047/2048)^n < 0.5
# n = (2047/2048)log 0.5

from math import log, floor, ceil
base = 2047/2048
num = 0.5
n = log(num,base)
print(f"n      : {n}")
print(f"n floor: {floor(n)}")
print(f"n ceil : {ceil(n)}")