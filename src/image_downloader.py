from pathlib import Path
from time import sleep

import requests
from loguru import logger

import db
from models import ImageModel, TweetModel


class RecordNotFoundError(Exception):
    pass


class ImageDownloader:
    def __init__(self):
        logger.info("Initializing image downloader.")
        self.save_dir = Path(__file__).parents[1] / "imgs"

    def run(self):
        logger.info("Started image download.")
        images = db.get_undone_images()
        for image in images:
            res = self.download(image.url)
            if res.status_code != 200:
                logger.error(
                    f"Response status code was {res.status_code} in {image.url}"
                )
                continue
            try:
                path: str = self.save(res, image)
            except RecordNotFoundError:
                logger.error(f"DB Error occurred in image id: {image.id}")
                continue
            self.update_db(image, path)
            logger.debug(f"Downloaded: {image.url}")
        logger.info("Finished image download.")

    def download(self, url: str) -> requests.Response:
        sleep(1)
        return requests.get(url)

    def save(self, response: requests.Response, image: ImageModel) -> str:
        tweet = db.get_tweet(image.tweet_id)
        if tweet is None:
            raise RecordNotFoundError
        filepath = self.make_filepath(tweet, image)
        with filepath.open(mode="wb") as f:
            f.write(response.content)
        return str(filepath)

    def update_db(self, image: ImageModel, path: str) -> None:
        record = image.dict()
        record["downloaded"] = 1
        record["path"] = path
        db.images.update(record, ["url"])

    def make_filepath(self, tweet: TweetModel, image: ImageModel) -> Path:
        number = 1
        filepath = self.save_dir / self._make_filename(tweet.id, image.ext, number)
        while filepath.exists():
            number += 1
            filepath = self.save_dir / self._make_filename(tweet.id, image.ext, number)
        return filepath

    @staticmethod
    def _make_filename(tweet_id: int, ext: str | None, number: int) -> str:
        return f"{tweet_id}_{number}.{ext or 'unk'}"


if __name__ == "__main__":
    ImageDownloader().run()
