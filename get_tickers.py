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

excluded_tickers = ['TRUE', 'YOLO', 'Y', 'X', 'WORK', 'WELL', 'WANT', 'W', 'VERY', 'V', 'USD', 'USA', 'U', 'TWO', 'TRIP', 'TELL', 'T', 'STAY', 'SO', 'SNOW', 'SNAP', 'SIX', 'SEE', 'SAVE', 'RUN', 'RIDE', 'REAL', 'RE', 'R', 'PLUS', 'PICK', 'OUT', 'OR', 'OPEN', 'ONE', 'ON', 'OLD', 'O', 'NYC', 'NOW', 'NEXT', 'NEW', 'MUST', 'MOON', 'MARK', 'MAN', 'M', 'LOW', 'LOVE', 'LIVE', 'LIFE', 'LEAP', 'JUST', 'J', 'IT', 'IMO', 'ICE', 'HUGE', 'HOLD', 'HEAR', 'HE', 'HD', 'HAS', 'H', 'GOOD', 'GO', 'GDP', 'G', 'FOR', 'FAST', 'F', 'EVER', 'EOD', 'EDIT', 'EAT', 'E', 'DEEP', 'DD', 'D', 'CPI', 'CFO', 'CEO', 'CAT', 'CASH', 'CAN', 'C', 'BIG', 'BEST', 'BE', 'B', 'AT', 'ARE', 'ANY', 'AN', 'ALL', 'A', ]

for stock in r.data.split('\\r\\n')[1:-2]:
    ticker = stock.split('|')[1]
    if ticker not in excluded_tickers:
        data['tickers'].append(ticker)

with open('tickers.json', 'w') as write_file:
    json.dump(data, write_file) 
