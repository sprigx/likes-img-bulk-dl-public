from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, BaseSettings


class ClientInfo(BaseSettings):
    """クライアント情報の定義(環境変数から持ってくる)"""

    bearer_token: str
    access_token: str
    access_token_secret: str
    consumer_key: str
    consumer_secret: str

    class Config:
        env_file = Path(__file__).parents[1] / ".env"


class TweetInfo(BaseModel):
    """ツイートデータの定義"""

    id: int
    text: str
    user_id: int
    image_urls: list[str]
    created_at: datetime
    crawled_at: datetime = datetime.now()


class UserInfo(BaseModel):
    """ユーザー情報の定義"""

    id: int
    name: str
    username: str
    protected: bool


class TweetModel(BaseModel):
    """DBのtweetsテーブル"""

    id: int
    text: str
    user_id: int
    created_at: str
    crawled_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class UserModel(BaseModel):
    """DBのusersテーブル"""

    id: int
    name: str
    username: str
    protected: int
    crawled_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ImageModel(BaseModel):
    """DBのimagesテーブル"""

    id: int | None = None
    url: str
    tweet_id: int
    path: str | None = None
    downloaded: int = 0
    ext: str | None
