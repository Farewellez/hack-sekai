import requests
from rich import print_json

URL = "http://154.57.164.77:32319/"

class Remote:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.url = URL
    
    def get_options(self):
        option = requests.get(f"{self.url}{self.endpoint}")
        data = option.json()
        return data

    def post_choice(self, command):
        data = { 'command': command }
        print()
        print(f"-> Mengirim {data}")
        
        header = {"Content-Type": "application/json"}
        print(f"-> Target endpoint: {self.endpoint}")
        
        choice = requests.post(f"{self.url}{self.endpoint}", json=data, headers=header)
        return choice.status_code, choice.json()

options = Remote("api/options")
print_json(data=options.get_options())

choice = Remote("api/monitor")
print(choice.post_choice('help'))

secret_choice = "Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"
print(choice.post_choice(secret_choice))

