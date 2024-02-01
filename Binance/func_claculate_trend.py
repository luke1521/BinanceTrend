import pandas as pd
from binance.um_futures import UMFutures
import datetime
import time
import numpy as np
import math
import requests
import threading


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


def get_funding_rate(tradeable_tickers):
    funding_rate = {}
    for ticker in tradeable_tickers:
        raw = um_futures_client.funding_rate(ticker, **{"limit": 1})
        if len(raw) > 0:
            funding_rate[ticker] = float(raw[0]["fundingRate"]) * 100
            time.sleep(0.1)
    return funding_rate


def get_kline(tradeable_tickers):
    price = um_futures_client.klines(symbol=tradeable_tickers, interval="1h", startTime=time_start_second)
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
        ema89 = get_ema(close, 89)[-200:]
        ema144 = get_ema(close, 144)[-200:]
        ema89_201 = get_ema(close, 89)[-201]
        ema144_201 = get_ema(close, 144)[-201]
        ema89 = [item for sublist in ema89 for item in sublist]
        ema144 = [item for sublist in ema144 for item in sublist]

        ema_fast[ticker] = [ema89, ema89_201]
        ema_slow[ticker] = [ema144, ema144_201]

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema89np = np.array(ema_fast[ticker1][0])
                ema144np = np.array(ema_slow[ticker2][0])

                if np.all(ema89np > ema144np) and ema_fast[ticker1][1] <= ema_slow[ticker2][1]:
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
        ema89 = get_ema(close, 89)[-200:]
        ema144 = get_ema(close, 144)[-200:]
        ema89_201 = get_ema(close, 89)[-201]
        ema144_201 = get_ema(close, 144)[-201]
        ema89 = [item for sublist in ema89 for item in sublist]
        ema144 = [item for sublist in ema144 for item in sublist]

        ema_fast[ticker] = [ema89, ema89_201]
        ema_slow[ticker] = [ema144, ema144_201]

    for ticker1 in ema_fast.keys():
        for ticker2 in ema_slow.keys():
            if ticker1 == ticker2:
                ema89np = np.array(ema_fast[ticker1][0])
                ema144np = np.array(ema_slow[ticker2][0])

                if np.all(ema89np < ema144np) and ema_fast[ticker1][1] >= ema_slow[ticker2][1]:
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


def remove_from_list(item, mylist):
    mylist.remove(item)
    print(f"删除了列表中的项: {item}")


def add_to_self_remove_list(item, mylist):
    mylist.append(item)
    threading.Timer(259200, remove_from_list, args=(item, mylist)).start()


def send_telegram_message(message):
    telegram_token = "6175801430:AAFKr7osgB7s36HhAI2Drhtbhgq_eSvaPZ0"
    telegram_id = "1235292983"
    api = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_id}&parse_mode=MarkdownV2&text={message}"
    res = requests.get(api)
    if res.status_code == 200:
        return "Telegram message sent"
    else:
        return "Telegram send failed"
