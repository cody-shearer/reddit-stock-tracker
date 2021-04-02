create table users (
    user_id nvarchar(16) primary key,
    user_name nvarchar(20),
    date_created date
    );

create table log (
    run_id smallint auto_increment primary key,
    start_time datetime,
    end_time datetime
    );

create table error_log (
    error_id smallint auto_increment primary key,
    run_id smallint,
    error text,
    error_time datetime,
    foreign key (run_id)
        references log (run_id)
            on delete cascade
);

create table posts (
    run_id smallint,
    post_id nvarchar(16),
    parent_id nvarchar(16),
    user_id nvarchar(16),
    date_created datetime,
    subreddit nvarchar(20),
    score mediumint,
    num_comments mediumint,
    primary key (run_id, post_id),
    foreign key (run_id)
        references log (run_id)
            on delete cascade,
    foreign key (user_id)
        references users (user_id)
            on delete cascade
    );

create table post_symbols (
    run_id smallint,
    post_id nvarchar(16),
    symbol nvarchar(10),
    primary key(run_id, post_id, symbol),
    foreign key (run_id, post_id)
        references posts (run_id, post_id)
            on delete cascade
    );
