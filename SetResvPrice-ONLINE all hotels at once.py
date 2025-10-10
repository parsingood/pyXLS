import cx_Oracle
import subprocess
import datetime
import os


#Хотели
hotels=[ 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
 'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 
 'PAN', 'VMG'
    ]
    
#hotels=[ 'GER']   

hotels_str="'" + "','".join(hotels) + "'"

# Настройки за Oracle
oracle_username = "your_username"
oracle_password = "your_password"
oracle_dsn = "hostname:port/service_name"

# Път към PEngine.EXE
engine_path = r"c:\ivanm\exe\PEngine.EXE"

# Връзка с Oracle
print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') 
connection = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns)
cursor = connection.cursor()

# Днешна дата
today = datetime.date.today()
date_from = today.strftime("%d%m%Y")
# SQL заявка
sql = f"""
SELECT 
  R.RESORT AS HOT,
  R.RESV_NAME_ID,
  R.CONFIRMATION_NO AS CONFIRM_NO,
  TRAIN.ALB_GET_RES_AMNT(R.RESORT, R.RESV_NAME_ID) AS AMOUNT_BGN,
  TO_NUMBER(REGEXP_SUBSTR(TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID),
                          'Amount:([0-9]+\.?[0-9]*)BGN', 1, 1, NULL, 1)) AS COMMENT_AMOUNT_BGN
FROM 
  OPERA.RESERVATION_NAME R
  JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT AND EN.RESV_NAME_ID = R.RESV_NAME_ID 
                                               AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
  LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID
WHERE 
  R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
  AND NVL(EN.ADULTS + EN.CHILDREN, 0) > 0
  AND R.TRUNC_BEGIN_DATE >= TO_DATE('{date_from}','DDMMYYYY')
  AND R.RESORT IN ({hotels_str})
  AND UPPER(SO.COMPANY) LIKE 'ONLINE%'
  AND TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID) LIKE '%Amount:%'
  AND ABS(TRAIN.ALB_GET_RES_AMNT(R.RESORT, R.RESV_NAME_ID) - 
          TO_NUMBER(REGEXP_SUBSTR(TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID),
                                  'Amount:([0-9]+\.?[0-9]*)BGN', 1, 1, NULL, 1))) > 0.01
"""

#print(sql)
#exit()

# Изпълнение на заявката
cursor.execute(sql)

rows = cursor.fetchall()

print(f"Намерени резервации за корекция: {len(rows)}")

# За всяка резервация стартираме EXE
for row in rows[:1]:
    resort, resv_name_id, confirmation, current_price, comment_price = row
    
    custom_env = os.environ.copy()
    custom_env["ORACLE_HOME"] = r"C:\app\Ivanm\product\11.2.0\client_1"
    custom_env["TNS_ADMIN"] = r"C:\app\Ivanm\product\11.2.0\client_1\network\admin"
    custom_env["PATH"] += r";C:\app\Ivanm\product\11.2.0\client_1\bin"

    cmd = [
        engine_path,
        "-SetResvPrice",
        f"RESV_NAME_ID={resv_name_id}",
        f"CUSTOM_PRICE={comment_price}"
    ]

    print(f"\n===> hotel={resort}, confirmation={confirmation}, RESV_NAME_ID={resv_name_id}, price={current_price}, new_price={comment_price}")
    print(f"Команда: {' '.join(cmd)}")

    try:
        result = subprocess.run(" ".join(cmd), shell=True, cwd=r"c:\ivanm\exe", env=custom_env)
#        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("-----stdout begin-----")
        print(result.stdout)
        print("-----stdout end-----")
        
    except subprocess.CalledProcessError as e:
        print("❌ Грешка:")
        print(e.stderr)

    print("-" * 40)

# Затваряне на връзката
cursor.close()
connection.close()
