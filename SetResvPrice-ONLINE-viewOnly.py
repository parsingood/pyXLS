import cx_Oracle
import subprocess
import datetime
import os

# Настройки за Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera')
connection = cx_Oracle.connect(user='opera', password='opera', dsn=dsn_tns)
cursor = connection.cursor()

# Път към PEngine.EXE
engine_path = r"c:\ivanm\exe\PEngine.EXE"

# ORACLE среда за subprocess
custom_env = os.environ.copy()
custom_env["ORACLE_HOME"] = r"C:\app\Ivanm\product\11.2.0\client_1"
custom_env["TNS_ADMIN"] = r"C:\app\Ivanm\product\11.2.0\client_1\network\admin"
custom_env["PATH"] += r";C:\app\Ivanm\product\11.2.0\client_1\bin"

# Хотели
hotels = [
    'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG',
    'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG',
    'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS',
    'PAN', 'VMG'
]

# Днешна дата
today = datetime.date.today()
date_from = today.strftime("%d%m%Y")

print('Started at', today.strftime("%A, %d.%m.%Y %X"), "\n")

# Минаваме хотел по хотел
for hotel in hotels:
    print(f"\n>>> Проверка на хотел: {hotel}")
    
    sql = f"""
    SELECT 
      R.RESORT AS HOT,
      R.RESV_NAME_ID,
      R.CONFIRMATION_NO AS CONFIRM_NO,
      TRAIN.ALB_GET_RES_AMNT(R.RESORT, R.RESV_NAME_ID) AS AMOUNT_BGN,
      TO_NUMBER(REGEXP_SUBSTR(TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID),
                              'Amount:([0-9]+\.?[0-9]*)BGN', 1, 1, NULL, 1)) AS COMMENT_AMOUNT_BGN,
                              TRAIN.ALB_GET_RES_AMNT(R.RESORT, R.RESV_NAME_ID) - 
      TO_NUMBER(REGEXP_SUBSTR(TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID),
                              'Amount:([0-9]+\.?[0-9]*)BGN', 1, 1, NULL, 1)) diff
    FROM 
      OPERA.RESERVATION_NAME R
      JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN 
        ON EN.RESORT = R.RESORT AND EN.RESV_NAME_ID = R.RESV_NAME_ID 
        AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
      LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID
    WHERE 
      R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
      AND NVL(EN.ADULTS + EN.CHILDREN, 0) > 0
      AND R.TRUNC_BEGIN_DATE >= TO_DATE('{date_from}','DDMMYYYY')
      AND R.RESORT = '{hotel}'
      AND UPPER(SO.COMPANY) LIKE 'ONLINE%'
      AND TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID) LIKE '%Amount:%'
      AND ABS(TRAIN.ALB_GET_RES_AMNT(R.RESORT, R.RESV_NAME_ID) - 
              TO_NUMBER(REGEXP_SUBSTR(TRAIN.ALB_GET_RES_COMMENT(R.RESORT, R.RESV_NAME_ID),
                                      'Amount:([0-9]+\.?[0-9]*)BGN', 1, 1, NULL, 1))) > 0.01
    """

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"❌ SQL грешка за хотел {hotel}: {e}")
        continue

    print(f"Намерени резервации за корекция: {len(rows)}")

    for row in rows:
        resort, resv_name_id, confirmation, current_price, comment_price, diff = row
        cmd = [
            engine_path,
            "-SetResvPrice",
            f"RESV_NAME_ID={resv_name_id}",
            f"CUSTOM_PRICE={comment_price}"
        ]

        print(f"\n===> hotel={resort}, confirmation={confirmation}, RESV_NAME_ID={resv_name_id}, price={current_price}, new_price={comment_price}, diff={diff}")
        # print(f"Команда: {' '.join(cmd)}")

        # try:
            # result = subprocess.run(" ".join(cmd), shell=True, cwd=r"c:\ivanm\exe", env=custom_env)
            # if result.stdout
                # print(result.stdout)
                
        # except subprocess.CalledProcessError as e:
            # print("❌ Грешка при изпълнение на команда:")
            # print(e.stderr)

        # print("-" * 40)

# Затваряне на връзката
cursor.close()
connection.close()

print("\nВсички хотели обработени успешно.")
