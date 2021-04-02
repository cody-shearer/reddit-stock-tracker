CREATE PROCEDURE `log_start`()
BEGIN
insert into 
    log(start_time) 
select 
    now();
commit;
select max(run_id) from log;
END

CREATE PROCEDURE `log_finish`(IN run_id smallint)
BEGIN
update 
    log l 
set 
    end_time = now() 
where 
    l.run_id = run_id;
commit;
END

CREATE PROCEDURE `log_error`(IN run_id smallint,IN error text)
BEGIN
insert into 
    error_log(
        run_id, 
        error, 
        error_time
        ) 
values(
    run_id, 
    error, 
    now()
    );
commit;
END