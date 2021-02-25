import praw
import pandas as pd
import numpy as np
import json
import ftplib
import re
import datetime

# Acessing the reddit api
with open('pystock_data.json', 'r') as read_file:
    settings = json.load(read_file)

with open('tickers.json', 'r') as read_file:
    tickers = json.load(read_file)

regex = re.compile('\\b(?:' + '|'.join(re.escape(str(x)) for x in tickers['tickers']) + ')\\b')

reddit = praw.Reddit(client_id=settings['client_id'],#my client id
                     client_secret=settings['client_secret'],  #your client secret
                     user_agent=settings['user_agent'])

subreddits = ['stocks', 'investing', 'wallstreetbets', 'smallstreetbets', 'options', 'dividends', 'daytrading']

arr_data = [ticker for ticker in tickers['tickers']]
s = pd.Series(arr_data)
df_index = pd.Index(s)
data = pd.DataFrame(index = s) 

data['Total Mentions'] = 0 
data['Score Weighted Mentions'] = 0 
data['Unique Mentions'] = 0 
data['Unique Users'] = '' 

for s in subreddits:
    subreddit = reddit.subreddit(s)   # Chosing the subreddit

    for submission in subreddit.top(time_filter = 'day'):        
        found_tickers = regex.findall(submission.title + ' ' + submission.selftext )
        if 0 < len(found_tickers) < 200:
            for ticker in found_tickers:
                data.at[ticker, 'Total Mentions'] += 1
                data.at[ticker, 'Score Weighted Mentions'] += submission.score
                if submission.author.name not in data.at[ticker, 'Unique Users']:
                    data.at[ticker, 'Unique Users'] += submission.author.name + '|'
                    data.at[ticker, 'Unique Mentions'] += 1

        ##### Acessing comments on the post
        submission.comments.replace_more()
        for comment in submission.comments.list():
            found_tickers = regex.findall(comment.body)
            if 0 < len(found_tickers) < 200:
                for ticker in found_tickers:
                    data.at[ticker, 'Total Mentions'] += 1
                    data.at[ticker, 'Score Weighted Mentions'] += comment.score
                    if comment.author.name not in data.at[ticker, 'Unique Users']:
                        data.at[ticker, 'Unique Users'] += comment.author.name + '|'
                        data.at[ticker, 'Unique Mentions'] += 1
    
data.to_csv('subreddit_stock_data' + datetime.date.today() + '.csv')
