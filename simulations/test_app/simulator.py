import pandas as pd
import datetime as dt
import yfinance as yf

class Simulator(object):

    def __init__(self, symbols, budget, trade_budget, buy_in, sell, stop, positions={}, dax_limit=0, detail_1m=False, three=False):
        self.symbols = symbols
        self.budget  = budget
        self.trade_budget = trade_budget
        self.buy_in = buy_in
        self.sell = sell
        self.stop = stop
        self.positions = positions
        self.transactions = []
        self.dax_limit = dax_limit
        self.sell_remaining = True
        self.detail_1m = detail_1m
        self.hist = self.load_stock_values()
        self.three = three

    def run_test(self, period=60):
        period_string = str(period+1)+'d'
        self.dax_hist = yf.Ticker("^GDAXI").history(period=period_string)

        j = 0
        for index, row in self.dax_hist.iterrows():
            date = pd.to_datetime(index)
            date = date.replace(hour=9)
            self.trade_values = {}
            print(date.strftime("%Y-%m-%d") + "DAX - Performance: " + str(self.dax_hist.Close[j] - self.dax_hist.Open[j]) + " ")
            print(self.get_portfolio_value())
            if j > 0 and self.dax_hist.Close[j - 1] > self.dax_hist.Open[j - 1] * self.dax_limit:
                interv1 = self.get_interval_1m(date)
                if self.three:
                    self.trade_budget = (self.budget)/3
                for p in range(510 if interv1 else 102):
                    datetime = date + dt.timedelta(seconds=(60 if interv1 else 300)*p)
                    for sym in self.symbols:
                        time_string = datetime.strftime("%Y-%m-%d %H:%M:%S")+self.get_offset(date)
                        df = self.hist[sym]['1m' if interv1 else '5m']
                        if time_string in df.index:
                            stock_data = df.loc[time_string]
                            if sym not in self.trade_values:
                                self.trade_values[sym] = {
                                    'High': stock_data.High,
                                    'Low': stock_data.Low
                                }
                            else:
                                self.trade_values[sym]['High'] = max(stock_data.High, self.trade_values[sym]['High'])
                                self.trade_values[sym]['Low'] = min(stock_data.Low, self.trade_values[sym]['Low'])
                            # Buying?
                            if (sym not in self.positions) and (self.trade_values[sym]['High'] * self.buy_in > stock_data.Low) and self.trade_values[sym]['High'] * self.buy_in < stock_data.Open:
                                if self.budget >= self.trade_budget and p<(508 if interv1 else 101):
                                    print('Buying: ' + sym + ' for ' + str(round(self.trade_values[sym]['High'] * self.buy_in, 2)))
                                    self.positions[sym] = {
                                        'buy_price': self.trade_values[sym]['High'] * self.buy_in,
                                        'sell_price': self.trade_values[sym]['High'] * self.sell,
                                        'stop': self.trade_values[sym]['High'] * self.stop,
                                        'quantity': self.trade_budget / (self.trade_values[sym]['High'] * self.buy_in),
                                        'value': self.trade_budget,
                                        'bought_time': time_string
                                    }
                                    self.budget -= self.trade_budget
                                #else:
                                #    print("Not enough budget...")
                            # If in portfolio
                            if sym in self.positions:
                                self.positions[sym]['value'] = self.positions[sym]['quantity'] * stock_data.Close
                                # Selling?
                                if(stock_data.High > self.positions[sym]['sell_price']):
                                    self.sell_position(sym, self.positions[sym]['sell_price'], time_string)
                                elif(stock_data.Low < self.positions[sym]['stop']):
                                    self.sell_position(sym, self.positions[sym]['stop'], time_string)
                                elif p>=(508 if interv1 else 101):
                                    self.sell_position(sym, stock_data.Close, time_string)
                        #else:
                            #print('missing: ' + sym + ' ' + time_string)
            j += 1
            self.empty_portfolio()
        if self.sell_remaining:
            self.empty_portfolio()

    def get_offset(self, date):
        return "+01:00" if pd.to_datetime(dt.date(2022,3,27)) >= date.tz_localize(None) else "+02:00"

    def load_stock_values(self):
        hist = {}
        for sym in self.symbols:
            hist[sym] = {}
            hist[sym]['1m'] = pd.read_csv('./simulations/ticker_data/1m/' + sym + '.csv', index_col=0)
            hist[sym]['5m'] = pd.read_csv('./simulations/ticker_data/5m/' + sym + '.csv', index_col=0)
        return hist

    def sell_position(self, sym, price, datetime, delete=True):
        print('Selling: ' + sym + ' for ' + str(round(price, 2)))
        self.budget += self.positions[sym]['quantity'] * price
        transaction = {
            'symbol': sym,
            'buy_price': self.positions[sym]['buy_price'],
            'sell_price': price,
            'quantity': self.positions[sym]['quantity'],
            'bought_time': self.positions[sym]['bought_time'],
            'sold_time': datetime
        }
        self.transactions.append(transaction)
        if delete:
            del self.positions[sym]

    def empty_portfolio(self):
        for sym in self.positions:
            pos = self.positions[sym]
            self.sell_position(sym, pos['value']/pos['quantity'], 'Final', False)
        self.positions = {}

    def get_portfolio_value(self):
        value = self.budget
        for i in self.positions:
            value += self.positions[i]['value']
        return value

    def get_interval_1m(self, date):
        missing = ["2022-04-05"]
        interv = self.detail_1m and pd.to_datetime(dt.date(2022,3,3)) <= date.tz_localize(None) and date.strftime("%Y-%m-%d") not in missing
        return interv
