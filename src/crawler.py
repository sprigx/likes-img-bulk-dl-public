import re
from abc import ABCMeta, abstractmethod
from time import sleep

import tweepy
from loguru import logger

import db
from models import ClientInfo, TweetInfo, UserModel
from utils import dig, none_to_empty_list


class BaseCrawler(metaclass=ABCMeta):
    """Twitterクローラーの抽象基底クラス"""

    def __init__(self, username: str):
        logger.info("Initializing crawler.")
        self.client = tweepy.Client(wait_on_rate_limit=True, **ClientInfo().dict())
        self.user_info = self._fetch_user_info(username)

    def _fetch_user_info(
        self, username: str | None = None, user_id: int | None = None
    ) -> UserModel:
        """ユーザー情報を取得
        usernameかuser_idで指定
        DBにデータがあればそれを使う
        """
        if user_id is not None:
            user_cached = db.get_user(user_id)
            if user_cached is not None:
                return user_cached
        user = self.client.get_user(
            id=user_id,
            username=username,
            user_fields="protected,name",
            tweet_fields="id",
        )
        return UserModel(**user.data)

    def batch_run(self) -> None:
        """一括処理
        next_tokenがNoneになるまでクロールを続ける
        """
        logger.info("Start batch crawling.")
        next_token = None
        while True:
            next_token, _ = self._crawl(next_token)
            if next_token is None:
                break
        logger.info("Finished batch crawling.")

    def online_run(self) -> None:
        """差分更新
        next_tokenがNoneになるか、DB側からストップがかかるまでクロールする
        """
        logger.info("Start online crawling.")
        next_token = None
        while True:
            next_token, status = self._crawl(next_token)
            if next_token is None or status == "finished":
                break
        logger.info("Finished online crawling.")

    def _crawl(self, pagination_token: str | None) -> tuple[str | None, str]:
        sleep(1)
        fetched: tweepy.Response = self.fetch(pagination_token)
        parsed: dict = self.parse(fetched)
        next_token: str | None = parsed["next_token"]
        logger.info(f"next_token: {next_token}")
        store_status = self.store(parsed)
        return next_token, store_status

    @abstractmethod
    def fetch(self, pagination_token: str | None) -> tweepy.Response:
        """APIからデータを取ってくる"""
        pass

    @abstractmethod
    def parse(self, fetched: tweepy.Response) -> dict:
        """取ってきたデータをDBに格納できるようパースする"""
        pass

    @abstractmethod
    def store(self, parsed: dict) -> str:
        """パースしたデータをDBに格納する"""
        pass


class LikesCrawler(BaseCrawler):
    def fetch(self, pagination_token: str | None) -> tweepy.Response:
        liked_tweets = self.client.get_liked_tweets(
            id=self.user_info.id,
            expansions="attachments.media_keys",
            media_fields="url",
            tweet_fields=["author_id", "created_at"],
            user_auth=self.user_info.protected,
            pagination_token=pagination_token,
        )
        return liked_tweets

    def parse(self, fetched: tweepy.Response) -> dict:
        # media_keyをmedia_urlに変換する辞書
        image_url_dict = {
            d["media_key"]: self._make_image_url(d["url"])
            for d in none_to_empty_list(dig(fetched, "includes", "media"))
            if d["type"] == "photo"
        }
        parse_image_urls = ImageUrlParser(image_url_dict).parse_image_urls

        # ツイートのパース実行
        tweet_info_list = [
            TweetInfo(
                id=tweet.id,
                text=tweet.text,
                image_urls=parse_image_urls(tweet),
                user_id=tweet.author_id,
                created_at=tweet.created_at,
            )
            for tweet in none_to_empty_list(dig(fetched, "data"))
        ]

        return {
            "next_token": dig(fetched, "meta", "next_token"),
            "tweet_info_list": tweet_info_list,
        }

    @staticmethod
    def _make_image_url(original_url: str) -> str:
        match = re.match(r".*\.(.+)$", original_url)
        if match is None:
            return original_url
        ext = match.group(1)
        return original_url + f"?format={ext}&name=orig"

    def store(self, parsed: dict) -> str:
        tweets: list[TweetInfo] = parsed["tweet_info_list"]
        if tweets == [] or db.get_tweet(tweets[0].id) is not None:
            return "finished"
        for tweet in tweets:
            logger.debug(f"Stored tweet: {tweet}")
            user = self._fetch_user_info(user_id=tweet.user_id)
            db.add_tweet(tweet, user)
        return "continue"


class ImageUrlParser:
    def __init__(self, image_url_dict: dict):
        self.image_url_dict = image_url_dict

    def parse_image_urls(self, tweet: dict) -> list[str]:
        """tweet内のmedia_keyをurlに変換"""
        media_keys = none_to_empty_list(dig(tweet, "attachments", "media_keys"))
        urls = [dig(self.image_url_dict, key) for key in media_keys]
        return list(filter(None, urls))
