from crawler import LikesCrawler

dev = True
if dev:
    import colored_traceback.always

LikesCrawler("your_twitter_username_here").batch_run()
