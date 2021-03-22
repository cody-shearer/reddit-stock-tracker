import json
import praw
import re
import sqlite3
import time
import datetime
from ftplib import FTP

class Reader:
    def __init__(self):
        self.data = ""
    def __call__(self,s):
        self.data += str(s)

class reddit_data:
    def __init__(self, sub, users):
        self.post_data = []
        self.post_stock_data = []
        self.user_data = []
        self.tickers = []
        self.subreddit_name = sub
        self.conn = sqlite3.connect('stonks.db')
        self.get_tickers()
        self.regex = re.compile('\\b(?:' + '|'.join(re.escape(str(ticker)) for ticker in self.tickers) + ')\\b')
    
        if users == []:
            cur = self.conn.cursor()
            cur.execute('select user_id from users')
            self.unique_users = cur.fetchall()
            self.unique_users = [user[0] for user in self.unique_users]
        else:
            self.unique_users = users

    
    def get_tickers(self):
        ftp = FTP('ftp.nasdaqtrader.com')
        ftp.login()
        r = Reader()
        ftp.retrbinary('RETR /SymbolDirectory/nasdaqtraded.txt', r)

        excluded_tickers = ['TRUE', 'YOLO', 'Y', 'X', 'WORK', 'WELL', 'WANT', 'W', 'VERY', 'V', 'USD', 'USA', 'U', 'TWO', 'TRIP', 'TELL', 'T', 'STAY', 'SO', 'SNOW', 'SNAP', 'SIX', 'SEE', 'SAVE', 'RUN', 'RIDE', 'REAL', 'RE', 'R', 'PLUS', 'PICK', 'OUT', 'OR', 'OPEN', 'ONE', 'ON', 'OLD', 'O', 'NYC', 'NOW', 'NEXT', 'NEW', 'MUST', 'MOON', 'MARK', 'MAN', 'M', 'LOW', 'LOVE', 'LIVE', 'LIFE', 'LEAP', 'JUST', 'J', 'IT', 'IMO', 'ICE', 'HUGE', 'HOLD', 'HEAR', 'HE', 'HD', 'HAS', 'H', 'GOOD', 'GO', 'GDP', 'G', 'FOR', 'FAST', 'F', 'EVER', 'EOD', 'EDIT', 'EAT', 'E', 'DEEP', 'DD', 'D', 'CPI', 'CFO', 'CEO', 'CAT', 'CASH', 'CAN', 'C', 'BIG', 'BEST', 'BE', 'B', 'AT', 'ARE', 'ANY', 'AN', 'ALL', 'A', ]

        for stock in r.data.split('\\r\\n')[1:-2]:
            ticker = stock.split('|')[1]
            if ticker not in excluded_tickers:
                self.tickers.append(ticker)

    def add_post(self, post):
        post_text = getattr(post, 'title', '') +  ' ' + getattr(post, 'selftext', '') + ' ' + getattr(post, 'body', '')
        found_tickers = self.regex.findall(post_text)
        found_tickers = list(dict.fromkeys(found_tickers))
        if 0 < len(found_tickers):
            user_id = getattr(post, 'author_fullname', None)
            post_id = getattr(post, 'fullname')

            if user_id != None:
                self.post_data.append([
                    post_id, 
                    getattr(post, 'parent_id', None), 
                    getattr(post, 'author_fullname', None), 
                    getattr(post, 'created_utc', None), 
                    self.subreddit_name,
                    getattr(post, 'score', 0), 
                    getattr(post, 'num_comments', 0), 
                    getattr(post, 'permalink', None)
                ])

                if user_id not in self.unique_users:
                    self.unique_users.append(user_id)
                    user = getattr(post, 'author')

                    self.user_data.append([
                        user_id,
                        getattr(user, 'name', None),
                        getattr(user, 'created_utc', 0)
                    ])

                for ticker in found_tickers:
                   self.post_stock_data.append([post_id, ticker])
    
    def upload_data(self):
        self.conn.executemany('insert into users \
                            (user_id, user_name, date_created) \
                            values (?, ?, ?)', self.user_data)

        self.conn.executemany('insert or replace into posts \
                            (post_id, parent_id, user_id, date_created, subreddit, score, num_comments, permalink) \
                            values (?, ?, ?, ?, ?, ?, ?, ?)', self.post_data)

        self.conn.executemany('insert or ignore into post_symbols \
                            (post_id, symbol) \
                            values (?, ?)', self.post_stock_data)
        
        self.conn.commit()

with open('config.json', 'r') as read_file:
    settings = json.load(read_file)

reddit = praw.Reddit(client_id=settings['client_id'],
                     client_secret=settings['client_secret'],
                     user_agent=settings['user_agent'])

subreddits = ['stocks', 'investing', 'smallstreetbets', 'daytrading', 'options', 'wallstreetbets']
users = []

for sub in subreddits:
    timer = time.perf_counter()
    subreddit = reddit.subreddit(sub)
    data = reddit_data(sub, users)
    for submission in subreddit.top(time_filter = 'day',limit=1):
        data.add_post(submission)
        submission.comments.replace_more()
        for comment in submission.comments.list():
            data.add_post(comment)
    data.upload_data()
    users = data.unique_users
    print('Finished data collection for r/' + sub + ' in ' + str(round(time.perf_counter() - timer)) + ' seconds.')

conn = sqlite3.connect('stonks.db')
conn.execute('insert into log (finish_time) values (?)', str(datetime.datetime.now().strftime('%Y-%M-%d %H:%m'))) 
conn.commit()
