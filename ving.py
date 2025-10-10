import email, smtplib, ssl
import os
import re

from email.message import EmailMessage

import datetime 
import cx_Oracle


#receiver_email = "reservations@albena.bg"
receiver_email = ["reservations@medica-albena.com","ivanm@albena.bg"]


print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') # if needed, place an 'r' before any parameter in 
conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
cursor = conn.cursor()
sql = '''
SELECT 
 R.RESV_STATUS
 , R.RESORT
 , R.CONFIRMATION_NO CONFIRM_NO
 , EN.ADULTS AD, EN.CHILDREN CH
 , TO_CHAR(R.TRUNC_BEGIN_DATE,'DD.MM.YYYY') ARRIVAL 
 , TO_CHAR(R.TRUNC_END_DATE,'DD.MM.YYYY') DEPARTURE 
 , NVL(N.LAST ,'???????') LAST_NAME
 , NVL(N.FIRST,'???????') FIRST_NAME
 , SO.COMPANY SOURCE_NAME
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN 
 ON EN.RESORT = R.RESORT       
 AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E 
 ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY 
 WHERE NVL(RT.PSEUDO_YN ,'N')='N'
   AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND UPPER(SO.COMPANY) LIKE 'NORDIC LEISURE TRAVEL GROUP LTD%'
 AND R.TRUNC_BEGIN_DATE between TO_DATE('25062025','DDMMYYYY') and TO_DATE('25062025','DDMMYYYY')
 AND R.TRUNC_END_DATE between TO_DATE('26062025','DDMMYYYY') and TO_DATE('26062025','DDMMYYYY')
 AND R.RESORT IN ('GER','BOR','ARB','OAS','VIT','OR1','FLG','LAM')
'''

cursor.execute(sql)
header = ['RESV_STATUS', 'RESORT', 'CONFIRM_NO', 'AD', 'CH', 'ARRIVAL', 'DEPARTURE', 'LAST_NAME', 'FIRST_NAME', 'SOURCE_NAME']
rows = [header]
for row in cursor:
    rows.append(list(map(str, row)))
data_str = '\n'.join(['\t'.join(row) for row in rows])
cursor.close()
conn.close()


sender_email = "ivanm.albena@gmail.com"
sender_password = "npdkxrfpkmiwqmng" 
mailserver = "smtp.gmail.com"

# Create the email message
msg = EmailMessage()
msg['Subject'] = 'VING Reservations'
msg['From'] = sender_email
msg['To'] =  receiver_email[0]
msg.set_content('VING Reservations')
msg.add_attachment(data_str, filename='reservation_data.txt', subtype='plain')
text = msg.as_string()
print('Sending email at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

#mailserver = "mail.wservices.ch"
#sender_email = "ivanm@albena.life"
#sender_password = "Y_gJ5Ect?N+k9,)"
#with smtplib.SMTP_SSL(mailserver, 465) as server:
#    server.login(sender_email, sender_password)
#    server.sendmail(sender_email, receiver_email, text)


server = smtplib.SMTP_SSL("smtp.gmail.com")
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_email, text)


