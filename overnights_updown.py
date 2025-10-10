import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


to_email ="maya.lazarova@albena.bg" #"velina.gyumova@albena.bg",
receiver_email = ["maya.lazarova@albena.bg","ivanm@albena.bg"]

#to_email ="mtodorova@albena.bg"
#receiver_email = ["mtodorova@albena.bg","velina.gyumova@albena.bg","ivanm@albena.bg"]

#"viktoriya.valkova@albena.bg,"maya.lazarova@albena.bg""

#mailserver = "mail.albena.bg"
directory = "C:/test/"

mailserver = "smtp.gmail.com"
sender_email = "ivanm.albena@gmail.com"
sender_password = "npdkxrfpkmiwqmng"



import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import datetime 
import cx_Oracle

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
#conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
#cursor = conn.cursor()

today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")
lastay = today - datetime.timedelta(365)
otherstay = today - datetime.timedelta(365+365+365) #2019
THEDATE = today.strftime("%d.%m.%Y")
THEDATE_SHORT = today.strftime("%d.%m.%y")

month_day_from = (2,1) # (month, day)
month_day_till = (11,30) # (month, day)
first_week_day = (1,1) # (month, day)
for_period = " 01.03-30.11.2025 "
year_this = 2025
HOTELS = [('''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
''','Albena'),
(''' 'MUR' ''','White Lagoon'),
(''' 'MGS', 'ROP', 'HOL', 'NEP' ''','Primorsko')]


#cols_ignore = [0,2,3] 
cols_ignore=[]
#cols_with_sum = list(range(4, 4+days+1))
#cols_with_sum.extend(range(4+days+5, 4+days + 5 + days))
cols_with_sum = [2]

column = ''',SUM(case when the_date = 
TO_DATE(\'''' + (today).strftime("%Y%m%d") + '''\','YYYYMMDD')  
then paxrooms else 0 end )  
 - SUM(case when the_date = 
TO_DATE(\'''' + (today + datetime.timedelta(-1)).strftime("%Y%m%d") + '''\','YYYYMMDD') 
then paxrooms else 0 end )
 "at ''' + (today + datetime.timedelta(-1)).strftime("%d.%m %a")  + '''" '''
 
where = ''' SUM(case when the_date = 
TO_DATE(\'''' + (today).strftime("%Y%m%d") + '''\','YYYYMMDD')  
then paxrooms else 0 end )  
 - SUM(case when the_date = 
TO_DATE(\'''' + (today + datetime.timedelta(-1)).strftime("%Y%m%d") + '''\','YYYYMMDD') 
then paxrooms else 0 end )
  <> 0 '''

sql='''
Select TourOperator "Туроператор", RESORT "Хотел" ''' + column + '''
from(SELECT TourOperator, RESORT,  the_date
    , SUM(paxrooms) paxrooms
    from(SELECT  resort 
    , SR.COMPANY TourOperator
    , e.ISSUE_DATE the_date
    , SUM(e.pax) paxrooms
    FROM train.ALB_OCCUPANCY_RATE_JURNAL e 
    LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID=SR.NAME_ID 
    WHERE e.ISSUE_DATE  between 
    TO_DATE(\'''' + (today + datetime.timedelta(-1)).strftime("%Y%m%d") + '''\','YYYYMMDD') 
    and TO_DATE(\'''' + today.strftime("%Y%m%d") + '''\','YYYYMMDD') 
    AND  e.reservation_date  between 
    TO_DATE(\''''+ datetime.datetime(year_this, month_day_from[0], month_day_from[1]).strftime("%Y%m%d") + '''\','YYYYMMDD') 
    and TO_DATE(\''''+ datetime.datetime(year_this, month_day_till[0], month_day_till[1]).strftime("%Y%m%d") + '''\','YYYYMMDD') 
     AND E.RESORT IN (@HOTELS)
     and SR.COMPANY not in ('STF','CONTRACTS','Block for future overbookings')
    group by  e.ISSUE_DATE
    , SR.COMPANY , E.RESORT
    ) group by TourOperator, RESORT, the_date
) occ 
group by TourOperator, RESORT
HAVING ''' + where + '''
ORDER BY TourOperator, RESORT

'''

#,'MNG-KLIMENT KOLEV'

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

border_currency =workbook.add_format({
    'border':   1,
    'num_format': '# ##0.00[$ лв.]'
})

border_currency_bold =workbook.add_format({
    'bold':     True,
    'border':   1,
    'num_format': '# ##0.00[$ лв.]'
})


for hotel_list in HOTELS:

    worksheet = workbook.add_worksheet(name=hotel_list[1])
    worksheet.set_row(0, 30)  # Увеличава височината на първия ред
    cr = 0

    ## - Table 1
    yesterday = (today + datetime.timedelta(-1)).strftime("%d.%m.%y")
    worksheet.merge_range(cr, 0, cr, 3, 
    f"Движение през {yesterday} на нощувки за периода {for_period} в {hotel_list[1]} по туроператори и хотели"
    , merge_bold  )

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
                worksheet.write(cr, c, col, border)
                c+=1
            cl=cl+1
        cr=cr+1
    r2 = cr-1
    if r2-r1 > 0:
        
        for sumCol in cols_with_sum:
            worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 

 
        cr=cr+1

    cr=cr+1

 
    cr=cr+1
    cr=cr+1

    worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
    cr=cr+1
    worksheet.write(cr, 1, 'Изготвил: ')

    conn.close()
    worksheet.set_column(0, 0, 35)
    worksheet.set_column(2, 2, 15)
    #worksheet.set_column(8, 8, 11)
    #worksheet.set_column(19,19, 11)
  
    print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

workbook.close()

#exit()
yesterday_day=(today + datetime.timedelta(-1)).strftime("%d.%m %a")
subject = f"Движение за {yesterday_day} на нощувките в периода {for_period} "
body = f"Промяна на нощувките в периода {for_period} в резултат на постъпили нови резервации, промени или анулаци за ден {yesterday_day}"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^OvernightsUpDown.+\.xlsx', f)]
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

#with smtplib.SMTP_SSL(mailserver, 465) as server:
#    server.login(sender_email, sender_password)
#    server.sendmail(sender_email, receiver_email, text)

server = smtplib.SMTP_SSL("smtp.gmail.com")
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_email , text)



print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





