import configparser
import collections
import re
import string

import praw

from stocks import get_valid_tickers, stock_data

config = configparser.ConfigParser()
config.read("config.ini")
reddit_config = config["reddit.com"]

reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["secret"],
    user_agent=reddit_config["agent"]
)


VALID_TICKERS = get_valid_tickers()


def has_no_numbers(text):
    return not bool(re.search(r"\d", text))


def text_to_tickers_list(text, valid_tickers=VALID_TICKERS):
    cleaned = [word
               .translate(str.maketrans("", "", string.punctuation))
               .strip()
               .replace("\n", "")
               for word in text.split(" ")]

    return [ticker for ticker in cleaned if ticker in valid_tickers]


def get_posts(subreddit, how="hot", n_posts=10):

    print(f"GETTING TICKER MENTIONS FROM HOT {n_posts} POSTS FROM {subreddit}")

    # assume you have a reddit instance bound to variable `reddit`
    subreddit = reddit.subreddit(subreddit)

    sort = {"hot": subreddit.hot,
            "top": subreddit.top,
            "new": subreddit.new}

    list_of_posts = sort[how](limit=n_posts)
    overall_ticker_counter = collections.Counter()

    # options = [controversial, gilded, hot, new, rising, top]
    for submission in list_of_posts:
        # print("REDDIT SCORE: ",
        #       submission.score,  # Output: the submission"s score
        #       submission.title  # Output: the submission"s title
        #       )

        top_level_comments = list(submission.comments)

        ticker_counter = collections.Counter()
        for comment in top_level_comments:
            try:
                full_text = comment.body
                tickers = text_to_tickers_list(full_text)
                ticker_counter.update(tickers)
            except AttributeError:
                pass

        # print(ticker_counter)
        overall_ticker_counter.update(ticker_counter)
        # print("___________________________________________________________\n")

    return overall_ticker_counter


all_posts = get_posts("wallstreetbets", how="hot")
print(all_posts)
