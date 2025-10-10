import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


to_email ="ivanm@albena.bg" #"velina.gyumova@albena.bg",
receiver_email = ["ivanm@albena.bg"]

#to_email ="mtodorova@albena.bg"
#receiver_email = ["mtodorova@albena.bg","velina.gyumova@albena.bg","ivanm@albena.bg"]

#"viktoriya.valkova@albena.bg,"maya.lazarova@albena.bg""

#mailserver = "mail.albena.bg"
directory = "C:/test/"

mailserver = "smtp.gmail.com"
sender_email = "ivanm.albena@gmail.com"
sender_password = "mzlqlnrrpjtasxra"

mailserver = "mail.wservices.ch"
sender_email = "ivanm@albena.life"
sender_password = "Y_gJ5Ect?N+k9,)"


import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import datetime 
import cx_Oracle

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
#conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
#cursor = conn.cursor()

today = datetime.date.today() # - datetime.timedelta(days=1)
TODAY_STR = today.strftime("%d.%m.%Y")
lastay = today - datetime.timedelta(365)
otherstay = today - datetime.timedelta(365+365+365) #2019
THEDATE = today.strftime("%d.%m.%Y")
THEDATE_SHORT = today.strftime("%d.%m.%y")

month_day_from = (3,1) # (month, day)
month_day_till = (11,30) # (month, day)
first_week_day = (1,1) # (month, day)
for_period = " 01.03-30.11.2025 "
year_this = 2025

#today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

HOTELS = [('''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
''','Albena'),
(''' 'MUR' ''','White Lagoon'),
(''' 'MGS', 'ROP', 'HOL', 'NEP' ''','Primorsko')]


today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")
year_this = today.year


# Генериране на SQL колони за месеци
columns_by_month = []

columns_by_month = []

yesterday = today - datetime.timedelta(1)
for month in range(month_day_from[0], month_day_till[0] + 1):
    start_date = datetime.datetime(year_this, month, 1)
    end_date = (datetime.datetime(year_this, month + 1, 1) - datetime.timedelta(days=1)) if month < 12 else datetime.datetime(year_this, 12, 31)

    # Име на месеца (например FEB, MAR)
    month_name = start_date.strftime('%b').upper()

    column = f"""
        SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') 
                 AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                          AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                 THEN paxrooms ELSE 0 END) AS "{month_name}"
    """

    columns_by_month.append(column)

month_columns_sql = ", ".join(columns_by_month)




#cols_ignore = [0,2,3] 
cols_ignore=[]
cols_sum_ignore=[0,1]
#cols_with_sum = list(range(4, 4+days+1))
#cols_with_sum.extend(range(4+days+5, 4+days + 5 + days))
cols_with_sum = [2]
cols_blue = [6,7,8]

column = ''',SUM(case when the_date = 
TO_DATE(\'''' + (today).strftime("%Y%m%d") + '''\','YYYYMMDD')  
then paxrooms else 0 end )  
 "at ''' + (today).strftime("%d.%m %a") + '''" '''

where = ''' SUM(case when the_date = 
TO_DATE(\'''' + (today).strftime("%Y%m%d") + '''\','YYYYMMDD')  
then paxrooms else 0 end )  
  <> 0 '''


# Основна SQL заявка
sql = f'''
SELECT TourOperator "Туроператор", RESORT "Хотел", 
    SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) AS "at {today.strftime('%d.%m %a')}"
    , {month_columns_sql}
FROM (
    SELECT TourOperator, RESORT, the_date, reservation_date, SUM(paxrooms) paxrooms
    FROM (
        SELECT resort, SR.COMPANY TourOperator, e.reservation_date, e.ISSUE_DATE the_date,
               SUM(e.pax) paxrooms
        FROM train.ALB_OCCUPANCY_RATE_JURNAL e
        LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID = SR.NAME_ID
        WHERE e.ISSUE_DATE = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD')
          AND e.reservation_date BETWEEN TO_DATE('{datetime.datetime(year_this, month_day_from[0], month_day_from[1]).strftime('%Y%m%d')}', 'YYYYMMDD')
                                    AND TO_DATE('{datetime.datetime(year_this, month_day_till[0], month_day_till[1]).strftime('%Y%m%d')}', 'YYYYMMDD')
          AND e.RESORT IN (@HOTELS)
          AND SR.COMPANY NOT IN ('STF', 'CONTRACTS', 'Block for future overbookings')
        GROUP BY e.ISSUE_DATE, e.reservation_date, SR.COMPANY, e.RESORT
    )
    GROUP BY TourOperator, RESORT, the_date, reservation_date
) occ
GROUP BY TourOperator, RESORT
HAVING SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0
ORDER BY TourOperator, RESORT

'''

#,'MNG-KLIMENT KOLEV'

#print (sql)

#exit()

