
select RESORT,
"-01/11" "OCT",
"-01/12" - "-01/11" "NOV",
"-01/01" - "-01/12" "DEC",
"-01/02" - "-01/01" "JAN",
"-01/03" - "-01/02" "FEB",
"-01/04" - "-01/03" "MAR",
"-01/05" - "-01/04" "APR",
"-01/06" - "-01/05" "MAY",
"-01/07" - "-01/06" "JUN",
"-01/08" - "-01/07" "JUL",
"-01/09" - "-01/08" "AUG"
from (
Select RESORT
,SUM(case when the_date = TO_DATE('01112024','DDMMYYYY') then paxrooms else 0 end ) "-01/11"
,SUM(case when the_date = TO_DATE('01122024','DDMMYYYY') then paxrooms else 0 end ) "-01/12"
,SUM(case when the_date = TO_DATE('01012025','DDMMYYYY') then paxrooms else 0 end ) "-01/01"
,SUM(case when the_date = TO_DATE('01022025','DDMMYYYY') then paxrooms else 0 end ) "-01/02"
,SUM(case when the_date = TO_DATE('01032025','DDMMYYYY') then paxrooms else 0 end ) "-01/03"
,SUM(case when the_date = TO_DATE('01042025','DDMMYYYY') then paxrooms else 0 end ) "-01/04"
,SUM(case when the_date = TO_DATE('01052025','DDMMYYYY') then paxrooms else 0 end ) "-01/05"
,SUM(case when the_date = TO_DATE('01062025','DDMMYYYY') then paxrooms else 0 end ) "-01/06"
,SUM(case when the_date = TO_DATE('01072025','DDMMYYYY') then paxrooms else 0 end ) "-01/07"
,SUM(case when the_date = TO_DATE('01082025','DDMMYYYY') then paxrooms else 0 end ) "-01/08"
,SUM(case when the_date = TO_DATE('01092025','DDMMYYYY') then paxrooms else 0 end ) "-01/09"
,SUM(case when the_date = TO_DATE('01102025','DDMMYYYY') then paxrooms else 0 end ) "-01/10"
from(SELECT e.resort 
, e.ISSUE_DATE the_date
, SUM(e.pax) paxrooms
 FROM train.ALB_OCCUPANCY_RATE_JURNAL e 
 WHERE e.ISSUE_DATE in ( 
  TO_DATE('01112024','DDMMYYYY') 
, TO_DATE('01122024','DDMMYYYY') 
, TO_DATE('01012025','DDMMYYYY') 
, TO_DATE('01022025','DDMMYYYY') 
, TO_DATE('01032025','DDMMYYYY') 
, TO_DATE('01042025','DDMMYYYY') 
, TO_DATE('01052025','DDMMYYYY') 
, TO_DATE('01062025','DDMMYYYY') 
, TO_DATE('01072025','DDMMYYYY') 
, TO_DATE('01082025','DDMMYYYY') 
, TO_DATE('01092025','DDMMYYYY') 
, TO_DATE('01102025','DDMMYYYY') 

 )
 AND  e.reservation_date  between TO_DATE('01032025','DDMMYYYY') and TO_DATE('30112025','DDMMYYYY')
 AND E.RESORT IN ('GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'MAG', 'SUP', 'RAL', 'VIT', 'KPS', 'VMG', 'GOR', 'ARA')
group by  e.resort, e.ISSUE_DATE
 ) occ 
group by RESORT
) x
ORDER BY RESORT
;