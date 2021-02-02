import configparser
import re
import collections

import praw


config = configparser.ConfigParser()
config.read("config.ini")
reddit_config = config["reddit.com"]


reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["secret"],
    user_agent=reddit_config["agent"]
)


def has_no_numbers(text):
    return not bool(re.search(r'\d', text))


def tickers_only(txt):
    tickers_only = [word for word in txt.split(" ")
                    if word.isupper() and word.startswith("$")
                    # ignore cases where tickers have numbers for now
                    and has_no_numbers(word)]

    return tickers_only


def get_hot_posts(subreddit, how='hot', n_posts=10):

    print(f"GETTING TICKER MENTIONS FROM HOT {n_posts} POSTS FROM {subreddit}")

    # assume you have a reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit(subreddit)

    hot_posts = subreddit.hot(limit=n_posts)
    # options = [controversial, gilded, hot, new, rising, top]
    for submission in hot_posts:
        print("REDDIT SCORE: ",
              submission.score,  # Output: the submission's score
              submission.title  # Output: the submission's title
              )

        submission.comment_sort = "top"
        top_level_comments = list(submission.comments)

        ticker_counter = collections.Counter()
        for comment in top_level_comments:
            try:
                full_text = comment.body
                tickers = tickers_only(full_text)
                ticker_counter.update(tickers)
            except AttributeError:
                pass

        print(ticker_counter)
        print('___________________________________________________________\n')


get_hot_posts("wallstreetbets")
