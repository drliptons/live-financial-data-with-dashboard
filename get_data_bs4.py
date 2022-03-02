import random
import time
import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/98.0.4758.109 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

Stock = ["AAPL", "MSFT", "NFLX", "PYPL", "FB", "TWTR", "AMZN"]

FILE_NAME = "stock_data.csv"


def get_data(_symbol):
    """
    Get live data with beautifulsoup
    :param _symbol: stock symbol. Ex: For Apple => AAPL
    :return:
    """
    # Retrieve live data
    url = "https://finance.yahoo.com/quote/" + _symbol + "?p=" + _symbol + "&.tsrc=fin-srch"
    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get price data
    _price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
    _price = _price.replace(",", "")
    _price = pd.to_numeric(_price, downcast="float")

    # Get volume data
    _volume = soup.find('fin-streamer', {'data-field': 'regularMarketVolume'}).text
    _volume = _volume.replace(",", "")
    _volume = int(_volume)
    _volume = f"{_volume:,}"

    # Get changes data
    _changes_list = soup.find_all('fin-streamer', {'class': 'Fw(500) Pstart(8px) Fz(24px)'})
    _change_real = _changes_list[0].text
    _changes_pct = _changes_list[1].text
    _change = f"{_change_real} {_changes_pct}"

    return _price, _change, _volume


def start_get_data_bs4():
    """
    Main loop for getting live data
    """
    # Loop getting live data
    while True:
        time_stamp = datetime.datetime.now() - datetime.timedelta(hours=6)  # current time of the stock market
        time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")  # format time string

        info = []  # create empty list for the data

        # Getting data for each stock
        for symbol in Stock:
            price, change, volume = get_data(symbol)  # get live data
            info.append(price)  # add price to info list
            info.extend([change])  # add changes to info list
            info.extend([volume])  # add volume to info list
            time.sleep(random.randint(1, 3))  # delay before getting next stock data. Here to prevent server ban

        # Save data to a csv file
        col = [time_stamp]  # new list with timestamp as first data
        col.extend(info)  # add stock info to list
        df = pd.DataFrame(col)  # create dataframe
        df = df.T  # transpose dataframe
        df.to_csv(FILE_NAME, mode="a", header=False)  # save data to csv file
        print(col)  # print stock data to console

        # Delay before getting next loop. Here to prevent server ban
        time.sleep(random.randint(10, 12))


# Start and loop getting live data
start_get_data_bs4()
