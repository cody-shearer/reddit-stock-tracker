#Downloads stock list from nasdqtrader.com. Extracts tickers and dumps to tickers.json.

from ftplib import FTP
import json

class Reader:
    def __init__(self):
        self.data = ""
    def __call__(self,s):
        self.data += str(s)

ftp = FTP('ftp.nasdaqtrader.com')
ftp.login()
r = Reader()
ftp.retrbinary('RETR /SymbolDirectory/nasdaqtraded.txt', r)

data = {}
data['tickers'] = []

for stock in r.data.split('\\r\\n')[1:-2]:
    ticker = stock.split('|')[1]
    data['tickers'].append(ticker)

with open('tickers.json', 'w') as write_file:
    json.dump(data, write_file) 
