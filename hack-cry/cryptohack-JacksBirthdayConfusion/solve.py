n = 11
all_possibility = 1 << n
print(f"n   = {n}") # 11
print(f"2^n = {all_possibility}") # 2048


# alogb = c ->(2047/2048)log 0.5 = n
# a^c   = b ->(2047/2048)^n      = 0.5

import math
n = math.sqrt(2 * all_possibility * math.log((1/(1-0.75)),math.e))
print(f"n      : {n}")
print(f"n floor: {math.floor(n)}")
print(f"n ceil : {math.ceil(n)}")