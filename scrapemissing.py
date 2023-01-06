import csv
import yfinance as yf
import pandas as pd

symbols = []
period = 7

# DAX
with open('simulations/symbols-dax.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        symbols.append(line[0])

# MDAX
with open('simulations/symbols-mdax.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        symbols.append(line[0])

symbols.append("SXR8.DE")

def write_data(filename, ticker_data):
    with open(filename, 'a+') as f2:
        writer = csv.writer(f2)
        #writer.writerow(['','Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        for index, row in ticker_data.iterrows():
            writer.writerow([
                index,
                row.Open,
                row.High,
                row.Low,
                row.Close,
                row['Adj Close'],
                row.Volume
            ])
    f2.close()
    rows = {}
    with open(filename) as f:
        reader = csv.reader(f)
        for line in reader:
            rows[line[0]] = line
    with open(filename, 'w') as t:
        writer = csv.writer(t)
        for i in rows:
            writer.writerow(rows[i])

for sym in symbols:
    ticker_data = yf.download(tickers=sym, period=str(7 if period > 7 else period) + "d", interval='1m')
    write_data('simulations/ticker_data/1m/'+sym+'.csv', ticker_data)
    ticker_data = yf.download(tickers=sym, period=str(period)+"d", interval='5m')
    write_data('simulations/ticker_data/5m/'+sym+'.csv', ticker_data)

