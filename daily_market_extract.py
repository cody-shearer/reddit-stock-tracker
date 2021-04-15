import json
import praw
import re
import sqlite3
import time
import datetime
import mysql.connector
from ftplib import FTP
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

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

cursor.callproc('process_daily_data')
cursor.callproc('log_finish', [run_id])
