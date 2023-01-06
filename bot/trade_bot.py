import yfinance as yf
import pandas as pd
import datetime as dt
import csv
import time
from bot.order_bot import OrderBot
from os.path import exists

class TradeBot(object):
    
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
        self.today = dt.date.today()
        self.trade_values = {}
        self.load_backup()

    def run_bot(self):
        print("running...")
        cont = True
        j = 0
        while(cont):
            print("loop... " + dt.datetime.now().strftime("%H:%M:%S"))
            all_stocks = self.get_stock_data()
            for sym in self.symbols:
                #print(sym)
                stock_data = all_stocks if len(self.symbols) == 1 else all_stocks[sym]
                if(len(stock_data) > 0):
                    value = stock_data.iloc[-1].Close
                    last_datetime = pd.to_datetime(stock_data.iloc[[-1]].index)
                    if(last_datetime.date == self.today):
                        if sym not in self.trade_values:
                            self.trade_values[sym] = {
                                'High': stock_data.iloc[-1].High,
                                'Low': stock_data.iloc[-1].Low,
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
                                self.log_no_buy(sym)
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
            if(now.hour >= 17 and now.minute >= 27):
                self.empty_portfolio()
                self.log_final_transactions()
                cont = False
            if (j%10 == 0):
                self.log_values() 
        time.sleep(5)

    def get_stock_data(self):
        #stock = yf.download(tickers=sym, period='1d', interval='1d')
        stock = yf.download(tickers=self.symbols, period='1d', interval='1d')
        if len(self.symbols) > 1:
            stock.columns = stock.columns.swaplevel(0, 1)
            stock.sort_index(axis=1, level=0, inplace=True)
        return stock

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

    def log_no_buy(self, sym):
        print('Not Buying: ' + sym + ' for ' + str(round(self.trade_values[sym]['High'] * self.buy_in, 2)))
        datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"+01:00"
        with open('bot/logs/transactions' + self.today.strftime("%y-%m-%d") + '.csv', 'a+') as f:
            writer = csv.writer(f)
            writer.writerow([sym, datetime, 'NO-BUY', self.trade_values[sym]['High'] * self.buy_in, 
                0, 0, self.trade_values[sym]['High'] * self.sell,
                self.trade_values[sym]['High'] * self.stop])
            f.close()
        

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
                transaction['quantity'], self.positions[sym]['value']])
            f.close()
        self.order_bot.sell_limit(sym, self.positions[sym]['quantity'], price)
        if delete:
            del self.positions[sym]

    def empty_portfolio(self):
        for sym in self.positions:
            pos = self.positions[sym]
            self.sell_position(sym, pos['value']/pos['quantity'], False)
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
            for transaction in self.transactions:
                writer.writerow([transaction['symbol'], transaction['buy_price'], transaction['sell_price'], transaction['quantity'], transaction['bought_time'], transaction['sold_time']])
            f.close()

    def load_backup(self):
        today_data = yf.download(tickers=self.symbols, period='1d', interval='1d')
        if pd.to_datetime(today_data.iloc[[-1]].index) == self.today:
            for sym in self.symbols:
                if today_data.Close[sym]:
                    self.trade_values[sym] = {
                        'High': today_data.High[sym],
                        'Low': today_data.Low[sym],
                        'Last': today_data.Close[sym]
                    }
        print(self.trade_values)
        self.log_values()
        if exists('bot/logs/transactions' + self.today.strftime("%y-%m-%d") + '.csv'):
            with open('bot/logs/transactions' + self.today.strftime("%y-%m-%d") + '.csv') as f:
                reader = csv.reader(f)
                for l in reader:
                    if l[2] == 'BUY':
                        self.positions[l[0]] = {
                            'buy_price': float(l[3]),
                            'sell_price': float(l[6]),
                            'stop': float(l[7]),
                            'quantity': float(l[4]),
                            'value': float(l[5]),
                            'bought_time': l[1]
                        }
                        self.budget -= float(l[3]) * float(l[4])
                    elif l[2] == 'SELL':
                        sym = l[0]
                        transaction = {
                            'symbol': sym,
                            'buy_price': self.positions[sym]['buy_price'],
                            'sell_price': float(l[3]),
                            'quantity': self.positions[sym]['quantity'],
                            'bought_time': self.positions[sym]['bought_time'],
                            'sold_time': l[1]
                        }
                        self.transactions.append(transaction)
                        self.budget += self.positions[sym]['quantity'] * float(l[3])
                        del self.positions[sym]


