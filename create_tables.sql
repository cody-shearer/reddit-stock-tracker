-- SQLite
create table daily_report (
    symbol TEXT,
    date REAL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    mentions INTEGER,
    sentiment_score REAL,
    PRIMARY KEY (symbol, date)
    ) WITHOUT ROWID ;

create table users (
    user_id TEXT PRIMARY KEY,
    user_name TEXT,
    date_created REAL,
    link_karma INTEGER,
    comment_karma INTEGER
    ) WITHOUT ROWID ;

create table posts (
    post_id TEXT PRIMARY KEY,
    parent_id TEXT,
    user_id TEXT,
    date_created REAL,
    subreddit TEXT,
    score REAL,
    num_comments INTEGER,
    permalink TEXT,
    FOREIGN KEY (user_id)
        REFERENCES users (user_id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    ) WITHOUT ROWID;

create table post_symbols (
    post_id TEXT,
    symbol TEXT,
    PRIMARY KEY(post_id, symbol),
    FOREIGN KEY (post_id)
        REFERENCES posts (post_id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    ) WITHOUT ROWID;