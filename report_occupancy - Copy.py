import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
subject = "Заетост по хотели и тур-агенти"
body = "Заетост за 120 дни напред по хотели и тур-агенти в нощувки и стаи, според постъпилите резервации към момента, без незаетите блокирани по гаранции и out-of-order стаи"



#receiver_email = ["reservations@albena.bg","ivanm@albena.bg"]
#to_email = "velina.gyumova@albena.bg"
#receiver_email = "ivanm@albena.bg"
#to_email ="ivanm@albena.bg"
#receiver_email = ["ivanm@albena.bg"]

to_email ="marinela.tsaneva@albena.bg"
receiver_email = ["mtodorova@albena.bg","marinela.tsaneva@albena.bg","maya.lazarova@albena.bg","ivanm@albena.bg"]

#to_email ="ivanm@albena.bg"
#receiver_email =["ivanm@albena.bg","ivanm.albena@gmail.com"]

#mailserver = "mail.albena.bg"
#sender_email = "ivanm@albena.bg"
#password = ""

mailserver = "smtp.gmail.com"
sender_email = "ivanm.albena@gmail.com"
password = "mzlqlnrrpjtasxra"

mailserver = "mail.wservices.ch"
sender_email = "ivanm@albena.life"
password = "Y_gJ5Ect?N+k9,)"




directory = "C:/test/"

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
THEDATE = today.strftime("%d.%m.%Y")
THEDATE_SHORT = today.strftime("%d.%m.%y")

HOTELS = [('''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG','GOR'
''','Albena'),
#(''' 'MUR' ''','White Lagoon'),
#(''' 'MGS', 'ROP', 'HOL', 'NEP' ''','Primorsko'),
]
paxrooms=[('СТАИ','e.QUANTITY',', e.QUANTITY'),
          ('НОЩУВКИ','(e.ADULTS + e.CHILDREN)',', e.ADULTS, e.CHILDREN')]

hotelagents = [
    ('R.SEASON5 "Хотел", R.TOT_ROOMS "All"','e.resort,',
     ''' LEFT JOIN RESORT R ON R.RESORT = OCC.RESORT
 group by R.RESORT_TYPE,R.SEASON5,R.TOT_ROOMS,R.RESORT
 ORDER BY R.RESORT_TYPE DESC ,R.SEASON5
     ''', 1),
    ('TourOperator "Тур-агент", \'\' "All" ','',
     '''
 group by TourOperator
 ORDER BY TourOperator
     ''', 1),
    ('R.SEASON5 "Хотел",TourOperator "Тур-агент", R.TOT_ROOMS "All"','e.resort,',
     ''' LEFT JOIN RESORT R ON R.RESORT = OCC.RESORT
 group by R.RESORT_TYPE,R.SEASON5,R.TOT_ROOMS,R.RESORT,TourOperator
 ORDER BY R.RESORT_TYPE DESC ,R.SEASON5, TourOperator
     ''', 0),	 
    
    ]

date1 = datetime.date.today()  # datetime.date(2023,4,14)
if date1 < datetime.date(2024,3,1):
    date1 = datetime.date(2024,3,1)
days = 120 #31
date2 = date1 + datetime.timedelta(days)
cols_ignore = [] 
#cols_with_sum = list(range(4, 4+days+1))
#cols_with_sum.extend(range(4+days+5, 4+days + 5 + days))
cols_with_sum = list(range(1, days+2))
timedelta_list = range(0,days)
columns_this = ''
for d in timedelta_list:
    columns_this += ''',SUM(case when the_date=trunc(
    TO_DATE(\'''' + (date1 + datetime.timedelta(d)).strftime("%Y%m%d") + '''\','YYYYMMDD')
    , 'DDD') then paxrooms else 0 end) "''' + (date1 + datetime.timedelta(d)).strftime("%d_%m") + '''" '''