current_time = datetime.datetime.now()
#today = datetime.date.today()
dt_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
workbook = xlsxwriter.Workbook('C:/test/CurrentOvernights-'+dt_string+'.xlsx')
bold = workbook.add_format({'bold': True})

merge_format = workbook.add_format({
    'align':    'center',
    'valign':   'vcenter',
#    'fg_color': '#DDDDDD',
    'text_wrap': True
})

merge_bold = workbook.add_format({
    'bold':     True,
    'align':    'center',
    'valign':   'vcenter',
#    'fg_color': '#DDDDDD',
    'text_wrap': True
})

header_format =workbook.add_format({
    'bold':     True,
    'border':   1,
    'align':    'center',
    'valign':   'vcenter',
#    'fg_color': '#DDDDDD',
    'text_wrap': True
})

border =workbook.add_format({
    'border':   1,
})

border_bold =workbook.add_format({
    'border':   1,
    'bold':     True,
})

border_currency =workbook.add_format({
    'border':   1,
    'num_format': '# ##0.00[$ лв.]'
})

border_currency_bold =workbook.add_format({
    'bold':     True,
    'border':   1,
    'num_format': '# ##0.00[$ лв.]'
})


# Създаваме формат със светло синкаво-сив фон
border_light_blue = workbook.add_format({
    'bg_color': '#f0f7fa',  # Светло синкаво-сив цвят
    'border': 1,            # Добавяме рамка за видимост
})
border_light_blue_bold = workbook.add_format({
    'bg_color': '#f0f7fa',  # Светло синкаво-сив цвят
    'border': 1,            # Добавяме рамка за видимост
    'bold':     True,
})


for hotel_list in HOTELS:

    worksheet = workbook.add_worksheet(name=hotel_list[1])
    worksheet.set_row(0, 30)  # Увеличава височината на първия ред
    cr = 0

    ## - Table 1
    worksheet.merge_range(cr, 0, cr, 3, 
    f"Брой нощувки към {today.strftime('%d.%m.%Y')} за периода {for_period} в {hotel_list[1]} по туроператори и хотели"
    , merge_bold)


    cr+=2


    conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
    cursor = conn.cursor()
    cursor.execute(sql.replace('@HOTELS',hotel_list[0])  )

    print('T1 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

    cl = 0
    c = 0
    for hd in [i[0] for i in cursor.description]:
        if cl not in cols_ignore :
            worksheet.write(cr, c, hd, header_format)
            c+=1
        cl=cl+1
    cr=cr+1
    r1 = cr
    for row in cursor:
        cl = 0
        c = 0
        for col in row:
            if cl not in cols_ignore :
                # Bold specific column (e.g., "at ...")
                if c == 2:  # Assuming "at ..." is the third column (index 2)
                    worksheet.write(cr, c, col, border_bold)
                elif c in cols_blue:  # Проверка дали колоната попада в обхвата
                    worksheet.write(cr, c, col, border_light_blue)
                else:
                    worksheet.write(cr, c, col, border)
                
                
                c+=1
            cl=cl+1
        cr=cr+1
    r2 = cr-1
    if r2-r1 > 0:
        
 #       for sumCol in cols_with_sum:
 #           worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 

        # Adding sums for all columns
        for col_index in range(len(cursor.description)):
            if col_index not in cols_ignore and col_index not in cols_sum_ignore:
                worksheet.write_formula(
                    cr, col_index,
                    f'=SUM({xl_rowcol_to_cell(r1, col_index)}:{xl_rowcol_to_cell(r2, col_index)})',
                    border_light_blue_bold if col_index in cols_blue else border_bold  
                )
        worksheet.set_row(cr, 30)  # Увеличава височината на cr ред
        cr=cr+1

    cr=cr+1

 
    cr=cr+1
    cr=cr+1

    worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
    cr=cr+1
    worksheet.write(cr, 1, 'Изготвил: Иван Михайлов')

    conn.close()
    worksheet.set_column(0, 0, 35)
    worksheet.set_column(2, 2, 15)
    #worksheet.set_column(8, 8, 11)
    #worksheet.set_column(19,19, 11)
  
    print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

workbook.close()

#exit()
yesterday_day=(today + datetime.timedelta(-1)).strftime("%d.%m %a")
subject = f"Hощувки към {yesterday_day} в периода {for_period} "
body = f"Нощувките в периода {for_period} според наличните резервации към {yesterday_day}"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^CurrentOvernights.+\.xlsx', f)]
for filename in files:
    # Open file in binary mode
    with open(directory + filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Add attachment to message and convert message to string
    message.attach(part)
    os.remove(directory + filename)

text = message.as_string()
# Log in to server 
print('Sending email at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

#with smtplib.SMTP(mailserver) as server:
    #server.login(sender_email, password)
#    server.sendmail(sender_email, receiver_email, text)

with smtplib.SMTP_SSL(mailserver, 465) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, text)





print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





