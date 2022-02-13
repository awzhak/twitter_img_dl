"""Favorite image downloader."""
import os
import datetime
from typing import List
import requests
import tweepy
from dotenv import load_dotenv

class Env():
    def __init__(self) -> None:
        load_dotenv()
        self.consumer_key = os.getenv('CONSUMER_KEY')
        self.consumer_secret = os.getenv('CONSUMER_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        self.screen_names = os.getenv('SCREEN_NAMES').split(',')
        self.save_dirs = os.getenv('SAVE_DIRS').split(',')
        self.des_fav_scn = os.getenv('DES_FAV_IDS').split(',')

class TwitterAPI():
    def __init__(self, env: Env) -> None:
        _auth = tweepy.OAuth1UserHandler(consumer_key=env.consumer_key,
                                         consumer_secret=env.consumer_secret,
                                         access_token=env.access_token,
                                         access_token_secret=env.access_token_secret,
                                         callback=None)
        self.api = tweepy.API(_auth)

    def get_favorites(self,
                      screen_name: str,
                      paging: int,
                      count: int=200,
                      max_id: int=None):
        for _ in range(paging):
            fav_tweets = self.api.get_favorites(screen_name=screen_name,
                                                count=count,
                                                max_id=max_id)
            for tweet in fav_tweets:
                yield tweet
            max_id = fav_tweets[len(fav_tweets) - 1].id

    def destroy_favorite(self, tweet_id: str):
        self.api.destroy_favorite(tweet_id)

class Save():
    @classmethod
    def img(cls, img_source, file_path: str):
        with open(os.path.join(file_path), 'wb') as fp:
            fp.write(img_source)

class Downloader():

    def __init__(self, env: Env) -> None:
        self.env = env
        self.api = TwitterAPI(env)

    def run(self, screen_name: str, save_dir: str, paging: int=1):
        """downloader.

        Args:
            screen_name (str): target screen_name
            save_dir (str): save directory
            paging (int, optional): paging. Defaults to 1.
        """
        for result in self.api.get_favorites(screen_name=screen_name, paging=paging):
            if self._has_img(result):
                created_at = self._to_jst_str(result.created_at)
                media_urlds = [e['media_url_https'] for e in result.extended_entities['media']]
                self._save_imgs(media_urlds, created_at, save_dir, result.user.screen_name)
                print(f'{screen_name}: {result.id}')

                if screen_name in self.env.des_fav_scn:
                    self.api.destroy_favorite(result.id)

    @staticmethod
    def _has_img(tweet) -> bool:
        return bool('media' in tweet.entities)

    @staticmethod
    def _to_jst_str(utc: datetime) -> str:
        jst = utc + datetime.timedelta(hours=9)
        return jst.strftime('%Y-%m%d-%H%M%S')

    @staticmethod
    def _save_imgs(media_urlds: List[str],
                   created_at: str,
                   save_dir: str,
                   target_screen_name: str):
        for i, media_url in enumerate(media_urlds):
            source = requests.get(media_url + ':orig')
            path = f'{save_dir}{created_at}_{target_screen_name}{str(i)}.{media_url.split(".")[-1]}'
            Save.img(source.content, path)

if __name__ == '__main__':
    env_ = Env()
    for screen_name_, save_dir_ in zip(env_.screen_names, env_.save_dirs):
        Downloader(env_).run(screen_name_, save_dir_)
