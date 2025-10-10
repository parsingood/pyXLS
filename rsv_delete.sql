select n.name_id, n.last, n.first, s.* 
from RESERVATION_STAT_DAILY s
left join name n on n.name_id = s.name_id
where s.RESORT = 'MRA'
and s.BUSINESS_DATE = to_date('10082024','ddmmyy')
and s.SOURCE_PROF_ID = 8830354
and s.TRUNC_BEGIN_DATE=to_date('08082024','ddmmyy')
--and not exists (select 1 from name n where n.name_id = s.name_id)

--Select company from name where name_id = '8830354'
;

select * from RESERVATION_DAILY_ELEMENT_NAME
where RESV_NAME_ID = 12760415

;

select  en.RESV_NAME_ID, n.name_id, n.last, n.first, s.* 
from RESERVATION_STAT_DAILY s
left join RESERVATION_DAILY_ELEMENT_NAME en on en.RESV_NAME_ID = s.RESV_NAME_ID
and en.resort = s.resort
left join name n on n.name_id = s.name_id
where s.RESORT = 'MRA'
and s.BUSINESS_DATE between to_date('08082024','ddmmyy') and  to_date('10082024','ddmmyy') -- = to_date('10082024','ddmmyy')
and s.SOURCE_PROF_ID = 8830354
and s.TRUNC_BEGIN_DATE between to_date('08082024','ddmmyy') and  to_date('10082024','ddmmyy')
--and not exists (select 1 from name n where n.name_id = s.name_id)
and en.RESV_NAME_ID is null
and resv_status <> 'NO SHOW'

--Select company from name where name_id = '8830354'
;


13665497
13665498
13665500
13665509
;



select  en.RESV_NAME_ID, n.name_id, n.last, n.first, s.* 
from RESERVATION_STAT_DAILY s
left join RESERVATION_DAILY_ELEMENT_NAME en on en.RESV_NAME_ID = s.RESV_NAME_ID
and en.resort = s.resort
left join name n on n.name_id = s.name_id
where s.RESORT = 'MRA'
and s.BUSINESS_DATE between to_date('08082024','ddmmyy') and  to_date('10082024','ddmmyy') -- = to_date('10082024','ddmmyy')
and s.SOURCE_PROF_ID = 8830354
and s.TRUNC_BEGIN_DATE between to_date('08082024','ddmmyy') and  to_date('10082024','ddmmyy')
--and not exists (select 1 from name n where n.name_id = s.name_id)
and en.RESV_NAME_ID is null
and resv_status <> 'NO SHOW'

--Select company from name where name_id = '8830354'
;

delete from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('08082024','ddmmyy') and  to_date('10082024','ddmmyy')
and NAME_ID in (13665497,13665498,13665500,13665509)

;
select * from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('07082024','ddmmyy') and  to_date('12082024','ddmmyy')
and NAME_ID in (13665497,13665498,13665500,13665509)

;
commit
;

select * from name
where NAME_ID in (13665497,13665498,13665500,13665509)
;
delete from NAME$OWNER
where NAME_ID in (13665497,13665498,13665500,13665509)
;
delete from name
where NAME_ID in (13665497,13665498,13665500,13665509)
;
delete from FINANCIAL_TRANSACTIONS_JRNL
where NAME_ID in (13665497,13665498,13665500,13665509)
;
delete from NAME_DOCUMENTS
where NAME_ID in (13665497,13665498,13665500,13665509)
;
commit

;
select *  from NAME_DOCUMENTS
where NAME_ID in (13665497,13665498,13665500,13665509)
;
select * from FINANCIAL_TRANSACTIONS_JRNL
where NAME_ID in (13665497,13665498,13665500,13665509)
;
select * from NAME$OWNER
where NAME_ID in (13665497,13665498,13665500,13665509)
;
SELECT 
    a.table_name,
    a.column_name
FROM 
    all_cons_columns a
JOIN 
    all_constraints c 
    ON a.constraint_name = c.constraint_name
WHERE 
    c.constraint_type = 'R'
    AND c.constraint_name = 'NAME_DOCUMENT_NAME_FK';

;
delete
from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('01052024','ddmmyy') and  to_date('31082024','ddmmyy')
and NAME_ID in (
select NAME_ID from name
where last = 'KIROV'
and first='RUMEN'

)
;
select *
from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('01052024','ddmmyy') and  to_date('31082024','ddmmyy')
and NAME_ID in (
select NAME_ID from name
where last = 'KIROV'
and first='RUMEN'

)
;
select *
from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('01052023','ddmmyy') and  to_date('31082023','ddmmyy')
and NAME_ID in (
select NAME_ID from name
where last = 'KIROV'
and first='RUMEN'

)
;
select *
from RESERVATION_STAT_DAILY
where RESORT = 'MRA'
and BUSINESS_DATE between to_date('01052024','ddmmyy') and  to_date('31082024','ddmmyy')
and NAME_ID in (
select NAME_ID from name
where last = 'KIROVA'
and first='DETELINA'

)
