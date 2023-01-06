import csv
import pandas as pd

symbols = []

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

for sym in symbols:
    with open('simulations/ticker_data/'+sym+'.csv', 'a+') as f2:
        writer = csv.writer(f2)
        writer.writerow(['','Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        df1 = pd.read_csv('./simulations/ticker_data-backup/'+sym+'.csv', index_col=0)
        df2 = pd.read_csv('./simulations/ticker_data-backup/last_week/'+sym+'.csv', index_col=0)
        for i in df1.index:
            if i not in df2.index:
                x = df1.loc[i]
                writer.writerow([i, x.Open, x.High, x.Low, x.Close, x['Adj Close'], x.Volume])
        for i in df2.index:
            writer.writerow([i, x.Open, x.High, x.Low, x.Close, x['Adj Close'], x.Volume])
    f2.close()

