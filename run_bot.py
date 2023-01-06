import yfinance as yf
import pandas as pd
import datetime as dt
import csv

from bot.trade_bot import TradeBot

period = 1

symbols = []

budget = 500
trade_budget = 160

buy_in = 0.98
sell = 1.005
stop = 0.9
#dax_limit = 1

with open('bot/stocks.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        sym = line[0]
        symbols.append(sym)

bot = TradeBot(symbols, budget, trade_budget, buy_in, sell, stop)
bot.run_bot()