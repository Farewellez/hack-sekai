import os

with open("example.png", "rb") as f:
    known = f.read(16)

out = []
with open("flag.png", "rb") as f:
    block = f.read(16)
    keystream = [a^b for a, b in zip(known, block)]
    while block:
        xored = [a^b for a, b in zip(block, keystream)]
        out.append(bytes(xored))
        block = f.read(16)

with open("recover.png", "wb") as f:
    for m in out:
        f.write(m)

if os.path.isfile("recover.png"):
    print("File berhasil disimpan")
    os.system("ls -la ./recover.png")
else:
    print("File gagal disimpan")