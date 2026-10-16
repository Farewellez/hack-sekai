from sage.all import *

N = Integer(510143758735509025530880200653196460532653147)
F = [f[0] for f in N.factor()]
print(f"N-bit          : {N.bit_length()}")
print(f"Smallest factor: {min(F)}")