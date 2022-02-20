import requests
import json

user = 'bitcoin'
url = f'https://api.github.com/users/{user.lower()}/repos'

res = requests.get(url)
json_data = res.json()

if res.ok and json_data:
    with open(f'github_repos_{user.lower()}.json', 'w') as file:
        json.dump(json_data, file)
else:
    print('Error!')
