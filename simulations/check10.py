from re import S
import pandas as pd
import datetime as dt
import yfinance as yf
import csv

symbols = []

with open('simulations/symbols-dax.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        sym = line[0]
        symbols.append(sym)