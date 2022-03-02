import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick_ohlc
import datetime
import math

# Size visualization
#----------------------------------------------#-------------------------#
#                                              # ax2 Line chart [0, 4:6] #
#                                              #-------------------------#
#                                              # ax3 Line chart [1, 4:6] #
#                    ax1                       #-------------------------#
#                Candle Stick                  # ax4 Line chart [2, 4:6] #
#                 [0:4, 0:4]                   #-------------------------#
#                                              # ax5 Line chart [3, 4:6] #
#----------------------------------------------#-------------------------#
#            ax8 Bar chart [4, 0:4]            # ax6 Line chart [4, 4:6] #
#----------------------------------------------#-------------------------#
#            ax9 Line chart [5, 0:4]           # ax7 Line chart [5, 4:6] #
#----------------------------------------------#-------------------------#

# Configure window size
fig = plt.figure(figsize=(8, 6), dpi=100)  # Set figure size figsize=(W, H)
fig.patch.set_facecolor("#121416")  # Set face color to bluish black
gs = fig.add_gridspec(6, 6)  # Grid will be 6x6
ax1 = fig.add_subplot(gs[0:4, 0:4])  # Set ax1 HxW
ax2 = fig.add_subplot(gs[0, 4:6])
ax3 = fig.add_subplot(gs[1, 4:6])
ax4 = fig.add_subplot(gs[2, 4:6])
ax5 = fig.add_subplot(gs[3, 4:6])
ax6 = fig.add_subplot(gs[4, 4:6])
ax7 = fig.add_subplot(gs[5, 4:6])
ax8 = fig.add_subplot(gs[4, 0:4])
ax9 = fig.add_subplot(gs[5, 0:4])

# Constant
Stock = ["AAPL", "MSFT", "NFLX", "PYPL", "FB", "TWTR", "AMZN"]
FILE_NAME = "stock_data.csv"


def figure_design(ax):
    """
    Set up faced layout for each subplot
    :param ax: subplot to set up
    """
    ax.set_facecolor("#091217")  # face color
    ax.tick_params(axis="both", labelsize=10, colors="white")  # tick labels
    ax.ticklabel_format(useOffset=False)
    ax.spines["bottom"].set_color("#808080")
    ax.spines["top"].set_color("#808080")
    ax.spines["left"].set_color("#808080")
    ax.spines["right"].set_color("#808080")


def subplot_plot(ax, symbol, data, latest_price, latest_changes):
    """
    Plot stock figure for a small window
    :param ax: location
    :param symbol: stock symbol
    :param data: dataframe
    :param latest_price: latest price
    :param latest_changes: latest change
    """
    # Clear previous values
    ax.clear()
    # Plot graph
    # x-axis: list(range(1, len(data["close"]) + 1))
    # y-axis: data["close"]
    ax.plot(list(range(1, len(data["close"]) + 1)), data["close"], color="white", linewidth=2)

    # Calculate data to plot
    ymin = data["close"].min()
    ymax = data["close"].max()
    ystd = data["close"].std()

    # Set y-axis limit
    if not math.isnan(ymax) and ymax != 0:  # check if value is null (at the beginning)
        ax.set_ylim([ymin - ystd * 0.5, ymax + ystd * 3])  # set boundary

    # Set stock symbl text
    ax.text(0.02, 0.95, symbol, transform=ax.transAxes, color="#FFBF00", fontsize=7, fontweight="bold",
            horizontalalignment="left", verticalalignment="top")

    # Set stock latest price
    ax.text(0.25, 0.95, latest_price, transform=ax.transAxes, color="white", fontsize=7, fontweight="bold",
            horizontalalignment="left", verticalalignment="top")

    # Set stock latest change
    if latest_changes[0] == "+":  # price going up
        colorcode = "#18b800"
    else:  # price going down
        colorcode = "#ff3503"
    # Plot text
    ax.text(0.5, 0.95, latest_changes, transform=ax.transAxes, color=colorcode, fontsize=7, fontweight="bold",
            horizontalalignment="left", verticalalignment="top")

    # Plot graph
    figure_design(ax)
    # Set axis visibility
    ax.axes.xaxis.set_visible(False)  # x-axis visibility
    ax.axes.yaxis.set_visible(False)  # y-axis visibility


