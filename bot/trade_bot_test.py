import yfinance as yf
import pandas as pd
import datetime as dt
import csv
from bot.order_bot import OrderBot

class TradeBotTest(object):
    
    def __init__(self, symbols, budget, trade_budget, buy_in, sell, stop, positions={}, sell_remaining=True):
        self.symbols = symbols
        self.budget  = budget
        self.trade_budget = trade_budget
        self.buy_in = buy_in
        self.sell = sell
        self.stop = stop
        self.positions = positions
        self.transactions = []
        self.sell_remaining = sell_remaining
        self.order_bot = OrderBot()

    def run_bot(self):
        print("running...")
        cont = True
        self.trade_values = {}
        j = 0
        while(cont):
            print("loop...")
            self.today = dt.date.today()
            #### FOR TESTING
            self.today = self.today.replace(day=11)
            for sym in self.symbols:
                print(sym)
                #### FOR TESTING
                stock_data = self.get_stock_data_testrun(sym, j)
                value = stock_data.iloc[-1].High
                last_datetime = pd.to_datetime(stock_data.iloc[[-1]].index)
                if(last_datetime.date == self.today):
                    if sym not in self.trade_values:
                        self.trade_values[sym] = {
                            'High': value,
                            'Low': value,
                            'Last': 0
                        }
                    else:
                        self.trade_values[sym]['High'] = max(value, self.trade_values[sym]['High'])
                        self.trade_values[sym]['Low'] = min(value, self.trade_values[sym]['Low'])
                    # Buying?
                    if (sym not in self.positions) and (self.trade_values[sym]['High'] * self.buy_in > value) and self.trade_values[sym]['High'] * self.buy_in < self.trade_values[sym]['Last']:
                        if self.budget >= self.trade_budget:
                            self.buy_stock(sym)
                        else:
                            print("Not enough budget...")
                    # If in portfolio
                    if sym in self.positions:
                        self.positions[sym]['value'] = self.positions[sym]['quantity'] * value
                        # Selling?
                        if(value > self.positions[sym]['sell_price']):
                            self.sell_position(sym, self.positions[sym]['sell_price'])
                        elif(value < self.positions[sym]['stop']):
                            self.sell_position(sym, self.positions[sym]['stop'])
                    self.trade_values[sym]['Last'] = value
            now = dt.datetime.now()
            j += 1
            #### FOR TESTING
            if(j >= 507):
            #if(now.hour >= 17 and now.minute >= 27):
                self.empty_portfolio()
                self.log_final_transactions()
                cont = False
            if (j%10 == 0):
                self.log_values() 

    def get_stock_data(self, sym):
        stock = yf.download(tickers=sym, period='1d', interval='1m')
        return stock

    def get_stock_data_testrun(self, sym, j):
        stock = yf.download(tickers=sym, period='1d', interval='1m')
        return stock.head(j + 1)

    def buy_stock(self, sym):
        print('Buying: ' + sym + ' for ' + str(round(self.trade_values[sym]['High'] * self.buy_in, 2)))
        quantity = round(self.trade_budget / (self.trade_values[sym]['High'] * self.buy_in), 2)
        self.positions[sym] = {
            'buy_price': self.trade_values[sym]['High'] * self.buy_in,
            'sell_price': self.trade_values[sym]['High'] * self.sell,
            'stop': self.trade_values[sym]['High'] * self.stop,
            'quantity': quantity,
            'value': quantity * self.trade_values[sym]['High'] * self.buy_in,
            'bought_time': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"+01:00"
        }
        self.budget -= self.trade_budget
        with open('bot/logs/transactions' + self.today.strftime("%y-%m-%d") + '.csv', 'a+') as f:
            writer = csv.writer(f)
            writer.writerow([sym, self.positions[sym]['bought_time'], 'BUY', self.positions[sym]['buy_price'], 
                self.positions[sym]['quantity'], self.positions[sym]['value'], self.positions[sym]['sell_price'],
                self.positions[sym]['stop']])
            f.close()
        self.order_bot.limit_order(sym, quantity, self.trade_values[sym]['High'] * self.buy_in)

    def sell_position(self, sym, price, delete=True):
        print('Selling: ' + sym + ' for ' + str(round(price, 2)))
        self.budget += self.positions[sym]['quantity'] * price
        transaction = {
            'symbol': sym,
            'buy_price': self.positions[sym]['buy_price'],
            'sell_price': price,
            'quantity': self.positions[sym]['quantity'],
            'bought_time': self.positions[sym]['bought_time'],
            'sold_time': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"+01:00"
        }
        self.transactions.append(transaction)
        with open('bot/logs/transactions' + self.today.strftime("%y-%m-%d") + '.csv', 'a+') as f:
            writer = csv.writer(f)
            writer.writerow([sym, transaction['sold_time'], 'SELL', transaction['sell_price'], 
                transaction['quantity'], transaction['value']])
            f.close()
        if delete:
            del self.positions[sym]

    def empty_portfolio(self):
        for sym in self.positions:
            pos = self.positions[sym]
            self.sell_position(sym, pos['value']/pos['quantity'], 'Final', False)
        self.positions = {}

    def log_values(self):
        with open('bot/logs/val' + self.today.strftime("%y-%m-%d") + '.csv', 'a+') as f:
            writer = csv.writer(f)
            for sym in self.trade_values:
                writer.writerow([sym, self.trade_values[sym]['High'], self.trade_values[sym]['Low'], self.trade_values[sym]['Last']])
            f.close()

    def log_final_transactions(self):
        with open('bot/logs/final-transactions' + self.today.strftime("%y-%m-%d") + '.csv', 'a+') as f:
            writer = csv.writer(f)
            for sym in self.transactions:
                for transaction in self.transactions[sym]:
                    writer.writerow([transaction['symbol'], transaction['buy_price'], transaction['sell_price'], transaction['quantity'], transaction['bought_time'], transaction['sold_time']])
            f.close()