import datetime
from datetime import datetime

import numpy as np
import talib as ta
from binance.client import Client
from telegram import Update, ForceReply
from telegram.ext import Updater, CallbackContext
# from telegram.ext import CommandHandler, MessageHandler, Filters


class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)


class TelegramBot:
    def __init__(self):
        self.buy_list = []
        self.sell_list = []
        self.token = self.read()
        self.updater = Updater(self.token)
        self.time = datetime.now()
        self.dispatcher = self.updater.dispatcher

    def read(self):
        token = open('token.txt', "r")
        data = token.read()
        token.close()
        return data

    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        data = f'Hi {user.mention_markdown_v2()}\!\nAvailable Commands:\n/buy for Buy Signals\n/sell for Sell Signals'
        update.message.reply_markdown_v2(data, reply_markup=ForceReply(selective=True))

    def buy(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            f'(T3--{interval}) BUY LIST => {self.buy_list}\nAnalyze Time: {self.time}')

    def sell(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            f'(T3--{interval}) SELL LIST => {self.sell_list}\nAnalyze Time: {self.time}')

    def echo(self, update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        update.message.reply_text(update.message.text)


def generateTillsonT3(close_array, high_array, low_array, volume_factor, t3Length):
    ema_first_input = (high_array + low_array + 2 * close_array) / 4

    e1 = ta.EMA(ema_first_input, t3Length)

    e2 = ta.EMA(e1, t3Length)

    e3 = ta.EMA(e2, t3Length)

    e4 = ta.EMA(e3, t3Length)

    e5 = ta.EMA(e4, t3Length)

    e6 = ta.EMA(e5, t3Length)

    c1 = -1 * volume_factor * volume_factor * volume_factor

    c2 = 3 * volume_factor * volume_factor + 3 * volume_factor * volume_factor * volume_factor

    c3 = -6 * volume_factor * volume_factor - 3 * volume_factor - 3 * volume_factor * volume_factor * volume_factor

    c4 = 1 + 3 * volume_factor + volume_factor * volume_factor * volume_factor + 3 * volume_factor * volume_factor

    t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    return t3


if __name__ == '__main__':
    filename = 'credentials.txt'
    connection = BinanceConnection(filename)
    interval = '15m'
    pair_one = ['BTCUSDT']
    pair_list = ['BTCUSDT',
                 'ETHUSDT',
                 'BNBUSDT',
                 'ADAUSDT',
                 'XRPUSDT',
                 'XLMUSDT',
                 'LTCUSDT',
                 'TRXUSDT',
                 'ETCUSDT',
                 'LINKUSDT',
                 'HOTUSDT',
                 'XMRUSDT',
                 'MATICUSDT',
                 'ATOMUSDT',
                 'FTMUSDT',
                 'DOGEUSDT',
                 'ALGOUSDT',
                 'CHZUSDT',
                 'KAVAUSDT',
                 'BCHUSDT',
                 'FTTUSDT',
                 'USDTTRY',
                 'EURUSDT',
                 'SOLUSDT',
                 'LRCUSDT',
                 'SNXUSDT',
                 'MANAUSDT',
                 'SANDUSDT',
                 ]
    limit = 1000
    bot = TelegramBot()
    for pair in pair_list:
        print(f'Analyze started for the coin pair: {pair}')
        klines = connection.client.get_klines(symbol=pair, interval=interval, limit=limit)
        # print(f"len of output: {len(klines)}")

        """
        get_klines method returns below parameters;
            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]
        """

        total_volume = 0
        for kline in klines:
            # print(f"output: {kline}")
            total_volume = total_volume + int(float(kline[5]))
        avg_volume = total_volume / 1000
        # avg_volume = int(avg_volume)
        print(f'>>> avg_volume: {avg_volume}')

        last_ten_list = klines[-10:]
        last_ten_volume = 0
        for last in last_ten_list:
            last_ten_volume = last_ten_volume + int(float(last[5]))
        last_ten_avg = last_ten_volume / 10
        # last_ten_avg = int(last_ten_avg)
        print(f'>>> last_ten_avg: {last_ten_avg}')

        volume_alert = False
        if last_ten_avg > avg_volume:
            print(f'***Volume Alert for {pair}***')
            volume_alert = True
        else:
            print(f'***Volume Normal for {pair}***')
            volume_alert = False
            continue

        open_time = [int(entry[0]) for entry in klines]
        openP = [float(entry[1]) for entry in klines]
        highP = [float(entry[2]) for entry in klines]
        lowP = [float(entry[3]) for entry in klines]
        closeP = [float(entry[4]) for entry in klines]

        close_array = np.asarray(closeP)
        high_array = np.asarray(highP)
        low_array = np.asarray(lowP)

        new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
        new_time_x = [date.strftime("%y-%m-%d") for date in new_time]
        volume_factor = 0.7
        t3length = 8
        tt3 = generateTillsonT3(close_array, high_array, low_array, volume_factor=volume_factor, t3Length=t3length)

        """Plot Part"""
        # plt.figure(figsize=(11, 6))
        # plt.plot(new_time_x[400:], close_array[400:], label='Price')
        # plt.plot(new_time_x[400:], tt3[400:], label='Tillson T3')
        # plt.xticks(rotation=90, fontsize=5)
        # plt.title("Tillson T3 Plot for BTC/USDT")
        # plt.xlabel("Open Time")
        # plt.ylabel("Value")
        # plt.legend()
        # plt.show()

        """signal creation part"""
        t3_last = tt3[-1]
        t3_previous = tt3[-2]
        t3_prev_previous = tt3[-3]

        # red to green -> BUY signal
        if t3_last > t3_previous and t3_previous < t3_prev_previous:
            bot.buy_list.append(pair)
            print(f'ALERT: Tillson T3 BUY signal, from red to green for: {pair}')

        # green to red -> SELL signal
        elif t3_last < t3_previous and t3_previous > t3_prev_previous:
            bot.sell_list.append(pair)
            print(f'ALERT: Tillson T3 SELL signal, from green to red for: {pair}')

    print("*********FINAL***RESULT*********")
    print("***************************************")
    print(f'***(T3--{interval})_BUY_LIST: {bot.buy_list}')
    print("***************************************")
    print(f'***(T3--{interval})_SELL_LIST: {bot.sell_list}')
    print("***************************************")
    # print("Telegram Bot is Starting...")
    # bot.dispatcher.add_handler(CommandHandler('start', bot.start))
    # bot.dispatcher.add_handler(CommandHandler('buy', bot.buy))
    # bot.dispatcher.add_handler(CommandHandler('sell', bot.sell))
    # bot.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bot.echo))
    # bot.updater.start_polling()
    # print("Telegram Bot started, press CTRL+C to stop...")
    # bot.updater.idle()
