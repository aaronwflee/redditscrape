import pandas as pd
import configparser
import collections
import re
import string

import praw

config = configparser.ConfigParser()
config.read("config.ini")
reddit_config = config["reddit.com"]

reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["secret"],
    user_agent=reddit_config["agent"]
)

NASDAQ_SYMBOLS = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
COMMON_WORDS = "https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"


def get_valid_tickers(url=NASDAQ_SYMBOLS, remove_common_english=True):
    valid_tickers = set(pd.read_csv(url, sep="|")["Symbol"].unique())
    if remove_common_english:
        english_words = pd.read_csv(COMMON_WORDS, header=None).iloc[:, 0]
        english_words = set(english_words.str.upper())
        return valid_tickers - english_words

    return valid_tickers


VALID_TICKERS = get_valid_tickers()


def has_no_numbers(text):
    return not bool(re.search(r"\d", text))


def tickers_only(text, valid_tickers=VALID_TICKERS):
    cleaned = [word  # .upper()  # turn all to upper case for consistency
               .translate(str.maketrans("", "", string.punctuation)) \
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
        print("REDDIT SCORE: ",
              submission.score,  # Output: the submission"s score
              submission.title  # Output: the submission"s title
              )

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
        overall_ticker_counter.update(ticker_counter)
        print("___________________________________________________________\n")

    return overall_ticker_counter


all_posts = get_posts("wallstreetbets", how="hot")
print(all_posts)
