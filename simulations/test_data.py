from re import S
import pandas as pd
import datetime as dt
import yfinance as yf
import csv

from test_app.simulator import Simulator

period = 70

symbols = []

budget = 1000
trade_budget = 100

buy_in = 0.98
sell = 1.01
#!!
stop = 0.9
dax_limit = 1

with open('simulations/symbols-dax.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        sym = line[0]
        symbols.append(sym)

with open('simulations/symbols-mdax.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        sym = line[0]
        symbols.append(sym)

pf_transactions = {}

for sym in symbols:
#for sym in ["ALV.DE", "BAS.DE"]:
    print(sym)
    simulator = Simulator([sym], 1000, 100, buy_in, sell, stop, {}, dax_limit, True)
    simulator.run_test(period)
    pf_transactions[sym] = simulator.transactions
    print(simulator.get_portfolio_value())

#simulator = Simulator(symbols, 1010, 500, buy_in, sell, stop, {}, dax_limit)
#simulator.run_test(60)
#pf_transactions[sym] = simulator.transactions
#print(simulator.get_portfolio_value())

def write_data():
    with open('single-stock-test-09.csv', 'a+') as f:
        writer = csv.writer(f)
        for sym in pf_transactions:
            for transaction in pf_transactions[sym]:
                writer.writerow([transaction['symbol'], transaction['buy_price'], transaction['sell_price'], transaction['quantity'], transaction['bought_time'], transaction['sold_time']])
        f.close()

write_data()