def string_to_number(df, column):
    """
    Convert string into float
    :param df: dataframe to convert
    :param column: column index to convert
    :return: converted dataframe
    """
    # Check if first value (0) of the column (column) is a string
    if isinstance(df.iloc[0, df.columns.get_loc(column)], str):
        # Replace comma with an empty
        df[column] = df[column].str.replace(",", "")
        # Convert string into float
        df[column] = df[column].astype(float)
    # return converted dataframe
    return df


def compute_rsi(data, time_window):
    """
    Compute rsi values
    :param data: dataframe for calculate rsi
    :param time_window: time window, ex: 14 (for 14 data times)
    :return:
    """
    diff = data.diff(1).dropna()  # drop na (if any)

    # Get only the dimension of the differences
    up_chg = 0 * diff
    down_chg = 0 * diff

    # Get changes
    up_chg[diff > 0] = diff[diff > 0]
    down_chg[diff < 0] = diff[diff < 0]

    # Calculate averages
    up_chg_avg = up_chg.ewm(com=time_window-1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1, min_periods=time_window).mean()

    rs = abs(up_chg_avg / down_chg_avg)
    rsi = 100 - 100 / (1 + rs)

    return rsi


def read_data_ohlc(filename, symbol, use_cols):
    """
    Prepare data from the file into processable values.
    :param filename: file name
    :param symbol: short stock name symbol
    :param use_cols: input column
    :return:
    """
    # read file and convert it to a dataframe
    df = pd.read_csv(filename, header=None, usecols=use_cols,
                     names=["time", symbol, "change", "volume"],
                     index_col="time", parse_dates=["time"])

    # Check if the dataframe has any null value and return the column that contain the null column
    index_with_nan = df.index[df.isnull().any(axis=1)]
    # Drop index with the null value
    df.drop(index_with_nan, axis=0, inplace=True)

    # (Optional since already pass it when reading the file) Set index column
    df.index = pd.DatetimeIndex(df.index)

    # Convert string into numbers
    df = string_to_number(df, symbol)
    df = string_to_number(df, "volume")

    # Get information in the last row (the latest information)
    latest_info = df.iloc[-1, :]  # grab last row
    latest_price = str(latest_info.iloc[0])  # first column contains price
    latest_change = str(latest_info.iloc[1])  # second column contains changes

    # Convert data into a '1Min' timeframe, when having multiple data with in '1Min'
    df_vol = df["volume"].resample("1Min").mean()  # Convert volume into mean value
    data = df[symbol].resample("1Min").ohlc()  # convert into open, high, low, and close values
    data["time"] = data.index  # create index column
    # Convert index into a datetime format
    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")  # format index column

    # Create new columns with moving average values
    data["MA5"] = data["close"].rolling(5).mean()  # MA 5 minutes
    data["MA10"] = data["close"].rolling(10).mean()  # MA 10 minutes
    data["MA20"] = data["close"].rolling(20).mean()  # MA 20 minutes
    data["RSI"] = compute_rsi(data["close"], 14)  # RSI 14

    # Create a new column for the differences between volumes
    data["volume_diff"] = df_vol.diff()  # create new column
    data[data["volume_diff"] < 0] = None  # convert negative volume into 0

    # Check if the dataframe has any null value and return the column that contain the null column
    index_with_nan = data.index[data.isnull().any(axis=1)]  # check
    data.drop(index_with_nan, axis=0, inplace=True)  # drop the column that contain a nan value
    data.reset_index(drop=True, inplace=True)  # reset index

    # Return value
    return data, latest_price, latest_change, df["volume"][-1]


