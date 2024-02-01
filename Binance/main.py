import func_claculate_trend
import json
import time
from datetime import datetime


def step1():
    tradeable_tickers = func_claculate_trend.get_tradeable_symbols()
    counts = 0
    kline_info_dict = {}
    print("Gathering kline info...")
    for ticker in tradeable_tickers:
        counts += 1
        kline_info = func_claculate_trend.get_kline(ticker)
        if (len(kline_info)) > 0:
            kline_info_dict[ticker] = kline_info
            # counts += 1
    print(f"{counts} items stored")
    # else:
    #     print(f"{counts} items is not stored")

    if len(kline_info_dict) > 0:
        with open("1_kline_info.json", "w") as fp:
            json.dump(kline_info_dict, fp, indent=4)
        print("kline saved successfully.")

    print("Gathering funding rate...")
    funding_rate = func_claculate_trend.get_funding_rate(tradeable_tickers)
    if len(funding_rate) > 0:
        with open("1_funding_rate.json", "w") as fp:
            json.dump(funding_rate, fp, indent=4)
        print("funding rate saved successfully.")


def step2():
    with (open("1_kline_info.json") as json_file):
        kline_info = json.load(json_file)
        uptrend_list = []
        downtrend_list = []
        if len(kline_info) > 0:
            new_uptrend_list = func_claculate_trend.get_up_trend(kline_info)
            if len(new_uptrend_list) > 0:
                for i in new_uptrend_list:
                    func_claculate_trend.add_to_self_remove_list(i, uptrend_list)
            new_downtrend_list = func_claculate_trend.get_down_trend(kline_info)
            if len(new_downtrend_list) > 0:
                for i in new_downtrend_list:
                    func_claculate_trend.add_to_self_remove_list(i, downtrend_list)

            uptrend_entry = func_claculate_trend.get_up_trend_entry_zone(uptrend_list, kline_info)
            downtrend_entry = func_claculate_trend.get_down_trend_entry_zone(downtrend_list, kline_info)

            new_uptrend_list_str = "*New UPTREND LIST:  " + str(new_uptrend_list).replace(
                                ",", "  ").replace("[", "").replace(
                                "]", "").replace("_", "").replace("'", "") + "*"
            uptrend_list_str = "UPTREND LIST:  " + str(uptrend_list).replace(",", "  ").replace(
                                "[", "").replace("]", "").replace(
                                "_", "").replace("'", "")
            uptrend_entry_str = "UPTREND ENTRY:  " + str(uptrend_entry).replace(",", "  ").replace(
                                "[", "").replace("]", "").replace(
                                "_", "").replace("'", "")
            new_downtrend_list_str = "*New DOWNTREND LIST:  " + str(new_downtrend_list).replace(
                                ",", "  ").replace("[", "").replace(
                                "]", "").replace("_", "").replace("'", "") + "*"
            downtrend_list_str = "DOWNTREND LIST:  " + str(downtrend_list).replace(",", "  ").replace(
                                "[", "").replace("]", "").replace(
                                "_", "").replace("'", "")
            downtrend_entry_str = "DOWNTREND ENTRY:  " + str(downtrend_entry).replace(",", "  ").replace(
                                "[", "").replace("]", "").replace(
                                "_", "").replace("'", "")

            message = (new_uptrend_list_str + "\n" + uptrend_list_str + "\n" + uptrend_entry_str + "\n\n" +
                       new_downtrend_list_str + "\n" + downtrend_list_str + "\n" + downtrend_entry_str + "\n")
            print(message)

            if len(new_uptrend_list) > 0 or len(uptrend_list) > 0 or len(new_downtrend_list) > 0 or len(downtrend_list) > 0:
                telegram_message = func_claculate_trend.send_telegram_message(message)
                print(telegram_message)

    with open("1_funding_rate.json") as json_file2:
        funding_rate = json.load(json_file2)
        extreme_funding_rate = {}
        for ticker in funding_rate.keys():
            if funding_rate[ticker] >= 1 or funding_rate[ticker] <= -1:
                extreme_funding_rate[ticker] = funding_rate[ticker]
        extreme_funding_rate_str = "*EXTREME FUNDING RATE:*  " + str(extreme_funding_rate).replace(
            "{", "").replace("}", "").replace("'", "").replace(
            ",", ", ").replace("-", "\-").replace(".", "\.")
        print(extreme_funding_rate_str)
        if len(extreme_funding_rate) > 0:
            telegram_message = func_claculate_trend.send_telegram_message(extreme_funding_rate_str)
            print(telegram_message)


if __name__ == "__main__":
    while True:
        step1()
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        print(current_time)
        step2()
        time.sleep(3600)
