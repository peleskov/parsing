import requests
import json

app_id = '8084958'
user_id = '44101088'
access_token = '8d5b1ae7107d1f539aecaa573e0f8f267c805ff5fad2d1adfff1c63d6ab58fafa89071766165d541d822f'
url = 'https://api.vk.com/method/groups.get'

res = requests.post(url, data={'v': '5.131', 'user_id': user_id, 'access_token': access_token, 'extended': 'true'})
data = res.text

if res.ok and data:
    with open(f'vk_groups_{user_id.lower()}.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(data), file)
else:
    print('Error!')
