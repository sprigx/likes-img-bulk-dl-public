import re

import dataset

from models import ImageModel, TweetInfo, TweetModel, UserModel

db = dataset.connect("sqlite:///crawler.db")

tweets = db.create_table("tweets")
users = db.create_table("users")
images = db.create_table("images")


def get_user(user_id: int) -> UserModel | None:
    result = users.find_one(id=user_id)
    if result is None:
        return None
    return UserModel(**result)


def get_undone_images() -> list[ImageModel]:
    result = images.find(downloaded=0)
    return [ImageModel(**image) for image in result]


def update_image(image: ImageModel) -> None:
    image.update(ImageModel, ["url"])


def get_tweet(tweet_id: int) -> TweetModel | None:
    result = tweets.find_one(id=tweet_id)
    if result is None:
        return None
    return TweetModel(**result)


def add_tweet(tweet_info: TweetInfo, user: UserModel):
    # 画像を追加
    for image_url in tweet_info.image_urls:
        match = re.match(r".*\.(.+)\?.*$", image_url)
        if match is None:
            ext = None
        else:
            ext = match.group(1)
        images.insert_ignore(
            ImageModel(
                url=image_url,
                tweet_id=tweet_info.id,
                path=None,
                ext=ext,
            ).dict(),
            ["url"],
        )

    # ツイートを追加
    tweets.insert_ignore(
        TweetModel(
            id=tweet_info.id,
            text=tweet_info.text,
            user_id=tweet_info.user_id,
            created_at=tweet_info.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ).dict(),
        ["id"],
    )

    # ユーザーを追加
    users.insert_ignore(user.dict(), ["id"])