def animate(i):
    """
    Plot the data into a live chart
    :param i:
    :return:
    """
    # Accounting time zone differences
    # time_stamp = datetime.datetime.now() - datetime.timedelta(hours=6)  # time diff between US and Germany
    # time_stamp = time_stamp.strftime("%Y-%m-%d")  # change time format
    # filename = str(time_stamp) + " stock_data.csv"  # define filename file

    # --- PLOT AX1 ---
    # Preparing data for ax1
    data, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[0], [1, 2, 3, 4])

    # capture the range of the data
    candle_counter = range(len(data["open"]) - 1)  # numbers of candles

    # create empty list for adding data
    ohlc = []  # empty list for creating a candle chart
    for candle in candle_counter:
        # x-axis: candle_counter[candle]
        # open, high, low, and close: respectively from data["open"][candle] to data["close"][candle]
        append_me = candle_counter[candle], data["open"][candle], data["high"][candle], data["low"][candle], \
                    data["close"][candle]
        ohlc.append(append_me)  # append values to ohlc list

    ax1.clear()  # clear previous data

    candlestick_ohlc(ax1, ohlc, width=0.4, colorup="#18b800", colordown="#ff3503")  # set candle

    # Plot MA lines into ax1
    ax1.plot(data["MA5"], color="pink", linestyle="-", linewidth=1, label="5 min SMA")
    ax1.plot(data["MA10"], color="orange", linestyle="-", linewidth=1, label="10 min SMA")
    ax1.plot(data["MA20"], color="#08a0e9", linestyle="-", linewidth=1, label="20 min SMA")

    # Plot legends box
    leg = ax1.legend(loc="upper left", facecolor="#121416", fontsize=8)
    for text in leg.get_texts():
        plt.setp(text, color="w")

    # Setup subplot
    figure_design(ax1)

    # Setup text above window
    # Stock symbol
    ax1.text(0.005, 1.05, Stock[0], transform=ax1.transAxes, color="black", fontsize=16, fontweight="bold",
             horizontalalignment="left", verticalalignment="center", bbox=dict(facecolor="#FFBF00"))
    # Stock latest price
    ax1.text(0.35, 1.05, latest_price, transform=ax1.transAxes, color="white", fontsize=16, fontweight="bold",
             horizontalalignment="center", verticalalignment="center")

    # Stock latest changes
    if latest_change[0] == "+":  # if price going of (positive)
        colorcode = "#18b800"
    else:  # if price going down (negative)
        colorcode = "#ff3503"
    # Plot latest change text
    ax1.text(0.75, 1.05, latest_change, transform=ax1.transAxes, color=colorcode, fontsize=16, fontweight="bold",
             horizontalalignment="center", verticalalignment="center")

    # Time stamp text on the right top corner of the window
    time_stamp = datetime.datetime.now()  # set value
    time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")  # set format
    # Plot time stamp
    ax1.text(1.32, 1.05, time_stamp, transform=ax1.transAxes, color="white", fontsize=10, fontweight="bold",
             horizontalalignment="center", verticalalignment="center")

    # Set up graph for ax1
    ax1.grid(True, color="grey", linestyle="-", which="major", axis="both", linewidth=0.3)  # set grid
    ax1.set_xticklabels([])  # x-axis labels to empty

    # --- PLOT AX2 ---
    # Prepare data for ax2
    data_ax2, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[1], [1, 5, 6, 7])
    # Plot ax2
    subplot_plot(ax2, Stock[1], data_ax2, latest_price, latest_change)

    # --- PLOT AX3 ---
    # Prepare data for ax3
    data_ax3, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[2], [1, 8, 9, 10])
    # Plot ax3
    subplot_plot(ax3, Stock[2], data_ax3, latest_price, latest_change)

    # --- PLOT AX4 ---
    # Prepare data for ax4
    data_ax4, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[3], [1, 11, 12, 13])
    # Plot ax4
    subplot_plot(ax4, Stock[3], data_ax4, latest_price, latest_change)

    # --- PLOT AX5 ---
    # Prepare data for ax5
    data_ax5, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[4], [1, 14, 15, 16])
    # Plot ax5
    subplot_plot(ax5, Stock[4], data_ax5, latest_price, latest_change)

    # --- PLOT AX6 ---
    # Prepare data for ax6
    data_ax6, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[5], [1, 17, 18, 19])
    subplot_plot(ax6, Stock[5], data_ax6, latest_price, latest_change)

    # --- PLOT AX7 ---
    # Prepare data for ax7
    data_ax7, latest_price, latest_change, volume = read_data_ohlc(FILE_NAME, Stock[6], [1, 20, 21, 22])
    subplot_plot(ax7, Stock[6], data_ax7, latest_price, latest_change)

    # --- PLOT AX8 BAR CHART ---
    ax8.clear()  # clear previous values

    # Set designs
    figure_design(ax8)  # use the same design as ax1
    ax8.axes.yaxis.set_visible(False)  # hide y-axis values

    # Prepare data for the bar chart
    pos = data["open"] - data["close"] < 0  # positive values
    neg = data["open"] - data["close"] > 0  # negatives values
    data["x_axis"] = list(range(0, len(data["volume_diff"])))  # create x-axis values

    # Create bar chart
    # x-axis: data["x_axis"][pos]
    # y-axis: data["volume_diff"][pos]
    ax8.bar(data["x_axis"][pos], data["volume_diff"][pos], color="#18b800", width=1, align="center")  # positives
    ax8.bar(data["x_axis"][neg], data["volume_diff"][neg], color="#ff3503", width=1, align="center")  # negatives

    ymax = data["volume_diff"].max()  # volume max value
    ystd = data["volume_diff"].std()  # standard deviation

    if not math.isnan(ymax):  # check if there is a nan value
        ax8.set_ylim([0, ymax + ystd * 3])  # set y-axis limit

    # Volume text
    ax8.text(0.01, 0.95, "Volume: " + "{:,}".format(int(volume)), transform=ax8.transAxes, color="white",
             fontsize=10, fontweight="bold",
             horizontalalignment="left", verticalalignment="top")
    # Set up graph for ax8
    ax8.grid(True, color="grey", linestyle="-", which="major", axis="both", linewidth=0.3)  # set grd
    ax8.set_xlim(ax1.get_xlim())  # align x-axis of ax8 with ax1
    ax8.set_xticklabels([])  # hide x-axis label values

    # --- PLOT AX9 LINE CHART ---
    ax9.clear()  # clear all previous values

    # Set designs
    figure_design(ax9)  # use the same design as ax1
    ax9.axes.yaxis.set_visible(False)  # hide y-axis values
    ax9.set_ylim([-5, 105])  # set y-axis limit. Normally [0, 100] but add room for margin
    ax9.set_xlim(ax1.get_xlim())  # align x-axis of ax9 with ax1

    # Set low, middle, and high reference lines
    ax9.axhline(30, linestyle="-", color="green", linewidth=0.5)  # lower line
    ax9.axhline(50, linestyle="-", color="white", linewidth=0.5)  # middle line
    ax9.axhline(70, linestyle="-", color="red", linewidth=0.5)  # higher line

    # Plot ax9 graph
    ax9.plot(data["x_axis"], data["RSI"], color="#08a0e9", linewidth=1.5)

    # Set rsi text in the top-left corner of the graph
    try:
        rsi = str(round(data["RSI"].iloc[-1], 2))
    except IndexError:
        rsi = "..."
    # rsi = str(round(data["RSI"].iloc[-1], 2))
    ax9.text(0.01, 0.95, "RSI(14): " + rsi, transform=ax9.transAxes,
             color="white", fontsize=10, fontweight="bold",
             horizontalalignment="left", verticalalignment="top")

    # Create time function for the x-axis
    xdate = [i for i in data["time"]]  # grab time value

    # Process time value for the x-axis
    def mydate(x, pos=None):
        try:
            t = xdate[int(x)].strftime("%H:%M")
            return t
        except IndexError:
            return ""

    # Set up a-axis
    ax9.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))  # set x-axis value
    ax9.grid(True, color="grey", linestyle="-", which="major", axis="both", linewidth=0.3)  # set grid
    ax9.tick_params(axis="x", which="major", labelsize=8)  # show x-axis value


def start_dashboard():
    """
    Init and run dashboard
    """
    anim = animation.FuncAnimation(fig, animate, interval=1)
    plt.show()


# Run dashboard
start_dashboard()
