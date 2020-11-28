# coding: UTF-8
import tweepy
import datetime
import sys
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
CK = os.getenv('CONSUMER_KEY')
CS = os.getenv('CONSUMER_SECRET')
AT = os.getenv('ACCESS_TOKEN')
AS = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)

user_ids = os.getenv('USER_IDS').split(',')
save_dirs = os.getenv('SAVE_DIRS').split(',')
des_fav_ids = os.getenv('DES_FAV_IDS').split(',')

for uid, save_dir in zip(user_ids, save_dirs):
    result = api.favorites(uid, count = 200)
    for fav in result:
        if 'media' in fav.entities:
            jst = fav.created_at + datetime.timedelta(hours=9)
            time_str = jst.strftime('%Y-%m%d-%H%M%S')
            for i, media in enumerate(fav.extended_entities['media']):
                url = media['media_url_https']
                filename = f'{save_dir}{time_str}_{fav.user.screen_name + str(i)}.{url.split(".")[-1]}'
                res = requests.get(url + ':orig')
                with open(os.path.join(filename), 'wb') as fp:
                    fp.write(res.content)
            if uid in des_fav_ids:
                api.destroy_favorite(result.id)