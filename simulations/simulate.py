from re import S
import pandas as pd
import datetime as dt
import yfinance as yf
import csv

from test_app.simulator import Simulator

period = 30#270

symbols = []

budget = 300
trade_budget = 100

buy_ins = [0.99]#[0.98, 0.99]#[0.97, 0.975, 0.98, 0.985, 0.99]
sells = [1.005]#[1.005, 1.01]#[1, 1.005, 1.01, 1.015, 1.02, 1.025, 2]
#!!
stop = 0.9
dax_limits = [0.995] #[0.985, 0.99, 0.995, 1]

with open('simulations/symbols.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        sym = line[0]
        symbols.append(sym)

def write_data(dl, bi, s, transactions, total):
    with open('testdata/allstock-test-2804.csv', 'a+') as f:
        writer = csv.writer(f)
        for transaction in transactions:
            writer.writerow([dl, bi, s, transaction['symbol'], transaction['buy_price'], transaction['sell_price'], transaction['quantity'], transaction['bought_time'], transaction['sold_time']])
        f.close()
    with open('testdata/allstock-test-2804-result.csv', 'a+') as f:
        writer = csv.writer(f)
        writer.writerow([dl, bi, s, total])
        f.close()

for dax_limit in dax_limits:
    for buy_in in buy_ins:
        for sell in sells:
            print(dax_limit)
            print(buy_in)
            print(sell)
            pf_transactions = {}
            simulator = Simulator(symbols, budget, trade_budget, buy_in, sell, stop, {}, dax_limit, False, False)
            simulator.run_test(period)
            pf_transactions = simulator.transactions
            print(simulator.get_portfolio_value())
            #write_data(dax_limit, buy_in, sell, pf_transactions, simulator.get_portfolio_value())
