from random import SystemRandom
rng = SystemRandom()
true_count = 0
false_count = 0

for _ in range(500):
    if True ^ (rng.random() > 0.4):
        true_count += 1
        continue
    false_count += 1
print(f"true: {true_count}\nfalse: {false_count}")

true_count = 0
false_count = 0

for _ in range(500):
    if False ^ (rng.random() > 0.4):
        true_count += 1
        continue
    false_count += 1
print(f"true: {true_count}\nfalse: {false_count}")

