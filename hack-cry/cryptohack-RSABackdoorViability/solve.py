from sage.all import *
from Crypto.Util.number import long_to_bytes

# ==========================
# 1. Parameter Soal
# ==========================
N = 709872443186761582125747585668724501268558458558798673014673483766300964836479167241315660053878650421761726639872089885502004902487471946410918420927682586362111137364814638033425428214041019139158018673749256694555341525164012369589067354955298579131735466795918522816127398340465761406719060284098094643289390016311668316687808837563589124091867773655044913003668590954899705366787080923717270827184222673706856184434629431186284270269532605221507485774898673802583974291853116198037970076073697225047098901414637433392658500670740996008799860530032515716031449787089371403485205810795880416920642186451022374989891611943906891139047764042051071647203057520104267427832746020858026150611650447823314079076243582616371718150121483335889885277291312834083234087660399534665835291621232056473843224515909023120834377664505788329527517932160909013410933312572810208043849529655209420055180680775718614088521014772491776654380478948591063486615023605584483338460667397264724871221133652955371027085804223956104532604113969119716485142424996255737376464834315527822566017923598626634438066724763559943441023574575168924010274261376863202598353430010875182947485101076308406061724505065886990350185188453776162319552566614214624361251463
e = 65537
c = 608484617316138126443275660524263025508135383745665175433229598517433030003704261658172582370543758277685547533834085899541036156595489206369279739210904154716464595657421948607569920498815631503197235702333017824993576326860166652845334617579798536442066184953550975487031721085105757667800838172225947001224495126390587950346822978519677673568121595427827980195332464747031577431925937314209391433407684845797171187006586455012364702160988147108989822392986966689057906884691499234298351003666019957528738094330389775054485731448274595330322976886875528525229337512909952391041280006426003300720547721072725168500104651961970292771382390647751450445892361311332074663895375544959193148114635476827855327421812307562742481487812965210406231507524830889375419045542057858679609265389869332331811218601440373121797461318931976890674336807528107115423915152709265237590358348348716543683900084640921475797266390455366908727400038393697480363793285799860812451995497444221674390372255599514578194487523882038234487872223540513004734039135243849551315065297737535112525440094171393039622992561519170849962891645196111307537341194621689797282496281302297026025131743423205544193536699103338587843100187637572006174858230467771942700918388
D = 427

# ==========================
# 2. X-only Montgomery Ladder (Brier-Joye)
# ==========================
def montgomery_ladder(A, B, X0, k):
    """
    Menjalankan algoritma double-and-add di dalam koordinat Proyektif (X, Z).
    Ini menghindari segala macam error zero-division karena pembagian ditiadakan.
    """
    X1 = X0
    Z1 = X0.parent()(1)
    
    # Formula Doubling untuk menghitung P2 = 2 * P1
    X2 = (X1**2 - A*Z1**2)**2 - 8*B*X1*Z1**3
    Z2 = 4*Z1*(X1**3 + A*X1*Z1**2 + B*Z1**3)
    
    # Looping berdasarkan panjang bit pengali (N)
    bits = bin(k)[3:] 
    for bit in bits:
        if bit == '0':
            # Jika 0: P2 = P1 + P2, dan P1 = 2 * P1
            X_add = 1 * ((X1*X2 - A*Z1*Z2)**2 - 4*B*Z1*Z2*(X1*Z2 + X2*Z1))
            Z_add = X0 * (X1*Z2 - X2*Z1)**2
            
            X1_new = (X1**2 - A*Z1**2)**2 - 8*B*X1*Z1**3
            Z1_new = 4*Z1*(X1**3 + A*X1*Z1**2 + B*Z1**3)
            
            X1, Z1 = X1_new, Z1_new
            X2, Z2 = X_add, Z_add
        else:
            # Jika 1: P1 = P1 + P2, dan P2 = 2 * P2
            X_add = 1 * ((X1*X2 - A*Z1*Z2)**2 - 4*B*Z1*Z2*(X1*Z2 + X2*Z1))
            Z_add = X0 * (X1*Z2 - X2*Z1)**2
            
            X2_new = (X2**2 - A*Z2**2)**2 - 8*B*X2*Z2**3
            Z2_new = 4*Z2*(X2**3 + A*X2*Z2**2 + B*Z2**3)
            
            X1, Z1 = X_add, Z_add
            X2, Z2 = X2_new, Z2_new
            
    return X1, Z1

# Fungsi Extended GCD dari script aslimu (ini masih dipertahankan untuk menginisialisasi kurva)
def polynomial_xgcd(a, b):
    r_prev, r = a, b
    s_prev, s = 1, 0
    while r:
        try:
            q = r_prev // r
            r_prev, r = r, r_prev - q * r
            s_prev, s = s, s_prev - q * s
        except (RuntimeError, ZeroDivisionError):
            raise ArithmeticError("r is not invertible", r)
    return r_prev, s_prev

# ==========================
# 3. Setup Ring & Polinomial
# ==========================
print("[*] Inisialisasi Ring dan Polinomial Hilbert...")
zmodn = Zmod(N)
pr = zmodn["x"]
H = pr(hilbert_class_polynomial(-D))

# Membangun Quotient Ring berdasar polinomial Hilbert
Q = pr.quotient(H)
j = Q.gen()

# Kalkulasi parameter (k) untuk kurva eliptik
g, s = polynomial_xgcd((1728 - j).lift(), H)
inv_1728_j = s * g.lc()**-1
k = j * Q(inv_1728_j)

# Parameter kurva Weierstrass: y^2 = x^3 + Ax + B
A = 3 * k
B = 2 * k

# Pilih nilai awal x-coordinate (titik awal generator di Ring Q)
X0 = Q.gen()

# ==========================
# 4. Eksekusi N * P
# ==========================
print("[*] Mengeksekusi Skalar Montgomery N * P... (Estimasi waktu: < 10 detik)")
X_N, Z_N = montgomery_ladder(A, B, X0, N)

# ==========================
# 5. Ekstraksi Faktor
# ==========================
print("[*] Memeriksa koefisien Z_N...")
p = 0
for coeff in Z_N.lift().list():
    val = int(coeff)
    if val != 0:
        # GCD memverifikasi apakah koefisien adalah kelipatan valid p
        potential_p = gcd(val, N)
        if 1 < potential_p < N:
            p = potential_p
            break

if p:
    q = N // p
    print(f"[+] Ditemukan p: {p}")
    print(f"[+] Ditemukan q: {q}")
    
    print("\n[*] Mendekripsi pesan...")
    d = inverse_mod(e, (p - 1)*(q - 1))
    m = pow(c, d, N)
    flag = long_to_bytes(int(m))
    print(f"[+] FLAG: {flag.decode(errors='ignore')}")
else:
    print("[-] Gagal mengekstrak faktor p.")