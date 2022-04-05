from pymongo import MongoClient

client = MongoClient('192.168.1.200', 27017)
insta_db = client.insta
collection = insta_db['followers']

print('Написать запрос к базе, который вернет список подписчиков только указанного пользователя')
for follower in insta_db.followers.find({'username': 'bang.bang4045'}):
    print(follower)

print('Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь')
for follow in insta_db.following.find({'username': 'bang.bang4045'}):
    print(follow)
