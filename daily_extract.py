import json
import praw
import re
import time
import datetime
import mysql.connector
from ftplib import FTP
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

class Reader:
    def __init__(self):
        self.data = ""
    def __call__(self,s):
        self.data += str(s)

class subreddit_data:
    def __init__(self, sub, users, run_id, cursor):
        self.post_data = []
        self.post_stock_data = []
        self.user_data = []
        self.tickers = []
        self.subreddit_name = sub
        self.cursor = cursor
        self.get_tickers()
        self.run_id = run_id
        self.regex = re.compile('\\b(?:' + '|'.join(re.escape(str(ticker)) for ticker in self.tickers) + ')\\b')
    
        if users == []:
            self.cursor.execute('select user_id from users')
            self.unique_users = self.cursor.fetchall()
            self.unique_users = [user[0] for user in self.unique_users]
        else:
            self.unique_users = users

    
    def get_tickers(self):
        ftp = FTP('ftp.nasdaqtrader.com')
        ftp.login()
        r = Reader()
        ftp.retrbinary('RETR /SymbolDirectory/nasdaqtraded.txt', r)
        columns = {}

        excluded_tickers = ['TRUE', 'YOLO', 'Y', 'X', 'WORK', 'WELL', 'WANT', 'W', 'VERY', 'V', 'USD', 'USA', 'U', 'TWO', 'TRIP', 'TELL', 'T', 'STAY', 'SO', 'SNOW', 'SNAP', 'SIX', 'SEE', 'SAVE', 'RUN', 'RIDE', 'REAL', 'RE', 'R', 'PLUS', 'PICK', 'OUT', 'OR', 'OPEN', 'ONE', 'ON', 'OLD', 'O', 'NYC', 'NOW', 'NEXT', 'NEW', 'MUST', 'MOON', 'MARK', 'MAN', 'M', 'LOW', 'LOVE', 'LIVE', 'LIFE', 'LEAP', 'JUST', 'J', 'IT', 'IMO', 'ICE', 'HUGE', 'HOLD', 'HEAR', 'HE', 'HD', 'HAS', 'H', 'GOOD', 'GO', 'GDP', 'G', 'FOR', 'FAST', 'F', 'EVER', 'EOD', 'EDIT', 'EAT', 'E', 'DEEP', 'DD', 'D', 'CPI', 'CFO', 'CEO', 'CAT', 'CASH', 'CAN', 'C', 'BIG', 'BEST', 'BE', 'B', 'AT', 'ARE', 'ANY', 'AN', 'ALL', 'A', ]

        for column in r.data.split('\\r\\n')[0].lower().split('|'):
            columns[column] = len(columns)

        for stock in r.data.split('\\r\\n')[1:-2]:
            stock_data = stock.split('|')
            if stock_data[columns['etf']] == 'N' and stock_data[columns['test issue']] == 'N':
                ticker = stock_data[columns['symbol']]
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
                parent_id = getattr(post, 'parent_id', None)

                if parent_id is not None: #only comments have a parent_id
                    num_comments = len(getattr(getattr(post, 'replies', None), '_comments', 0))
                else:
                    num_comments = len(getattr(getattr(post, 'comments', None), '_comments', 0))

                self.post_data.append([
                    self.run_id,
                    post_id,
                    parent_id,
                    getattr(post, 'author_fullname', None),
                    datetime.datetime.fromtimestamp(getattr(post, 'created_utc', None)).strftime('%Y-%m-%d %H:%M:%S'),
                    self.subreddit_name,
                    int(getattr(post, 'score', 0)),
                    num_comments
                    ])

                if user_id not in self.unique_users:
                    self.unique_users.append(user_id)
                    user = getattr(post, 'author')

                    self.user_data.append([
                        user_id,
                        getattr(user, 'name', None),
                        datetime.datetime.fromtimestamp(getattr(user, 'created_utc', None)).strftime('%Y-%m-%d %H:%M:%S'),
                    ])

                for ticker in found_tickers:
                   self.post_stock_data.append([
                        self.run_id,
                        post_id, 
                        ticker
                    ])
    
    def upload_data(self):
        try:
            self.cursor.executemany('insert into users \
                                (user_id, user_name, date_created) \
                                values (%s, %s, %s)'
                                , self.user_data
                                )

            self.cursor.execute('commit')

            self.cursor.executemany('insert into posts \
                                (run_id, post_id, parent_id, user_id, date_created, subreddit, score, num_comments) \
                                values (%s, %s, %s, %s, %s, %s, %s, %s)', 
                                self.post_data
                                )

            self.cursor.execute('commit')

            self.cursor.executemany('insert into post_symbols \
                                (run_id, post_id, symbol) \
                                values (%s, %s, %s)', 
                                self.post_stock_data
                                )

            self.cursor.execute('commit')
        except Exception as e: 
            self.cursor.callproc('log_error', [run_id, e])
            raise

with open(dir_path + '/config.json', 'r') as read_file:
    settings = json.load(read_file)

conn = mysql.connector.connect(
    host = settings['sql_host'],
    user = settings['sql_user'],
    password = settings['sql_pwd'],
    database = settings['sql_db']
)

cursor = conn.cursor()
cursor.callproc('log_start')
for result in cursor.stored_results():
    run_id = result.fetchone()[0]

reddit = praw.Reddit(client_id=settings['client_id'],
                     client_secret=settings['client_secret'],
                     user_agent=settings['user_agent']
                     )

subreddits = ['stocks', 'investing', 'smallstreetbets', 'daytrading', 'options', 'wallstreetbets']
users = []

for sub in subreddits:
    timer = time.perf_counter()
    subreddit = reddit.subreddit(sub)
    data = subreddit_data(sub, users, run_id, cursor)
    for submission in subreddit.top(time_filter = 'day'):
        data.add_post(submission)
        submission.comments.replace_more(limit=500)
        for comment in submission.comments.list():
            data.add_post(comment)
    data.upload_data()
    users = data.unique_users
    print('Finished data collection for r/' + sub + ' in ' + str(round(time.perf_counter() - timer)) + ' seconds.')

cursor.callproc('process_daily_data', [run_id])
cursor.callproc('log_finish', [run_id])
