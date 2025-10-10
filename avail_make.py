
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
plsql_block = f"""DECLARE
FROM_DATE DATE := TO_DATE('{TODAY_STR}','DD.MM.YYYY');
TILL_DATE DATE := TO_DATE('31.10.2027','DD.MM.YYYY');
BEGIN
  FOR X IN (
    SELECT
         H.RESORT
      ,  D.THE_DATE
      ,  T.ROOM_CATEGORY
      ,  T.ROOM_CLASS
      ,  T.NUMBER_ROOMS
    FROM OPERA.RESORT H
    JOIN OPERA.RESORT$_ROOM_CATEGORY T ON T.RESORT = H.RESORT
    , (   SELECT FROM_DATE + LEVEL - 1 THE_DATE FROM DUAL CONNECT BY LEVEL <=  TILL_DATE - FROM_DATE + 1  ) D
    WHERE 1=1
    and H.STATE IN ('ALB','PRI','WLA')
    and H.RESORT = 'ELI'
  --  and H.RESORT IN ('HOL','ARA','KPS','ELI','KLP','ROP','DRU','ALT','GER','FLA','DTC','FLG','ORL','SLA','KLK','MRA','PAN','LAB','ARB','LAM','MUR','DOR','LAG','BOR','OR1','MAG','GOR','MAL','RAL','MGS','NEP','SUP','VMG','VIT','NON','OAS','KOM') 
    AND T.ROOM_CLASS NOT IN ('P','PI')
  )
  LOOP
    DELETE FROM TRAIN.ALB_RESV_AVAILABILITY
    WHERE RESORT = X.RESORT AND THE_DATE=X.THE_DATE AND ROOM_CATEGORY=X.ROOM_CATEGORY
    ;
    INSERT INTO TRAIN.ALB_RESV_AVAILABILITY
    (RESORT,ROOM_CLASS,ROOM_CATEGORY,THE_DATE,AVAIL,OCCUP, UPDATED)
    SELECT  X.RESORT, X.ROOM_CLASS, X.ROOM_CATEGORY, X.THE_DATE
          , X.NUMBER_ROOMS - NVL(SUM(PHYSICAL_QUANTITY),0)  AVAIL
          , NVL(SUM(PHYSICAL_QUANTITY),0) OCCUP
          , CURRENT_DATE
    FROM OPERA.RESERVATION_DAILY_ELEMENTS
    WHERE RESORT=X.RESORT
      AND ROOM_CATEGORY=X.ROOM_CATEGORY
      AND RESERVATION_DATE = X.THE_DATE
      AND NVL(DUE_OUT_YN,'N')='N'
      AND RESV_STATUS NOT IN ('CANCELLED','WAITLIST','NO SHOW')
    ;
  COMMIT;
  END LOOP;
END; 
"""

# Изпълнение на PL/SQL блока
cursor.execute(plsql_block)

# Затваряне на курсора и връзката
cursor.close()
connection.close()

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