sql='''
Select @HotelAgentSelect
''' + columns_this + '''
from(
SELECT  @HotelAgentGroupBy 
 MIN(SR.COMPANY) TourOperator
, e.reservation_date the_date
, @paxrooms paxrooms
 FROM   reservation_daily_elements e 
JOIN RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = E.RESORT AND EN.RESV_DAILY_EL_SEQ=E.RESV_DAILY_EL_SEQ AND EN.reservation_date=E.reservation_date
JOIN resort$_room_category rct ON  rct.ROOM_CATEGORY = e.ROOM_CATEGORY and rct.resort=e.resort
LEFT JOIN NAME SR ON EN.SOURCE_ID=SR.NAME_ID 
WHERE e.reservation_date  between TO_DATE(\'''' + (date1).strftime("%Y%m%d") + '''\','YYYYMMDD')
and 
TO_DATE(\'''' + (date2).strftime("%Y%m%d") + '''\','YYYYMMDD') 
and rct.label not in ('PM','PI') and e.RESV_STATUS not in ('CANCELLED','NO SHOW') and ((e.DUE_OUT_YN is null) or (e.DUE_OUT_YN ='N')) 
 AND E.RESORT IN (@HOTELS)
and SR.COMPANY not in ('GUARANTEE ALLOTENTS','OUT OF ORDER','DOGS')
group by @HotelAgentGroupBy E.RESV_DAILY_EL_SEQ, e.reservation_date
@groupby 
) occ 
@HotelAgentOrderBy

'''

current_time = datetime.datetime.now()
#today = datetime.date.today()
dt_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
workbook = xlsxwriter.Workbook('C:/test/report-'+dt_string+'.xlsx')
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
    cr = 2
    do_first_row = True
    for hotelagent in hotelagents:
        for paxroom in paxrooms:
 
            s = sql.replace('@HOTELS',hotel_list[0]) 
            s = s.replace('@paxrooms',paxroom[1])
            s = s.replace('@groupby',paxroom[2])

            s = s.replace('@HotelAgentSelect',hotelagent[0])
            s = s.replace('@HotelAgentGroupBy',hotelagent[1])
            s = s.replace('@HotelAgentOrderBy',hotelagent[2])

            cs = hotelagent[3]
            ## - Table
            worksheet.merge_range(cr, 0, cr, days+2, 'Заетост - '+paxroom[0]+' ', merge_bold  )
            cr+=2
            conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
            cursor = conn.cursor()
            cursor.execute(s)

            print('T1 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

            cl = 0
            c = 0
            for hd in [i[0] for i in cursor.description]:
                if cl not in cols_ignore :
                    worksheet.write(cr, c + cs, hd, header_format)
                    if do_first_row : worksheet.write(0, c + cs, hd, header_format)
                    c+=1
                
                cl=cl+1
            do_first_row=False
            worksheet.write(0, 0 + cs, "", header_format)
            cr=cr+1
            r1 = cr
            for row in cursor:
                cl = 0
                c = 0
                for col in row:
                    if cl not in cols_ignore :
                        worksheet.write(cr, c + cs, col if str(col) != "0" else "", border)
                        c+=1
                    cl=cl+1
                cr=cr+1
            r2 = cr-1
            if r2-r1 > 0:
        
                for sumCol in cols_with_sum:
                    worksheet.write_formula(cr, sumCol + cs, '=SUM('+ xl_rowcol_to_cell(r1, sumCol + cs) +':'+  xl_rowcol_to_cell(r2, sumCol + cs) +')', bold) 
  
                cr=cr+1
            cr=cr+1
        cr=cr+1

    worksheet.write(cr, 0, 'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
    cr=cr+1
    worksheet.write(cr, 0, 'Изготвил: Иван Михайлов')
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 1, 30)
    worksheet.set_column(2, days+2 + cs, 5.5)
    conn.close()
    worksheet.freeze_panes(1, 2)
  
    print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

workbook.close()

#def get_col_widths(dataframe):
#    # First we find the maximum length of the index column   
#    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
#    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
#    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

#for i, width in enumerate(get_col_widths(dataframe)):
#    worksheet.set_column(i, i, width)




# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^report.+\.xlsx', f)]
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
#    #server.login(sender_email, password)
#    server.sendmail(sender_email, receiver_email, text)

with smtplib.SMTP_SSL(mailserver, 465) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)


print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





