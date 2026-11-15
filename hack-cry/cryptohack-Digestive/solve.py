import requests

BASE_URL = "https://web.cryptohack.org/digestive"
session = requests.Session()

def get_sign(msg):
    res = session.get(f"{BASE_URL}/sign/{msg}")
    return res.json()

def verify(msg, signature):
    res = session.get(f"{BASE_URL}/verify/{msg}/{signature}")
    return res.json()

mbg = 'vestia_zeta'
res = get_sign(mbg)
msg = res['msg']
sig = res["signature"]
print(res)

forge = '{"admin": false, "username": "' + mbg + '", "admin": true}'
flag = verify(forge, sig)['flag']
print(f"Flag: {flag}")