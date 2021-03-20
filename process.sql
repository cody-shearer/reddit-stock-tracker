select
	r.symbol,
	sum(r.score) as total_score,
	r_mentions.total_mentions,
	sum(r.num_comments) as total_comments,
	count(distinct r.user_name) as unique_users
from 
	reddit_data r
inner join (
	select
		r.symbol,
		count(1) as total_mentions
	from
		reddit_data r
	group by
		r.symbol) r_mentions
on
	r.symbol = r_mentions.symbol
where
	r_mentions.total_mentions > 1
group by
	r.symbol,
	r_mentions.total_mentions
order by 
	total_score desc

