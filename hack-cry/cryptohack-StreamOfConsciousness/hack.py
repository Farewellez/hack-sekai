from pwnlib.useragents import _cache
import requests
from tqdm import tqdm
from string import ascii_lowercase, ascii_uppercase

BASE_URL = "https://aes.cryptohack.org/stream_consciousness"
MAX_ATTEMP = 100
WORDS = ascii_lowercase + ascii_uppercase

# def get_ct():
#     data = requests.get(f"{BASE_URL}/encrypt/")
#     ct = data.json()['ciphertext']
#     return ct

# pbar = tqdm(range(MAX_ATTEMP), total=MAX_ATTEMP)
# list_ciphertext = []
# for i in pbar:
#     pbar.set_description(f"collecting ciphertext-{i}")
#     ct = get_ct()
#     list_ciphertext.append(ct)

# print(f"List of all ciphertext: {set(list_ciphertext)}")

list_ciphertext = {'4fefb6517498fe070c1b191d8dbc78d05541982096c37763c50a8e87be9a6547b50a7f382f0d8695c792679b6575a586', '4cefbd1475d7bc1c1d0d404f9fbd36d65506c4618fc16273c203c9c6b18a654daf116039354fc1e6c38c72d46b75a18789d7596af7', '4fefa11465ddee1a1c0a550ad8a67ed055419469958f6272cd10c9d3b78b655fbb0b787d3f40c8e1d6c07c913f69abd5939e5b7abc362bbae0a8ad799cfd82647c278d', '5fe8a8586898eb011904191b90bb78d21b52dc61928f5f3dc14485c2be982c41bd586d7d2f44c5a9cc843e9c6a6ea6c693da146ea67269b7a8a0ad2ac8e788796d32cc3d4b66a270b40631d17b1c218883fc3b5f2fc93d61c63d11f696da93ed64f57724', '53e8b31461caf31d114858019cf27ed84b56cd208eca3176c0448bc2ff992d4ab45864387c46c3b2d1c0738d3f73abd3989f', '52a7b75c70d4f04819074a0ad8b760dc495fc0688fc1713acd0a8d87b181310fbd1d787d3448cbe6c0817d9f31', '4ce8b1587598d5481d094f0ad8b073d55243c265828f6272c90ac9d3b78f310f93586f32294dc2e6d0857f97773db7d29ed6146bad663dabb3e1b66c9ce798666138ca2e5a2f843ee6', '78f5bd4465d7e70346110c588ae122d464548775d39c492b993b8f93e8da2952', '4be2b65c70c8ef481d0d190799a136d45255c765828f6272c9449dd5be872b0fbb16687d355286a4c38375d47d64e4c992c91a2f9f7727b7e0acb678d9af857e653dcf264f32823fb752', '52a7b75c70d4f04455211e0394f27ad64843946590ca6463d80c80c9b8ce2c49fa10697d384ec3b5ccc76ad47c72a9c2dddc556ca338', '52f3e45770d6bb1c550a5c4f8cbd64d71b49c174ca8f746fd84480d3ff8d2441fa1a697d3546c8a9d0857ada', '4cefa54031d9bc06141b4d16d8a17bdc574a94748ec6653adc0580c9abce2d4ebe56', '5ff5a1476295f1091e015708d8b378dd1b6bdd6c8ac6787fde1d', '55e8e814589ff004550f564f91bc36cd5406f06f8ac36f3acd0a8d87ab8b2943fa10692f7c52d2b4c389799c6b3dabd289', '57e8b2513d98ec1a1a0a580d94ab29996f4ed179c6cb79748b10c9ccb181320fb2177b7d3853c3a7d0993e9d6b3dadd4d19e5c60bf3621b6ada8b563ddfb84656f7a8d610e328335f93234c0351a31da87fe265f2ec47464cc6f00f0dd', '52a0a91464d6f40905184043d89b36dd5e55d17290ca3673d848c9d3b78b6549bb0d60297b5286abcb8e7bd83f7fb1d3ddf71362e86327aba1b1a9739cee81672820cb2a0e358a3dbc5f62cd3e0324da8bf56c', '5af4e45d7798d5481d095d4f99bc6f994c4fc768c6db793ace01c9ceb1ce3147bf587e343b49d2e782a93e977e73e3d3dc', '5ae9a0145898ef001404554f91b578d6494394699281', '4fefa1477498f407071b5c1cd4f262d15255946387dd6473cd038c87f2ce2d40ad58457d304ec7b2ca853e99666ea1cb9b9e5d61e86221aab3e1ba6bcefd846a6f3183620e328335a05430c07b0e3896c6f82b0c768c7f7ddc3d2cbe809285f367bb7e6f79fc1a027adbaeae1d210515e0f90b4bc7106d', '4cefa54031d9bc041a1c19009ef262d15248d373c6db7e7bd8449dcfba80655cbf1d61383801d2a9828d7bd46c72e4ca9ccc426aa47a26b6b3e1b864d8af98656920d72e47288a32b5166e85330e229fc6f2271c22c17828c17316f794948df962f871647bb5484367daebfa012c400ca8f1024ddd5e0a5942e3ef2068dc734732ec9af3b9a763aa9ce1084d2c413f8a889b793354d90ecff60fd82394b318', '59f2b0145898eb011904191c90bd6199534fd92e', '54f2b60b31eff41155074c1dc7'}
b_ct = [bytes.fromhex(c) for c in list_ciphertext]
max_len = max(len(c) for c in b_ct)
ks = []
# print(max_len)

for i in tqdm(range(max_len), total=max_len, desc="try recovering keystream "):
    best_k = 0
    max_score = -float('inf')

    for k in range(256):
        score = 0
        is_valid = True

        for ct in b_ct:
            if i < len(ct):
                p = ct[i] ^ k

                if 32 <= p <= 126:
                    _char = chr(p)
                    if _char.isalpha():
                        score += 10
                    elif _char == ' ':
                        score += 15
                    elif _char in "0123456789,.?/:;'" + '"':
                        score += 5
                else:
                    is_valid = False
                    break
        
        if is_valid and score > max_score:
            max_score = score
            best_k = k
    
    ks.append(best_k)

print(f"Finish recover keystream: {bytes(ks).hex()}")
print()
flag = None
for i in tqdm(range(len(b_ct)), total=len(b_ct), desc="recovering flag "):
    pt = "".join(chr(x ^ y) for x, y in zip(b_ct[i], ks))
    if "crypto" in pt:
        flag = pt

print(f"Flag: {flag}")
# Flag: crypto{k3y57r34m_r3u53_12_f474l}
# sedikit miss, harusnya: Flag: crypto{k3y57r34m_r3u53_15_f474l}