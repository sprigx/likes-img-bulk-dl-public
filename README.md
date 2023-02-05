# likes-img-bulk-dl-public

【供養】2023/2/9 廃止予定の Twitter API をつかって自分のいいねしたツイートの画像をまとめて DL するやつ

# 使い方

[pyenv](https://github.com/pyenv/pyenv)をインストール (リンク参照)

続いて以下のように環境構築 (Linux or MacOS の場合)

```shell
$ pyenv install 3.10.5
$ git clone git@github.com:sprigx/likes-img-bulk-dl-public.git
$ cd likes-img-bulk-dl-public
$ echo "3.10.5" > .python-version
$ pip install poetry
$ poetry install
```

[【Twitter】API キー利用申請から発行までの手順解説｜ツイッター運用自動化アプリ作成に向けた環境構築](https://di-acc2.com/system/rpa/9688/)を参考に Twitter API の利用申請

ディレクトリ直下に".env"という名前でテキストファイルを作成し、先程取得した API のキーなどを書く

```.env
CONSUMER_KEY = "hogefuga1234..."
CONSUMER_SECRET = "foobar2001..."
ACCESS_TOKEN_SECRET = "fugapiyo..."
BEARER_TOKEN = "AAAAAAA..."
ACCESS_TOKEN = "barbuz..."
ACCESS_TOKEN_SECRET = "fugahoge..."
DEVELOPMENT = 1
```

src/main.py にユーザーネーム (@の英数字)を書く

```python
from crawler import LikesCrawler

dev = True
if dev:
    import colored_traceback.always

LikesCrawler("ここに書く").batch_run()
```

いいねしたツイートを DB に保存 (量が多ければかなり時間かかる)

```shell
$ poetry run python src/main.py
```

DB に保存したツイートの画像を imgs フォルダに DL (量が多ければかなり時間かかる)

```shell
$ poetry run python src/image_downloader.py
```

おわり

# 仕様

- 画像ファイルの命名規則は"ツイート id(数字)\_連番(数字)"
- アクセスレートは 1 request/sec
- 一つのフォルダに全部の画像を入れるので数が多いとフォルダがとても重くなるかもしれない

# ライセンス

"likes-img-bulk-dl-public" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
