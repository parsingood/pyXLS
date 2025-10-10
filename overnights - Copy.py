import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import sys
import datetime
import argparse

import cx_Oracle

to_email ="ivanm@albena.bg" #"velina.gyumova@albena.bg",
receiver_email = ["ivanm@albena.bg"]

to_email ="mtodorova@albena.bg"
receiver_email = ["mtodorova@albena.bg","velina.gyumova@albena.bg","ivanm@albena.bg","maya.lazarova@albena.bg"]

#"viktoriya.valkova@albena.bg,"maya.lazarova@albena.bg"

#mailserver = "mail.albena.bg"
directory = "C:/test/"

# mailserver = "smtp.gmail.com"
# sender_email = "ivanm.albena@gmail.com"
# sender_password = "mzlqlnrrpjtasxra"

mailserver = "mail.wservices.ch"
sender_email = "ivanm@albena.life"
sender_password = "Y_gJ5Ect?N+k9,)"



def generate_sheet(workbook, sql, sheet_name, title, body, cols_ignore, cols_sum_ignore, cols_blue, widths):
    worksheet = workbook.add_worksheet(name=sheet_name)
    cr = 0

    # print(sql)

    try:
        worksheet.merge_range(cr, 0, cr, 9 + len(cols_sum_ignore), title, merge_bold)
        cr += 2

        conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns)
        cursor = conn.cursor()
        cursor.execute(sql)

        print(f'{sheet_name} executed at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X"))

        # Мапинг: Реален индекс -> Видим индекс
        visible_col_indices = []
        visible_index = 0

        # Първо заглавията
        for real_index, hd in enumerate([i[0] for i in cursor.description]):
            if real_index not in cols_ignore:
                worksheet.write(cr, visible_index, hd, header_format)
                visible_col_indices.append((real_index, visible_index))
                visible_index += 1

        cr += 1
        r1 = cr

        for row in cursor:
            visible_index = 0
            for real_index, col in enumerate(row):
                if real_index not in cols_ignore:
                    # Пишем данните
                    if visible_index ==  len(cols_sum_ignore): # 2:  # "updown" е третата видима колона (индекс 2)
                        worksheet.write(cr, visible_index, col, border_bold)
                    elif visible_index in cols_blue:
                        worksheet.write(cr, visible_index, col, border_light_blue)
                    else:
                        worksheet.write(cr, visible_index, col, border)
                    visible_index += 1
            cr += 1

        r2 = cr - 1

        # Сумиране най-отдолу
        if r2 - r1 > 0:
            for real_index, visible_index in visible_col_indices:
                if real_index not in cols_sum_ignore:
                    worksheet.write_formula(
                        cr, visible_index,
                        f'=SUM({xl_rowcol_to_cell(r1, visible_index)}:{xl_rowcol_to_cell(r2, visible_index)})',
                        border_light_blue_bold if visible_index in cols_blue else border_bold
                    )
            worksheet.set_row(cr, 30)
            cr += 1

        cr += 2
        worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
        cr += 1
        worksheet.write(cr, 1, 'Изготвил: Иван Михайлов')

        # Ширини на колоните
        for width in widths:
            worksheet.set_column(*width)
            
        # worksheet.set_column(0, 0, 35)
        # worksheet.set_column(1, 1, 20)
        # worksheet.set_column(2, 2, 15)

        worksheet.freeze_panes(3, 0) 
        
        conn.close()

    except Exception as e:
        worksheet.write(0, 0, f"Грешка при генериране на листа: {str(e)}")





print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')



parser = argparse.ArgumentParser(
    description="Справка за нощувките - общ брой към дадена дата или изменението им от определени дни назад до дадена дата",
    epilog="""Пример: py overnights_months.py --date 2025-04-24 --back 1
или py overnights_months.py --back 1
или py overnights_months.py --back 7""",
    add_help=True
)
# Четем аргументите
parser = argparse.ArgumentParser(description="Генериране на справка за заетост и гости по хотели.")
parser.add_argument('--date', type=str, help="Датата към която правим справката във формат YYYY-MM-DD")
parser.add_argument('--back', type=str, help="Дата или брой дни назад, от която правим разликата - ако е дата да е във формат YYYY-MM-DD или число(положително число), ако липсва се дава пълното състояние към дадената дата, а не разликите")

args = parser.parse_args()
# Дати за днес и вчера
today = datetime.date.today()
yesterday = None #today - datetime.timedelta(days=1)

if args.date:
    today = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()

if args.back:
    try:
        yesterday = datetime.datetime.strptime(args.back, "%Y-%m-%d").date()
        
    except:
        try:
            yesterday = today - datetime.timedelta(days=int(args.back))
            
        except:
            parser.print_help()
            exit()
       

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') 


# Основни параметри за периода
month_day_from = (3, 1)     # (месец, ден) - начало
month_day_till = (11, 30)   # (месец, ден) - край
year_this = 2025

# Дати за началото и края на сезона
date_from = datetime.datetime(year_this, month_day_from[0], month_day_from[1])
date_till = datetime.datetime(year_this, month_day_till[0], month_day_till[1])

# Период за надписи (пример: 01.03-30.11.2025)
for_period = f"{date_from.strftime('%d.%m')}-{date_till.strftime('%d.%m')}.{date_till.strftime('%Y')}"

# Форматирани дати за текстове и репорти
TODAY_STR = today.strftime("%d.%m.%Y")

# HOTELS групите
HOTELS = [
    ([
    'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
    'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
    'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
    ], 'Albena'),
    ([ 'MUR' ], 'White Lagoon'),
    ([ 'MGS', 'ROP', 'HOL', 'NEP' ], 'Primorsko')
]

# Генериране на SQL колони за месеци
columns_by_month = []

for month in range(month_day_from[0], month_day_till[0] + 1):
    start_date = datetime.datetime(year_this, month, 1)
    end_date = datetime.datetime(year_this, month + 1, 1) - datetime.timedelta(days=1) if month < 12 else datetime.datetime(year_this, 12, 31)

    # Име на месеца за SQL колоната
    month_name = start_date.strftime('%b').upper()

    if yesterday:
        column = f"""
            SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') 
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END)
            -
            SUM(CASE WHEN the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') 
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END) AS "{month_name}"
        """
        
    else:
        column = f"""
            SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') 
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END) AS "{month_name}"
        """
    columns_by_month.append(column)

# Обединени колони за SQL
month_columns_sql = ", ".join(columns_by_month)

# За специфични обработки в Excel
cols_ignore = []
cols_sum_ignore = [0, 1]
cols_with_sum = [2]
cols_blue = [6, 7, 8]

# Основна SQL заявка
if yesterday:
    sql = f'''
    SELECT OCC.TourOperator "Туроператор", R.SEASON2 "Хотел", 
        SUM(CASE WHEN OCC.the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END)
        - SUM(CASE WHEN OCC.the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END) AS "updown",
        {month_columns_sql}
    FROM (
        SELECT TourOperator, RESORT, the_date, reservation_date, SUM(paxrooms) paxrooms
        FROM (
            SELECT resort, SR.COMPANY TourOperator, e.reservation_date, e.ISSUE_DATE the_date,
                   SUM(e.pax) paxrooms
            FROM train.ALB_OCCUPANCY_RATE_JURNAL e
            LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID = SR.NAME_ID
            WHERE
              (    
                    e.ISSUE_DATE = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') 
                OR  e.ISSUE_DATE = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD')
              )
              AND e.reservation_date BETWEEN TO_DATE('{date_from.strftime('%Y%m%d')}', 'YYYYMMDD')
                                         AND TO_DATE('{date_till.strftime('%Y%m%d')}', 'YYYYMMDD')
              AND e.RESORT IN (@HOTELS)
              AND SR.COMPANY NOT IN ('STF', 'CONTRACTS', 'Block for future overbookings')
            GROUP BY e.ISSUE_DATE, e.reservation_date, SR.COMPANY, e.RESORT
        )
        GROUP BY TourOperator, RESORT, the_date, reservation_date
    ) OCC
    JOIN OPERA.RESORT R ON R.RESORT = OCC.RESORT
    GROUP BY OCC.TourOperator, R.SEASON2, R.RESORT_TYPE
    HAVING  SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END)  
        - SUM(CASE WHEN the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0
    ORDER BY OCC.TourOperator, R.RESORT_TYPE
    '''

else:
    sql = f'''
    SELECT OCC.TourOperator "Туроператор", R.SEASON2 "Хотел", 
        SUM(CASE WHEN OCC.the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END) AS "total",
        {month_columns_sql}
    FROM (
        SELECT TourOperator, RESORT, the_date, reservation_date, SUM(paxrooms) paxrooms
        FROM (
            SELECT resort, SR.COMPANY TourOperator, e.reservation_date, e.ISSUE_DATE the_date,
                   SUM(e.pax) paxrooms
            FROM train.ALB_OCCUPANCY_RATE_JURNAL e
            LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID = SR.NAME_ID
            WHERE
              (    
                    e.ISSUE_DATE = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') 
              )
              AND e.reservation_date BETWEEN TO_DATE('{date_from.strftime('%Y%m%d')}', 'YYYYMMDD')
                                         AND TO_DATE('{date_till.strftime('%Y%m%d')}', 'YYYYMMDD')
              AND e.RESORT IN (@HOTELS)
              AND SR.COMPANY NOT IN ('STF', 'CONTRACTS', 'Block for future overbookings')
            GROUP BY e.ISSUE_DATE, e.reservation_date, SR.COMPANY, e.RESORT
        )
        GROUP BY TourOperator, RESORT, the_date, reservation_date
    ) OCC
    JOIN OPERA.RESORT R ON R.RESORT = OCC.RESORT
    GROUP BY OCC.TourOperator, R.SEASON2, R.RESORT_TYPE
    HAVING  SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0
    ORDER BY OCC.TourOperator, R.RESORT_TYPE
    '''

# --- Тук са трите типа заявки ---
sql_full = sql  # както ти е оригиналния
sql_hotels = sql.replace(
    'OCC.TourOperator "Туроператор", R.SEASON2 "Хотел",', 
    'R.SEASON2 "Хотел",'
).replace(
    'GROUP BY OCC.TourOperator, R.SEASON2, R.RESORT_TYPE',
    'GROUP BY R.SEASON2'
).replace(
    'ORDER BY OCC.TourOperator, R.RESORT_TYPE',
    'ORDER BY R.SEASON2'
)

sql_touroperators = sql.replace(
    'OCC.TourOperator "Туроператор", R.SEASON2 "Хотел",',
    'OCC.TourOperator "Туроператор",'
).replace(
    'GROUP BY OCC.TourOperator, R.SEASON2, R.RESORT_TYPE',
    'GROUP BY OCC.TourOperator'
).replace(
    'ORDER BY OCC.TourOperator, R.RESORT_TYPE',
    'ORDER BY OCC.TourOperator'
)



#print (sql)

#exit()

current_time = datetime.datetime.now()
#today = datetime.date.today()
dt_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
workbook = xlsxwriter.Workbook('C:/test/OvernightsUpDown-'+dt_string+'.xlsx')
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
    # заглавия
    if yesterday:
        if (today - yesterday).days == 1:
            title = f"Движение през {yesterday} на нощувки за периода {for_period} в {hotel_list[1]}"
            body  = f"Промяна на нощувките за периода {for_period} в резултат на постъпили нови резервации, промени или анулаци за ден {yesterday.strftime('%d.%m')}"
        else:
            title = f"Движение в интервала {yesterday.strftime('%d.%m')}-{(today - datetime.timedelta(days=1)).strftime('%d.%m')} на нощувки за периода {for_period} в {hotel_list[1]}"
            body  = f"Промяна на нощувките за периода {for_period} в резултат на постъпили нови резервации, промени или анулаци в интервала {yesterday.strftime('%d.%m')}-{(today - datetime.timedelta(days=1)).strftime('%d.%m')}"
            
    else:
        title = f"Нощувки до {today.strftime('%d.%m.%Y')} за периода {for_period} в {hotel_list[1]} по туроператори и хотели"
        body  = f"Нощувки постъпили до {today.strftime('%d.%m.%Y')} за периода {for_period} по туроператори и хотели"

    hotels_str = str(hotel_list[0]).replace('[','').replace(']','')

    if len(hotel_list[0]) > 1:
        # Лист 1 - по хотели
        generate_sheet(
            workbook=workbook,
            sql=sql_hotels.replace('@HOTELS', hotels_str),
            sheet_name=f"{hotel_list[1]}-Хотели",
            title=title + " по хотели",
            body=body,
            cols_ignore=[],              # махаме Туроператор
            cols_sum_ignore=[0],          # НЕ сумираме Хотел
            cols_blue=[5, 6, 7],          # Преместени наляво с една позиция колоните на месеците
            widths=[(0, 0, 20),(1, 1, 15)],
        )

    # Лист 2 - по туроператори
    generate_sheet(
        workbook=workbook,
        sql=sql_touroperators.replace('@HOTELS', hotels_str),
        sheet_name=f"{hotel_list[1]}-Туроператори",
        title=title + " по туроператори",
        body=body,
        cols_ignore=[],              # махаме Хотел
        cols_sum_ignore=[0],          # НЕ сумираме Туроператор
        cols_blue=[5, 6, 7],          # Преместени наляво с една позиция колоните на месеците
        widths=[(0, 0, 35),(1, 1, 15)],
    )

    if len(hotel_list[0]) > 1:
    # Лист 3 - по туроператори и хотели (основен пълен)
        generate_sheet(
            workbook=workbook,
            sql=sql_full.replace('@HOTELS', hotels_str),
            sheet_name=hotel_list[1],
            title=title + " по туроператори и хотели",
            body=body,
            cols_ignore=[],              # нищо не махаме
            cols_sum_ignore=[0, 1],       # НЕ сумираме Туроператор и Хотел
            cols_blue=[6, 7, 8],          # колоните на месеците (примерно AUG, SEP, OCT) – без изместване
            widths=[(0, 0, 35),(1, 1, 20),(2, 2, 15)],
          
        )
  
    print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

workbook.close()

#exit()

yesterday_day=(today + datetime.timedelta(-1)).strftime("%d.%m %a")
subject = title
body = body 

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^Overnights.+\.xlsx', f)]
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





