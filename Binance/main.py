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


def step2():
    with (open("1_kline_info.json") as json_file):
        kline_info = json.load(json_file)
        zone_tickers_old = []
        uptrend_list_old = []
        uptrend_entry_old = []
        downtrend_list_old = []
        downtrend_entry_old = []
        sideway_long_entry_old = []
        sideway_short_entry_old = []
        if len(kline_info) > 0:
            uptrend_list = func_claculate_trend.get_up_trend(kline_info)
            uptrend_entry = func_claculate_trend.get_up_trend_entry_zone(uptrend_list, kline_info)
            downtrend_list = func_claculate_trend.get_down_trend(kline_info)
            downtrend_entry = func_claculate_trend.get_down_trend_entry_zone(downtrend_list, kline_info)
            sideway_tickers = func_claculate_trend.get_sideway_ticker(kline_info)
            sideway_zscore = func_claculate_trend.get_sideway_zscore(sideway_tickers, kline_info)
            sideway_long_entry, sideway_short_entry = func_claculate_trend.get_sideway_entry(sideway_zscore)
            zone_tickers = func_claculate_trend.get_zone_tickers(kline_info)

            # comment out this block on first run
            with open("1_result.json") as json_file2:
                result_old = json.load(json_file2)
                for ticker in result_old["uptrend_list"]:
                    uptrend_list_old.append(ticker)
                for ticker in result_old["uptrend_entry"]:
                    uptrend_entry_old.append(ticker)
                for ticker in result_old["downtrend_list"]:
                    downtrend_list_old.append(ticker)
                for ticker in result_old["downtrend_entry"]:
                    downtrend_entry_old.append(ticker)
                for ticker in result_old["sideway_long_entry"]:
                    sideway_long_entry_old.append(ticker)
                for ticker in result_old["sideway_short_entry"]:
                    sideway_short_entry_old.append(ticker)
                for ticker in result_old["zone"]:
                    zone_tickers_old.append(ticker)

            result = {
                "uptrend_list": uptrend_list,
                "uptrend_entry": uptrend_entry,
                "downtrend_list": downtrend_list,
                "downtrend_entry": downtrend_entry,
                "sideway_long_entry": sideway_long_entry,
                "sideway_short_entry": sideway_short_entry,
                "zone": zone_tickers
            }

            if len(result) > 0:
                with open("1_result.json", "w") as fp:
                    json.dump(result, fp, indent=4)

            uptrend_list_new = list(set(uptrend_list) - set(uptrend_list_old))
            uptrend_entry_new = list(set(uptrend_entry) - set(uptrend_entry_old))
            downtrend_list_new = list(set(downtrend_list) - set(downtrend_list_old))
            downtrend_entry_new = list(set(downtrend_entry) - set(downtrend_entry_old))
            sideway_long_entry_new = list(set(sideway_long_entry) - set(sideway_long_entry_old))
            sideway_short_entry_new = list(set(sideway_short_entry) - set(sideway_short_entry_old))
            zone_new = list(set(zone_tickers) - set(zone_tickers_old))

            uptrend_list_new_str = "*UPDATE:  " + str(uptrend_list_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            uptrend_entry_new_str = "*UPDATE:  " + str(uptrend_entry_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            downtrend_list_new_str = "*UPDATE:  " + str(downtrend_list_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            downtrend_entry_new_str = "*UPDATE:  " + str(downtrend_entry_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            sideway_long_entry_new_str = "*UPDATE:  " + str(sideway_long_entry_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            sideway_short_entry_new_str = "*UPDATE:  " + str(sideway_short_entry_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"
            zone_new_str = "*UPDATE:  " + str(zone_new).replace("', '", "  ").replace(
                "['", "").replace("']", "").replace("[", "").replace(
                "]", "").replace("_", "") + "*"

            uptrend_list_str = "UPTREND LIST:  " + str(uptrend_list).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + uptrend_list_new_str
            uptrend_entry_str = "UPTREND ENTRY:  "+str(uptrend_entry).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + uptrend_entry_new_str
            downtrend_list_str = "DOWNTREND LIST:  " + str(downtrend_list).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + downtrend_list_new_str
            downtrend_entry_str = "DOWNTREND ENTRY:  "+str(downtrend_entry).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + downtrend_entry_new_str
            sideway_long_entry_str = "SIDEWAY LONG:  "+str(sideway_long_entry).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + sideway_long_entry_new_str
            sideway_short_entry_str = "SIDEWAY SHORT:  "+str(sideway_short_entry).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + sideway_short_entry_new_str
            zone_str = "ZONE:  "+str(zone_tickers).replace("', '", "  ").replace(
                                "['", "").replace("']", "").replace("_", "").replace(
                                "[", "").replace("]", "") + "\n" + zone_new_str

            message = (uptrend_list_str + "\n\n" + uptrend_entry_str + "\n\n" + downtrend_list_str + "\n\n" +
                       downtrend_entry_str + "\n\n" + sideway_long_entry_str + "\n\n" + sideway_short_entry_str +
                       "\n\n" + zone_str)
            print(message)
            telegram_message = func_claculate_trend.send_telegram_message(message)
            print(telegram_message)


if __name__ == "__main__":
    while True:
        step1()
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        print(current_time)
        step2()
        time.sleep(3560)
