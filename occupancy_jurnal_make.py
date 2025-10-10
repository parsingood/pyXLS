
import datetime 
import cx_Oracle

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') # if needed, place an 'r' before any parameter in 

today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")

# Свързване към базата данни
connection = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
cursor = connection.cursor()
# PL/SQL кодът

plsql_block="""
  INSERT
        INTO TRAIN.ALB_OCCUPANCY_RATE_JURNAL ( ISSUE_DATE,RESORT,ROOM_CLASS,SOURCE_ID,TRAVEL_AGENT_ID,RESERVATION_DATE,MARKET,ROOMS,PAX, EURO, RATE_CODE ) 
        SELECT TRUNC( CURRENT_DATE, 'DD')     ISSUE_DATE
              ,RESORT,ROOM_CLASS,SOURCE_ID,TRAVEL_AGENT_ID,RESERVATION_DATE
              ,NVL(MAX(S.UDFC22),'XXX') MARKET
              ,SUM(ROOMS) ROOMS,SUM(PAX) PAX, SUM(EURO) EURO 
		  ,NVL(RATE_CODE,'X') RATE_CODE
        FROM 
        (
          SELECT 
             E.RESORT RESORT
           , T.ROOM_CLASS ROOM_CLASS
           , NVL(MAX(EN.SOURCE_ID),0) SOURCE_ID
           , NVL(MAX(EN.TRAVEL_AGENT_ID),0) TRAVEL_AGENT_ID
           , E.RESERVATION_DATE  RESERVATION_DATE   
           , MAX(E.PHYSICAL_QUANTITY) ROOMS    
           , SUM(EN.ADULTS+EN.CHILDREN) PAX
           , SUM(case when EN.CURRENCY_CODE='BGN' THEN EN.share_amount/1.95583 
                    when EN.CURRENCY_CODE='GBP' THEN EN.share_amount * 2.2 /1.99583 
                    ELSE EN.share_amount END
                ) EURO
	     , MAX(EN.RATE_CODE) RATE_CODE
          FROM OPERA.RESERVATION_DAILY_ELEMENT_NAME EN 
          JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT=EN.RESORT AND E.RESERVATION_DATE=EN.RESERVATION_DATE AND E.RESV_DAILY_EL_SEQ=EN.RESV_DAILY_EL_SEQ
          JOIN OPERA.RESERVATION_NAME R ON R.RESORT=EN.RESORT AND R.RESV_NAME_ID = EN.RESV_NAME_ID
          JOIN OPERA.RESORT RS ON RS.RESORT = EN.RESORT
          JOIN OPERA.RESORT$_ROOM_CATEGORY T ON T.RESORT = EN.RESORT AND T.ROOM_CATEGORY = E.ROOM_CATEGORY
          WHERE T.ROOM_CLASS <> 'P'
            AND NVL(E.DUE_OUT_YN,'N')='N'
            AND E.RESERVATION_DATE BETWEEN TO_DATE('01012025' ,'DDMMYYYY')  AND TO_DATE('30112025' ,'DDMMYYYY')  
            AND RS.STATE in (
			'ALB','WLA','PRI'
--			,'ANZ'
		)            
		AND E.RESV_STATUS NOT IN ('CANCELLED','WAITLIST','NO SHOW')
            AND NVL(R.UDFD15,E.INSERT_DATE) <= TRUNC( CURRENT_DATE, 'DD')    
          GROUP BY  E.RESORT,T.ROOM_CLASS,E.RESERVATION_DATE, E.RESV_DAILY_EL_SEQ
        ) X
        LEFT JOIN OPERA.NAME S ON S.NAME_ID = X.SOURCE_ID
        GROUP BY RESORT,ROOM_CLASS,SOURCE_ID,TRAVEL_AGENT_ID,RESERVATION_DATE, RATE_CODE
;
COMMIT
;    
 INSERT
    INTO TRAIN.ALB_TRENDS
      (
        ISSUE_DATE,
        SOURCE_ID,
        RESORT,
        RESERVATION_DATE,
        NEW_OVNTS,
        NEW_AMOUNT
      )
     SELECT current_date, SOURCE_ID, J.RESORT,RESERVATION_DATE,
        SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date,'DD')  THEN PAX ELSE 0 END)
        - SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date-1,'DD')  THEN PAX ELSE 0 END) OVNTS
      , ROUND(SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date,'DD')  THEN EURO ELSE 0 END)
        - SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date-1,'DD')  THEN EURO ELSE 0 END),2) AMOUNT_EURO
      FROM TRAIN.ALB_OCCUPANCY_RATE_JURNAL J
      join OPERA.RESORT R ON J.RESORT=R.RESORT
      WHERE ISSUE_DATE between current_date - 2 and current_date
      AND j.reservation_date > TO_DATE('01.01.2025','DD.MM.YYYY')
      AND R.STATE='ALB'
      group by 
        SOURCE_ID,
        J.RESORT,
        RESERVATION_DATE
      HAVING
              SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date,'DD')  THEN PAX ELSE 0 END)
              -SUM(CASE WHEN TRUNC(ISSUE_DATE,'DD') = TRUNC(current_date-1,'DD')  THEN PAX ELSE 0 END)  
              <>0
    ;
    COMMIT;
 
"""


# Изпълнение на PL/SQL блока
cursor.execute(plsql_block)

# Затваряне на курсора и връзката
cursor.close()
connection.close()

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





