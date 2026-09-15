import json
from pwn import *
import binascii

# --- KONFIGURASI TARGET ---
host = "socket.cryptohack.org"
port = 13421
context.log_level = 'info' # Ubah ke 'debug' jika ingin melihat pengiriman JSON secara detail

class Remote:    
    def __init__(self):
        self.io = remote(host, port)
        self.io.recvuntil(b"Let's practice padding oracle attacks! Recover my message and I'll send you a flag.\n")
    
    def get_ct(self, option="encrypt"):
        payload = {"option": option}
        self.io.sendline(json.dumps(payload).encode())
        return self.io.recvline()

    def oracle(self, fake_iv, ciphertext):
        """
        Fungsi ini khusus untuk berinteraksi dengan server.
        Menerima fake_iv (manipulasi kita) dan ciphertext blok yang ditarget.
        """
        payload_hex = (fake_iv + ciphertext).hex()
        payload = {
            "option": "unpad",
            "ct": payload_hex
        }
        self.io.sendline(json.dumps(payload).encode())
        res = json.loads(self.io.recvline().decode())
        return res.get('result', False)

    def close_conn(self):
        self.io.close()

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# --- MEMULAI KONEKSI ---
conn = Remote()

# 1. Mendapatkan Data Target
print("[*] Meminta data terenkripsi dari server...")
raw_response = conn.get_ct().decode()
ct_full_hex = json.loads(raw_response)['ct']
ct_full_bytes = bytes.fromhex(ct_full_hex)

# Memisahkan IV dan sisa Ciphertext
iv = ct_full_bytes[:16]
ciphertext = ct_full_bytes[16:]

print(f"[+] Got IV : {iv.hex()} ({len(iv)} bytes)")
print(f"[+] Got CT : {ciphertext.hex()} ({len(ciphertext)} bytes)")

# 2. Memecah Ciphertext menjadi array per blok (16 byte)
blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
print(f"[*] Total blok ciphertext (tanpa IV): {len(blocks)}")

full_plaintext = b""

# --- FUNGSI ATTACK PER BLOK ---
def attack_block(c1, c2):
    """
    c1: Blok sebelumnya (atau IV asli) - Hanya dipakai di akhir untuk mengungkap plaintext
    c2: Blok ciphertext yang sedang dibongkar
    """
    known_intermediate = b"" # Ini akan menyimpan state yang berhasil ditebak (dari belakang ke depan)
    
    for i in range(16): # Iterasi byte per byte (i=0 untuk byte paling belakang)
        padding_val = i + 1
        padding = padding_val.to_bytes(1, 'big') * padding_val
        
        for guess in range(256): 
            # 1. Buat tebakan Intermediate State parsial
            # bytes([guess]) = tebakan kita untuk byte yang sedang dicari
            # known_intermediate = byte yang sudah berhasil ditebak di iterasi sebelumnya
            guess_intermediate = bytes([guess]) + known_intermediate
            
            # 2. XOR-kan tebakan Intermediate State dengan target padding
            known_fake = xor(guess_intermediate, padding)
            
            # 3. Rakit Fake IV: Sisa byte di depan diisi dengan \x00
            fake_iv = bytes(15 - i) + known_fake
            
            # 4. Lempar ke Oracle
            if conn.oracle(fake_iv, c2):
                known_intermediate = bytes([guess]) + known_intermediate
                # print(f"    [+] Byte ditemukan! Intermediate sementara: {known_intermediate.hex()}")
                break # Pindah ke byte berikutnya
    
    # 5. Setelah 1 blok penuh (16 byte) Intermediate State didapat, XOR dengan blok ciphertext asli (c1)
    plaintext_block = xor(c1, known_intermediate)
    print(f"[+] Berhasil dekripsi blok: {plaintext_block}")
    return plaintext_block

# --- EKSEKUSI ATTACK DINAMIS ---
print("\n[*] Memulai dekripsi blok dari belakang...")

# Loop dari blok paling belakang (dinamis, tidak terpaku pada 2 blok)
for i in range(len(blocks) - 1, -1, -1):
    c2 = blocks[i]
    
    # Tentukan c1 (blok sebelumnya)
    if i == 0:
        c1 = iv # Jika blok pertama, c1 adalah IV
    else:
        c1 = blocks[i-1] # Jika blok lain, c1 adalah blok ciphertext sebelumnya
        
    print(f"\n[*] Membongkar Blok ke-{i+1}...")
    decrypted_block = attack_block(c1, c2)
    
    # Susun hasil dari belakang
    full_plaintext = decrypted_block + full_plaintext

print(f"\n[!!!] DEKRIPSI SELESAI [!!!]")
print(f"[>] Plaintext + Padding: {full_plaintext}")

# Menghapus padding PKCS7 untuk melihat pesan asli
try:
    from Crypto.Util.Padding import unpad
    clean_plaintext = unpad(full_plaintext, 16)
    print(f"[>] Clean Message: {clean_plaintext.decode()}")
    
    # Opsional: Kirim pesan yang sudah bersih kembali ke server untuk cek flag
    print("\n[*] Mengirim pesan kembali ke server untuk klaim flag...")
    conn.io.sendline(json.dumps({"option":"check", "message": clean_plaintext.decode()}).encode())
    flag_response = conn.io.recvline().decode()
    print(f"[>] Respons Server: {flag_response}")
    
except Exception as e:
    print(f"[-] Gagal membuang padding atau decode pesan: {e}")

conn.close_conn()
