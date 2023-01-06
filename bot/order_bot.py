from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from pytrading212 import *  
from pytrading212.trading212 import Trading212

from account_data import email, password

abbr = {
    'DHER.DE': 'DHER_US_EQ'
}

class OrderBot(object):
    def __init__(self, demo=True):
        print('order bot ready!')
        self.mode = Mode.DEMO if demo else Mode.LIVE

    def limit_order(self, sym, quantity, limit_price):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        trading212 = Trading212(email, password, self.driver, mode=self.mode)
        limit_order = trading212.execute_order(
            LimitOrder(
                instrument_code=self.get_instrument_code_d(sym),
                quantity=round(quantity, 2),
                limit_price=round(limit_price, 2),
                time_validity=TimeValidity.DAY,
            )
        )
        #trading212.close()
        if('code' in limit_order and limit_order['code'] == 'BusinessException' and limit_order['context']['type'] == 'WrongPriceIncrementation'):
            incr = limit_order['context']['priceIncrementation']
            limit_price = round(limit_price/incr, 0) * incr
            limit_order = trading212.execute_order(
                LimitOrder(
                    instrument_code=self.get_instrument_code_d(sym),
                    quantity=round(quantity, 2),
                    limit_price=round(limit_price, 2),
                    time_validity=TimeValidity.DAY,
                )
            )
        print(limit_order)

    def sell_limit(self, sym, quantity, limit_price):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        trading212 = Trading212(email, password, self.driver, mode=self.mode)
        sell_limit = trading212.execute_order(
            LimitOrder(
                instrument_code=self.get_instrument_code_d(sym),
                quantity=round(quantity, 2) * -1.0,
                limit_price=round(limit_price, 2),
                time_validity=TimeValidity.GOOD_TILL_CANCEL,
            )
        )
        if('code' in sell_limit and sell_limit['code'] == 'BusinessException' and sell_limit['context']['type'] == 'WrongPriceIncrementation'):
            incr = sell_limit['context']['priceIncrementation']
            limit_price = round(limit_price/incr, 0) * incr
            sell_limit = trading212.execute_order(
                LimitOrder(
                    instrument_code=self.get_instrument_code_d(sym),
                    quantity=round(quantity, 2),
                    limit_price=round(limit_price, 2),
                    time_validity=TimeValidity.DAY,
                )
            )
        #trading212.close()
        print(sell_limit)

    def get_instrument_code_d(self, sym):
        if sym in abbr:
            return abbr[sym]
        return sym.removesuffix('.DE') + 'd_EQ'

