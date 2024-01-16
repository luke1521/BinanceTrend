import pandas as pd
from binance.um_futures import UMFutures
import datetime
import time
import numpy as np
import math
import requests


um_futures_client = UMFutures()
time_start_date = datetime.datetime.now() - datetime.timedelta(hours=500)
time_start_second = int(time_start_date.timestamp()) * 1000


def get_tradeable_symbols():
    ticker_list = []
    symbols = um_futures_client.exchange_info()["symbols"]
    for sym in symbols:
        if sym["quoteAsset"] == "USDT" and sym["status"] == "TRADING":
            ticker_list.append(sym["symbol"])

    return ticker_list


def get_kline(ticker):
    price = um_futures_client.klines(symbol=ticker, interval="1h", startTime=time_start_second)
    time.sleep(0.1)
    if len(price) != 500:
        return []

    return price


def get_ema(kline, length):
    df = pd.DataFrame(kline)
    ema = df.ewm(span=length, min_periods=length, adjust=False).mean()
    ema_list = ema.values.tolist()
    return ema_list


def extract_close_price(ticker_kline):
    close_price = []
    for price_values in ticker_kline:
        if math.isnan(float(price_values[4])):
            return []
        close_price.append(float(price_values[4]))

    return close_price


def get_up_trend(kline):
    uptrend_tickers = []
    ema_fast = {}
    ema_slow = {}
    for ticker in kline.keys():
        close = extract_close_price(kline[ticker])
        ema89 = get_ema(close, 89)[-300:]
        ema144 = get_ema(close, 144)[-300:]
        ema89 = [item for sublist in ema89 for item in sublist]
        ema144 = [item for sublist in ema144 for item in sublist]

        ema_fast[ticker] = ema89
        ema_slow[ticker] = ema144

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema89np = np.array(ema_fast[ticker1])
                ema144np = np.array(ema_slow[ticker2])

                if np.all(ema89np > ema144np):
                    uptrend_tickers.append(ticker1)
                    uptrend_tickers = list(set(uptrend_tickers))

    return uptrend_tickers


def get_up_trend_entry_zone(uptrend_tickers, kline):
    ema_fast = {}
    ema_slow = {}
    up_trend_entry_ticker = []
    for ticker_up in uptrend_tickers:
        for ticker in kline.keys():
            if ticker_up == ticker:
                close = extract_close_price(kline[ticker])
                ema13 = get_ema(close, 13)[-1]
                ema21 = get_ema(close, 21)[-1]
                ema_fast[ticker] = ema13
                ema_slow[ticker] = ema21

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema13np = np.array(ema_fast[ticker1])
                ema21np = np.array(ema_slow[ticker2])

                if np.all(ema13np < ema21np):
                    up_trend_entry_ticker.append(ticker1)

    return up_trend_entry_ticker


def get_down_trend(kline):
    downtrend_tickers = []
    ema_fast = {}
    ema_slow = {}
    for ticker in kline.keys():
        close = extract_close_price(kline[ticker])
        ema89 = get_ema(close, 89)[-300:]
        ema144 = get_ema(close, 144)[-300:]
        ema89 = [item for sublist in ema89 for item in sublist]
        ema144 = [item for sublist in ema144 for item in sublist]

        ema_fast[ticker] = ema89
        ema_slow[ticker] = ema144

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema89np = np.array(ema_fast[ticker1])
                ema144np = np.array(ema_slow[ticker2])

                if np.all(ema89np < ema144np):
                    downtrend_tickers.append(ticker1)
                    downtrend_tickers = list(set(downtrend_tickers))

    return downtrend_tickers


def get_down_trend_entry_zone(uptrend_tickers, kline):
    ema_fast = {}
    ema_slow = {}
    down_trend_entry_ticker = []
    for ticker_up in uptrend_tickers:
        for ticker in kline.keys():
            if ticker_up == ticker:
                close = extract_close_price(kline[ticker])
                ema13 = get_ema(close, 13)[-1]
                ema21 = get_ema(close, 21)[-1]
                ema_fast[ticker] = ema13
                ema_slow[ticker] = ema21

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema13np = np.array(ema_fast[ticker1])
                ema21np = np.array(ema_slow[ticker2])

                if np.all(ema13np > ema21np):
                    down_trend_entry_ticker.append(ticker1)

    return down_trend_entry_ticker


def get_sideway_ticker(kline):
    all_tickers = []
    for ticker in kline.keys():
        all_tickers.append(ticker)
    up_trend_tickers = get_up_trend(kline)
    down_trend_tickers = get_down_trend(kline)
    sideway_tickers = list(set(all_tickers) - set(up_trend_tickers) - set(down_trend_tickers))

    return sideway_tickers


def get_sideway_zscore(sideway_tickers, kline):
    sideway_ticker_zscore = {}
    for sideway_ticker in sideway_tickers:
        for ticker in kline.keys():
            if sideway_ticker == ticker:
                close = extract_close_price(kline[sideway_ticker])
                df = pd.DataFrame(close)
                mean = df.rolling(center=False, window=200).mean()
                std = df.rolling(center=False, window=200).std()
                x = df.rolling(center=False, window=1).mean()
                df["ZSCORE"] = (x - mean) / std
                sideway_ticker_zscore[sideway_ticker] = df["ZSCORE"].to_dict()[499]

    return sideway_ticker_zscore


def get_sideway_entry(sideway_zscore):
    sideway_long_entry = []
    sideway_short_entry = []
    for ticker in sideway_zscore.keys():
        if sideway_zscore[ticker] > 2:
            sideway_short_entry.append(ticker)
        if sideway_zscore[ticker] < -2:
            sideway_long_entry.append(ticker)

    return sideway_long_entry, sideway_short_entry


def send_telegram_message(message):
    telegram_token = "6175801430:AAFKr7osgB7s36HhAI2Drhtbhgq_eSvaPZ0"
    telegram_id = "1235292983"
    api = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_id}&parse_mode=MarkdownV2&text={message}"
    res = requests.get(api)
    if res.status_code == 200:
        return "Telegram message sent"
    else:
        return "Telegram send failed"


def get_zone_tickers(kline):
    zone_tickers = []
    for ticker in kline.keys():
        close = extract_close_price(kline[ticker])
        ema200 = get_ema(close, 200)[-200:]
        min_close = min(close[-200:])
        max_close = max(close[-200:])
        res_min = []
        res_max = []
        for i in ema200:
            res_min.append((i[0] - min_close) / i[0])
            res_max.append((max_close - i[0]) / i[0])
        if np.all(np.array(res_min) < 0.08) and np.all(np.array(res_max) < 0.08):
            zone_tickers.append(ticker)
    return zone_tickers
