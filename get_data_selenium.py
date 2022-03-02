import time
import pandas as pd
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


chrome_driver_path = "/Users/markschwarz/My Files/Python Projects/ChromeDriver/chromedriver"
service = Service(executable_path=chrome_driver_path)
option = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=option)
url_home = "https://finance.yahoo.com/"

Stock = ["AAPL", "MSFT", "NFLX", "PYPL", "FB", "TWTR", "AMZN"]
TIME_DELAY = 30
FILE_NAME = "stock_data.csv"


def get_real_time_data(_symbol):
    """
    Get real time data with Selenium
    :param _symbol:
    :return:
    """
    # Open website
    url = "https://finance.yahoo.com/quote/" + _symbol + "?p=" + _symbol + "&.tsrc=fin-srch"
    driver.get(url)

    # Try to retrieve live data
    try:
        price = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]"
                                              "/div[1]/div[5]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/"
                                              "fin-streamer[1]").text
        change = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]"
                                               "/div[1]/div[5]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/"
                                               "fin-streamer[2]/span[1]").text
        pct_change = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]"
                                                   "/div[1]/div[5]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/"
                                                   "fin-streamer[3]/span[1]").text
        abs_change = change + " " + pct_change
        volume = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]"
                                               "/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]"
                                               "/tr[7]/td[2]/fin-streamer[1]").text
    except Exception as e:
        print(e)
        price, abs_change, volume = "", "", ""

    # return retrieved values
    return price, abs_change, volume


def start_get_data_selenium():
    """
    Main loop for getting live data
    """
    # Handling GDPR popup
    driver.get(url_home)
    driver.implicitly_wait(5)
    # # Try to find consent page
    try:
        driver.find_element(By.ID, "consent-page")
    except Exception as e:
        print(e)

    # # Try to click agree button
    try:
        submit = driver.find_element(By.NAME, "agree")
        submit.click()
    except Exception as e:
        print(e)

    # Loop getting live data
    time_last_update = time.time()
    while True:  # loop program
        time_passed = time.time() - time_last_update  # calculate time passed from last update
        if time_passed > TIME_DELAY:  # Check delay
            time_last_update = time.time()  # reset delay

            info = []  # create empty list for the data
            time_stamp = datetime.datetime.now() - datetime.timedelta(hours=6)  # current time of the stock market
            time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")  # format time string

            # Getting data for each stock
            for symbol in Stock:
                price, change, volume = get_real_time_data(symbol)  # get live data
                info.append(price)  # add price to info list
                info.extend([change])  # add changes to info list
                info.extend([volume])  # add volume to info list

            # Save data to a csv file
            col = [time_stamp]  # new list with timestamp as first data
            col.extend(info)  # add stock info to list
            df = pd.DataFrame(col)  # create dataframe
            df = df.T  # transpose dataframe
            df.to_csv(FILE_NAME, mode="a", header=False)  # save data to csv file
            print(col)  # print stock data to console


# Start and loop getting live data
start_get_data_selenium()
