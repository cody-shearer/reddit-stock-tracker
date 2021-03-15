import praw
import pandas as pd
import numpy as np
import json
import ftplib
import re
import datetime
import sqlite3

class reddit_data:
    def __init__(self):
        self.post_data = []
        self.post_stock_data = []
        self.user_data = []
        self.user_data_pos = {}
        self.regex = re.compile('\\b(?:' + '|'.join(re.escape(str(x)) for x in tickers['tickers']) + ')\\b')

    def add_post(self, post):
        post_text = getattr(post, 'title', '') +  ' ' + getattr(post, 'selftext', '')
        found_tickers = self.regex.findall(post_text)
        if 0 < len(found_tickers) < 200:
            user_id = getattr(post, 'author_fullname', None)

            self.post_data.append([
                getattr(post, 'fullname', None), 
                getattr(post, 'parent_id', None), 
                getattr(post, 'author_fullname', None), 
                getattr(post, 'created_utc', 0), 
                getattr(subreddit, 'display_name', None),
                getattr(post, 'score', 0), 
                getattr(post, 'num_comments', 0), 
                getattr(post, 'permalink', None)
            ])

            if user_id not in self.user_data_pos:
                self.user_data_pos[user_id] = len(self.user_data)
                user = getattr(post, 'author')
                self.user_data.append([
                    user_id,
                    getattr(user, 'name', None),
                    getattr(user, 'created_utc', 0),
                    getattr(user, 'link_karma', 0),
                    getattr(user, 'comment_karma', 0)
                ])

            added_tickers = []
            for ticker in found_tickers:
                if ticker not in added_tickers:
                    added_tickers.append(ticker)
                    self.post_stock_data.append([getattr(submission, 'fullname'), ticker])

with open('pystock_data.json', 'r') as read_file:
    settings = json.load(read_file)

with open('tickers.json', 'r') as read_file:
    tickers = json.load(read_file)

reddit = praw.Reddit(client_id=settings['client_id'],
                     client_secret=settings['client_secret'],
                     user_agent=settings['user_agent'])

subreddits = ['stocks', 'investing', 'wallstreetbets', 'smallstreetbets', 'options', 'dividends', 'daytrading']

data = reddit_data()

for s in subreddits:
    subreddit = reddit.subreddit(s) 
    for submission in subreddit.top(time_filter = 'day', limit = 1):
        data.add_post(submission)
        submission.comments.replace_more()
        for comment in submission.comments.list():
            data.add_post(comment)

conn = sqlite3.connect('stonks.db')

conn.executemany('insert or replace into users \
                    (user_id, user_name, date_created, link_karma, comment_karma) \
                    values (?, ?, ?, ?, ?)', data.user_data)

conn.executemany('insert into posts \
                    (post_id, parent_id, user_id, date_created, subreddit, score, num_comments, permalink) \
                    values (?, ?, ?, ?, ?, ?, ?, ?)', data.post_data)

conn.executemany('insert into post_symbols \
                    (post_id, symbol) \
                    values (?, ?)', data.post_stock_data)

conn.commit()

print('Done')