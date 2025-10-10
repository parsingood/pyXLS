import email, smtplib, ssl
from email.message import EmailMessage
import datetime
import cx_Oracle
import os

# Конфигурация
receiver_email = ["ivanm@albena.bg"]
sender_email = "ivanm.albena@gmail.com"
sender_password = "npdkxrfpkmiwqmng"
mailserver = "smtp.gmail.com"

print('Started at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

# Инициализация на Oracle клиент
cx_Oracle.init_oracle_client(lib_dir=r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera')
conn = cx_Oracle.connect(user='opera', password='opera', dsn=dsn_tns)
cursor = conn.cursor()

# Обединена заявка със и без DOB
sql = """
SELECT 
  AGE_GROUP,
  COUNT(CASE WHEN YR = 2017 THEN 1 END) AS Y2017,
  COUNT(CASE WHEN YR = 2018 THEN 1 END) AS Y2018,
  COUNT(CASE WHEN YR = 2019 THEN 1 END) AS Y2019,
  COUNT(CASE WHEN YR = 2020 THEN 1 END) AS Y2020,
  COUNT(CASE WHEN YR = 2021 THEN 1 END) AS Y2021,
  COUNT(CASE WHEN YR = 2022 THEN 1 END) AS Y2022,
  COUNT(CASE WHEN YR = 2023 THEN 1 END) AS Y2023,
  COUNT(CASE WHEN YR = 2024 THEN 1 END) AS Y2024,
  COUNT(CASE WHEN YR = 2025 THEN 1 END) AS Y2025
FROM (
  SELECT 
    CASE 
      WHEN FLOOR((R.TRUNC_BEGIN_DATE - TO_DATE(DOB_STR, 'DD.MM.YYYY')) / 365.25) <= 18 THEN 'до 18'
      WHEN FLOOR((R.TRUNC_BEGIN_DATE - TO_DATE(DOB_STR, 'DD.MM.YYYY')) / 365.25) BETWEEN 19 AND 26 THEN '19–26'
      WHEN FLOOR((R.TRUNC_BEGIN_DATE - TO_DATE(DOB_STR, 'DD.MM.YYYY')) / 365.25) BETWEEN 27 AND 40 THEN '27–40'
      WHEN FLOOR((R.TRUNC_BEGIN_DATE - TO_DATE(DOB_STR, 'DD.MM.YYYY')) / 365.25) BETWEEN 41 AND 55 THEN '41–55'
      WHEN FLOOR((R.TRUNC_BEGIN_DATE - TO_DATE(DOB_STR, 'DD.MM.YYYY')) / 365.25) BETWEEN 56 AND 70 THEN '56–70'
      ELSE 'над 70'
    END AS AGE_GROUP,
    EXTRACT(YEAR FROM R.TRUNC_BEGIN_DATE) AS YR
  FROM OPERA.RESERVATION_NAME R
  JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID
  JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT AND EN.RESV_NAME_ID = R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
  LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
  LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY
  CROSS APPLY (SELECT NVL(OPERA.bts_sh_sens.dob(R.NAME_ID), OPERA.bit_sh_sens.dob(R.NAME_ID)) AS DOB_STR FROM DUAL)
  WHERE R.RESORT IN ('GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'MAG', 'SUP', 'RAL', 'VIT', 'KPS', 'VMG', 'GOR')
    AND R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
    AND NVL(RT.PSEUDO_YN, 'N') = 'N'
    AND R.TRUNC_BEGIN_DATE BETWEEN TO_DATE('01.01.2017', 'DD.MM.YYYY') AND TO_DATE('31.12.2025', 'DD.MM.YYYY')
    AND DOB_STR IS NOT NULL

  UNION ALL

  SELECT 
    'неизвестна възраст' AS AGE_GROUP,
    EXTRACT(YEAR FROM R.TRUNC_BEGIN_DATE) AS YR
  FROM OPERA.RESERVATION_NAME R
  JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID
  JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT AND EN.RESV_NAME_ID = R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
  LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
  LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY
  CROSS APPLY (SELECT NVL(OPERA.bts_sh_sens.dob(R.NAME_ID), OPERA.bit_sh_sens.dob(R.NAME_ID)) AS DOB_STR FROM DUAL)
  WHERE R.RESORT IN ('GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'MAG', 'SUP', 'RAL', 'VIT', 'KPS', 'VMG', 'GOR')
    AND R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
    AND NVL(RT.PSEUDO_YN, 'N') = 'N'
    AND R.TRUNC_BEGIN_DATE BETWEEN TO_DATE('01.01.2017', 'DD.MM.YYYY') AND TO_DATE('31.12.2025', 'DD.MM.YYYY')
    AND DOB_STR IS NULL
)
GROUP BY AGE_GROUP
ORDER BY 
  CASE 
    WHEN AGE_GROUP = 'до 18' THEN 1
    WHEN AGE_GROUP = '19–26' THEN 2
    WHEN AGE_GROUP = '27–40' THEN 3
    WHEN AGE_GROUP = '41–55' THEN 4
    WHEN AGE_GROUP = '56–70' THEN 5
    WHEN AGE_GROUP = 'над 70' THEN 6
    ELSE 7
  END
"""

# Изпълнение на заявката
cursor.execute(sql)

# Обработка на резултата
columns = [col[0] for col in cursor.description]
rows = [columns]
for row in cursor:
    rows.append(list(map(str, row)))

data_str = '\n'.join(['\t'.join(row) for row in rows])

# Запис във файл на диска
filename = "year_guests_by_age_groups.tsv"
with open(filename, "w", encoding="utf-8") as f:
    f.write(data_str)

# Изпращане по имейл
msg = EmailMessage()
msg['Subject'] = 'Справка: Брой гости по възрастови групи (2017–2025)'
msg['From'] = sender_email
msg['To'] = receiver_email[0]
msg.set_content('Прикачена е справката с гости по възрастови групи (вкл. "неизвестна възраст") за 2017–2025.')

with open(filename, 'rb') as f:
    msg.add_attachment(f.read(), maintype='text', subtype='plain', filename=filename)

print('Sending email at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

server = smtplib.SMTP_SSL(mailserver)
server.login(sender_email, sender_password)
server.send_message(msg)
server.quit()

# Финал
cursor.close()
conn.close()
print('Done.\n')
