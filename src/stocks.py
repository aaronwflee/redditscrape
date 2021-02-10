import pandas as pd
import yfinance as yf


TRADED_SYMBOLS = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
# NYSE_SYMBOLS = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
# NASDAQ_SYMBOLS = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
COMMON_WORDS = "https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"


def get_valid_tickers(remove_common_english=True, remove_single_letter=True):
    valid_tickers = set(pd.read_csv(
        TRADED_SYMBOLS, sep="|")["Symbol"].unique())

    if remove_common_english:
        english_words = pd.read_csv(COMMON_WORDS, header=None).iloc[:, 0]
        english_words = set(english_words.str.upper())
        valid_tickers = valid_tickers - english_words

    if remove_single_letter:
        valid_tickers = {ticker for ticker in valid_tickers
                         if len(str(ticker)) > 1}

    return valid_tickers


def retrieve_stock_prices(tickers="GME AMC TSLA GM":
    stock_data_raw = yf.download(tickers, period="1mo", group_by='ticker')
    today = stock_data_raw.index[-1]

    stock_data = stock_data_raw.stack().loc[today].transpose()
    stock_data.columns = [var.lower().replace(" ", "_")
                          for var in stock_data.columns]

    deltas = {"1d": 1,
            "3d": 3,
            "1w": 5,
            "1m": len(stock_data_raw) - 1}

    for diff_label, diff, in deltas.items():
        abs_change = stock_data_raw.unstack()
                                   .diff(diff)
                                   .loc[:, "Adj Close", today]
        pct_change = stock_data_raw.unstack()
                                   .pct_change(diff)
                                   .multiply(100)
                                   .loc[:, "Adj Close", today]
        stock_data[f"abs_change_{diff_label}"] = abs_change
        stock_data[f"pct_change_{diff_label}"] = pct_change

    return stock_data
