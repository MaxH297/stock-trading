import sys

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from pytrading212 import *  # just for simplicity, not recommended, import only what you use
from pytrading212.trading212 import Trading212

from account_data import email, password

driver = webdriver.Chrome(ChromeDriverManager().install())

trading212 = Trading212(email, password, driver, mode=Mode.DEMO)

limit_order = trading212.execute_order(
    LimitOrder(
        instrument_code="AMZN_US_EQ",
        quantity=1,
        limit_price=3000.00,
        time_validity=TimeValidity.DAY,
    )
)