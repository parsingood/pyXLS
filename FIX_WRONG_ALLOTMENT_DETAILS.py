
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
plsql_block = f"""  
BEGIN
         OPERA.pms_grgrid.SET_AVAILABILITY_CHECK_NO;
         OPERA.RESERVATION_I.DISABLE_AVAILABILITY_CHECK;
FOR X IN 
(
SELECT RESORT FROM OPERA.RESORT 
WHERE STATE = 'ALB'
--AND RESORT = 'FLG'
)
LOOP
  UPDATE  OPERA.ALLOTMENT$DETAIL  
  SET TO_SELL =   NVL(SOLD,0) + RELEASED ,
    PROJECTED_OCC1=0,
    PROJECTED_OCC2=0,
    PROJECTED_OCC3=0,
    PROJECTED_OCC4=0
  WHERE   RESORT = X.RESORT 
  AND  ALLOTMENT_DATE BETWEEN CURRENT_DATE - 1 AND TO_DATE('31-10-2017','DD-MM-YYYY')
  AND  NVL(TO_SELL,0) -  NVL(SOLD,0) - NVL(RELEASED,0) < 0 
  ;
  COMMIT
  ;
END LOOP;  
         OPERA.pms_grgrid.SET_AVAILABILITY_CHECK_YES;
         OPERA.RESERVATION_I.ENABLE_AVAILABILITY_CHECK;
END;
"""

# Изпълнение на PL/SQL блока
cursor.execute(plsql_block)

# Затваряне на курсора и връзката
cursor.close()
connection.close()

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





