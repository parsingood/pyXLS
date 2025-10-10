import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
subject = "Reservations daily report"
body = "Reservations daily report"
sender_email = "ivanm@albena.bg"
receiver_email = ["velina.gyumova@albena.bg","ivanm@albena.bg"]
#receiver_email = ["reservations@albena.bg","ivanm@albena.bg"]
to_email = "velina.gyumova@albena.bg"
#receiver_email = "reservations@albena.bg"
#password = ""
mailserver = "mail.albena.bg"
directory = "C:/test/"

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import datetime 
import cx_Oracle

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
conn = cx_Oracle.connect(user=r'OPERA', password='OPERA', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'

today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")



yesterday = today - datetime.timedelta(1)
THEDATE = yesterday.strftime("%d.%m.%Y")
THEDATE_SHORT = yesterday.strftime("%d.%m.%y")
DATEFROM = '01.01.2021'
DATETILL = '31.12.2021'
HOTELS = '''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
'''
AGENTS = ''' UPPER(SO.COMPANY) LIKE 'MNG%' or UPPER(SO.COMPANY) LIKE 'CALL%' or UPPER(SO.COMPANY) LIKE 'ONLINE%' '''
c = conn.cursor()
sql_ins='''
  SELECT  R.RESORT
 , SUBSTR(H1.SEASON2,1,40) ACCOMOD_HOTEL
 , RT.LABEL RT
 , R.CONFIRMATION_NO CONFIRM_NO
 , EN.ADULTS AD
 , EN.CHILDREN CH
 , (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) OVNTS 
 , TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) AMOUNT_BGN
 , ROUND(TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) / ( (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) ),2) AVG_RES_AMNT_BGN
 , ROUND(TRAIN.ALB_GET_RES_DEPOSIT(R.RESORT,R.RESV_NAME_ID),2) DEP_BGN
 , R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE NTS 
 , TO_CHAR(R.TRUNC_BEGIN_DATE,'DD.MM.YYYY') ARRIVAL
 , TO_CHAR(R.TRUNC_END_DATE,'DD.MM.YYYY') DEPARTURE 
 , NVL(N.LAST,'???????') LAST_NAME
 , NVL(N.FIRST,'???????') FIRST_NAME
 , SO.UDFC22 MARKET
 , TO_CHAR(R.UDFD15,'DD.MM.YYYY') BOOK_DATE 
 , TO_CHAR(R.INSERT_DATE,'DD.MM.YYYY HH24:MI:SS') INSERT_DATE
 , R.GUARANTEE_CODE 
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID 
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT 
    AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT
    AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 LEFT JOIN OPERA.APPLICATION$_USER U ON U.APP_USER_ID = R.INSERT_USER 
 LEFT JOIN RESORT H1 ON H1.RESORT=R.RESORT
 LEFT JOIN RESORT H2 ON H2.RESORT=R.UDFC30
 LEFT JOIN RESORT$_ROOM_CATEGORY T2 ON T2.RESORT=R.UDFC30 AND T2.LABEL = RTC.LABEL 
 WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
 AND NVL(RT.PSEUDO_YN ,'N')='N'
 AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND ( ''' + AGENTS + ''' )
 AND R.TRUNC_END_DATE > TO_DATE(:DATE_FROM,'DD.MM.YYYY')
 AND R.TRUNC_BEGIN_DATE<= TO_DATE(:DATE_TILL,'DD.MM.YYYY')
 AND R.RESORT IN (''' + HOTELS + ''')
 AND TRUNC(R.INSERT_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY')

'''

sql_cxl='''
  SELECT  R.RESORT
 , SUBSTR(H1.SEASON2,1,40) ACCOMOD_HOTEL
 , RT.LABEL RT
 , R.CONFIRMATION_NO CONFIRM_NO
 , EN.ADULTS AD
 , EN.CHILDREN CH
 , (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) OVNTS 
 , TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) AMOUNT_BGN
 , ROUND(TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) / ( (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) ),2) AVG_RES_AMNT_BGN
 , ROUND(TRAIN.ALB_GET_RES_DEPOSIT(R.RESORT,R.RESV_NAME_ID),2) DEP_BGN
 , R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE NTS 
 , TO_CHAR(R.TRUNC_BEGIN_DATE,'DD.MM.YYYY') ARRIVAL
 , TO_CHAR(R.TRUNC_END_DATE,'DD.MM.YYYY') DEPARTURE 
 , NVL(N.LAST,'???????') LAST_NAME
 , NVL(N.FIRST,'???????') FIRST_NAME
 , SO.UDFC22 MARKET
 , TO_CHAR(R.INSERT_DATE,'DD.MM.YYYY') INSERT_DATE
 , :THE_DATE CANCEL_DATE 
 , R.GUARANTEE_CODE 
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID 
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT 
    AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT
    AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 LEFT JOIN OPERA.APPLICATION$_USER U ON U.APP_USER_ID = R.INSERT_USER 
 LEFT JOIN RESORT H1 ON H1.RESORT=R.RESORT
 LEFT JOIN RESORT H2 ON H2.RESORT=R.UDFC30
 LEFT JOIN RESORT$_ROOM_CATEGORY T2 ON T2.RESORT=R.UDFC30 AND T2.LABEL = RTC.LABEL 
 WHERE (R.RESV_STATUS = 'CANCELLED') 
 AND NVL(RT.PSEUDO_YN ,'N')='N'
 AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND (''' + AGENTS + ''' )
 AND R.TRUNC_END_DATE > TO_DATE(:DATE_FROM,'DD.MM.YYYY')
 AND R.TRUNC_BEGIN_DATE<= TO_DATE(:DATE_TILL,'DD.MM.YYYY')
 AND R.RESORT IN (''' + HOTELS + ''')
 AND (   TRUNC(R.UDFD12,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY') 
      OR (     TRUNC(R.UDFD12,'DD') IS NULL 
           AND TRUNC(R.UPDATE_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY') 
         )
     )
 AND TRUNC(R.INSERT_DATE,'DD') < TO_DATE(:THE_DATE,'DD.MM.YYYY')
'''

sql_total = '''

SELECT * FROM (  
  SELECT  DECODE(SO.UDFC22
  ,'CCA','CALL CENTER'
  ,'ONL','ONLINE RESERVATIONS'
  ,'MNG','HOTEL MANAGERS'
  ,SO.UDFC22) MARKET
 , '' x0
 , SUM(case when (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   and TRUNC(R.insert_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY')
   then TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) 
   else 0 end) NOW_RES_AMNT  
 , SUM(case when (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   and TRUNC(R.insert_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY')
   then ROUND(TRAIN.ALB_GET_RES_DEPOSIT(R.RESORT,R.RESV_NAME_ID),2) 
   else 0 end) NOW_DEP_BGN 
 , SUM(case when (R.RESV_STATUS = 'CANCELLED') 
   and ( TRUNC(R.UPDATE_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY')
      OR TRUNC(R.UDFD12,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY'))
   then TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) 
   else 0 end) NOW_CXL_AMNT
 , '' x1
 , SUM(case when (R.RESV_STATUS = 'CANCELLED')  
   then TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) 
   else 0 end) TOT_CXL_AMNT 
 , '' x2
 , SUM(case when (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   then TRAIN.ALB_GET_RES_AMNT(R.RESORT,R.RESV_NAME_ID) 
   else 0 end) TOT_RES_AMNT
 , '' x3
 , SUM(case when (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   then ROUND(TRAIN.ALB_GET_RES_DEPOSIT(R.RESORT,R.RESV_NAME_ID),2) 
   else 0 end) TOT_DEP_BGN
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID 
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT 
    AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT
    AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 LEFT JOIN OPERA.APPLICATION$_USER U ON U.APP_USER_ID = R.INSERT_USER 
 LEFT JOIN RESORT H1 ON H1.RESORT=R.RESORT
 LEFT JOIN RESORT H2 ON H2.RESORT=R.UDFC30
 LEFT JOIN RESORT$_ROOM_CATEGORY T2 ON T2.RESORT=R.UDFC30 AND T2.LABEL = RTC.LABEL 
 WHERE NVL(RT.PSEUDO_YN ,'N')='N'
 AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND ( UPPER(SO.COMPANY) LIKE 'MNG%' or UPPER(SO.COMPANY) LIKE 'CALL%' or UPPER(SO.COMPANY) LIKE 'ONLINE%'  )
 AND R.TRUNC_END_DATE > TO_DATE(:DATE_FROM,'DD.MM.YYYY')
 AND R.TRUNC_BEGIN_DATE<= TO_DATE(:DATE_TILL,'DD.MM.YYYY')
 AND R.RESORT IN (
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
)
 AND ( TRUNC(R.insert_DATE,'DD') < TO_DATE(:THE_DATE,'DD.MM.YYYY') 
    or ( TRUNC(R.insert_DATE,'DD') = TO_DATE(:THE_DATE,'DD.MM.YYYY') and (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW')  ) )

group by SO.UDFC22 
) ORDER BY TOT_RES_AMNT DESC

'''


current_time = datetime.datetime.now()
#today = datetime.date.today()
dt_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
workbook = xlsxwriter.Workbook('C:/test/ResvDaily-'+dt_string+'.xlsx')
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

worksheet = workbook.add_worksheet(name="xxx")
cr = 0

## - Table 1
worksheet.merge_range(cr, 0, cr, 17, 'СПИСЪК С НАПРАВЕНИ РЕЗЕРВАЦИ ЗА СЕЗОН 2021 В АЛБЕНА', merge_bold)
cr=cr+1
worksheet.merge_range(cr, 0, cr, 12, 'от  albena.bg, Call Center Albena, хотелски мениджъри, flamingotours.de, albenatour.bg', merge_format)
worksheet.write(cr, 13, 'на ' + THEDATE, bold)
cr=cr+2
c1 = conn.cursor()
c1.execute(sql_ins, THE_DATE = THEDATE, DATE_FROM = DATEFROM, DATE_TILL = DATETILL  )
print('T1 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
hds = ('ХОТЕЛ','','Тип Стая','Но резервация','брой въз-растни','брой деца','нощув-ки','Стойност на резервация в лв','Среден приход на нощувка в лв','Платена сума','прес-той в дни','Пристигане','Заминаване','Фамилия','Име','Пазар / Канал','Дата на резервиране','Дата на влизане в системата','Статус','Платена сума'
)
cl = 0
for hd in hds:
    worksheet.write(cr, cl, hd, header_format)
    cl=cl+1
cr=cr+1
r1 = cr
for row in c1:
    cl = 0
    for col in row:
        if cl in (7,8,9) :
            worksheet.write(cr, cl, col, border_currency) 
        else:
            worksheet.write(cr, cl, col, border) 
        cl=cl+1
    worksheet.write_formula(cr, cl, '=IF(AND('+ xl_rowcol_to_cell(cr, cl-10) +'=0,'+ xl_rowcol_to_cell(cr, cl-1) +'="WEB_PP"),'+ xl_rowcol_to_cell(cr, cl-12) +'*0.2,IF(AND('+ xl_rowcol_to_cell(cr, cl-10) +'=0,'+ xl_rowcol_to_cell(cr, cl-1) +'="WEB_GFP"),'+ xl_rowcol_to_cell(cr, cl-12) +',"0"))', border_currency) 
    cr=cr+1
r2 = cr-1
if r2-r1 > 0:
    sumCol=6
    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 
    sumCol=7
    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold) 
    sumCol=8
    worksheet.write_formula(cr, sumCol, '='+ xl_rowcol_to_cell(cr, sumCol-1) +'/'+  xl_rowcol_to_cell(cr, sumCol-2) +'', border_currency_bold)
    sumCol=9
    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
    
    #sumCols = (6,7,8,9)
    #cl = 0
    #for sumCol in sumCols:
    #    if cl in (7,8,9) :
    #        worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold) 
    #    else:
    #        worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 
    #    cl=cl+1

    

    cr=cr+1

cr=cr+1

## - Table 2
worksheet.merge_range(cr, 0, cr, 17, 'СПИСЪК С АНУЛИРАНИ РЕЗЕРВАЦИ ЗА СЕЗОН 2021 В АЛБЕНА', merge_bold)
cr=cr+1
worksheet.merge_range(cr, 0, cr, 12, 'от  albena.bg, Call Center Albena, хотелски мениджъри, flamingotours.de, albenatour.bg', merge_format)
worksheet.write(cr, 13, 'на ' + THEDATE, bold)
cr=cr+2
c2 = conn.cursor()
c2.execute(sql_cxl,  THE_DATE = THEDATE, DATE_FROM = DATEFROM, DATE_TILL = DATETILL  )
print('T2 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
hds = ('ХОТЕЛ','','Тип Стая','Но резервация','брой въз-растни','брой деца','нощув-ки','Стойност на резервация в лв','Среден приход на нощувка в лв','Платена сума','прес-той в дни','Пристигане','Заминаване','Фамилия','Име','Пазар','Дата на резервиране','Дата на анулиране','Статус','Платена сума'
)
cl = 0
for hd in hds:
    worksheet.write(cr, cl, hd, header_format)
    cl=cl+1
cr=cr+1
r1 = cr
for row in c2:
    cl = 0
    for col in row:
        worksheet.write(cr, cl, col, border) # row[0] row[1] row[2] ...
        cl=cl+1
    worksheet.write_formula(cr, cl, '=IF(AND('+ xl_rowcol_to_cell(cr, cl-10) +'=0,'+ xl_rowcol_to_cell(cr, cl-1) +'="WEB_PP"),'+ xl_rowcol_to_cell(cr, cl-12) +'*0.2,IF(AND('+ xl_rowcol_to_cell(cr, cl-10) +'=0,'+ xl_rowcol_to_cell(cr, cl-1) +'="WEB_GFP"),'+ xl_rowcol_to_cell(cr, cl-12) +',"0"))', border_currency) 
    cr=cr+1
r2 = cr-1
if r2-r1 > 0:

    sumCol=6
    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 
    sumCol=7
    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold) 
    sumCol=8
    worksheet.write_formula(cr, sumCol, '='+ xl_rowcol_to_cell(cr, sumCol-1) +'/'+  xl_rowcol_to_cell(cr, sumCol-2) +'', border_currency_bold)

    #sumCols = (6,7,8)
    #for sumCol in sumCols:
    #    worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold)
    #cr=cr+1

cr=cr+1
cr=cr+1

## - Table 3
worksheet.merge_range(cr, 0, cr, 11, 'Обобщена справка', merge_bold)
cr=cr+1
worksheet.merge_range(cr, 2, cr, 14, 'в ЛЕВА с вкл. ДДС', header_format)
cr=cr+1
c3 = conn.cursor()
c3.execute(sql_total,  THE_DATE = THEDATE, DATE_FROM = DATEFROM, DATE_TILL = DATETILL  )
print('T3 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
hds = ('',
       '',
       'Обща стойност на направени резервации на ',
       'Обща платена сума по направени резервации на ',
       'Обща стойност на анулирани резервации на ',
       '',
       'Обща стойност на анулирани резервации за Сезон 2021 с натрупване към ',
       '',
       'Обща стойност на активни резервации за Сезон 2021 с натрупване и приспадане на анулираните към ',
       '',
       'Обща платена сума от активни резервации за Сезон 2021 с натрупване и приспадане на сумите за възстановяване към ',
       '',
       '',
       'Обща сума за възстановяване на предплатени анулирани резервации на ')
worksheet.merge_range(cr, 0, cr, 1, '', header_format)
worksheet.write(cr, 2, hds[2] + THEDATE_SHORT, header_format)
worksheet.write(cr, 3, hds[3] + THEDATE_SHORT, header_format)
worksheet.merge_range(cr, 4, cr, 5, hds[4] + THEDATE_SHORT, header_format)
worksheet.merge_range(cr, 6, cr, 7, hds[6] + THEDATE_SHORT, header_format)
worksheet.merge_range(cr, 8, cr, 9, hds[8] + THEDATE_SHORT, header_format)
worksheet.merge_range(cr, 10, cr, 12, hds[10] + THEDATE_SHORT, header_format)
worksheet.merge_range(cr, 13, cr, 14, hds[13] + THEDATE_SHORT, header_format)
#worksheet.write(cr, 13, hds[13], header_format)
cr=cr+1
r1 = cr
for row in c3:
    worksheet.merge_range(cr, 0, cr, 1, row[0], border_currency)
    worksheet.write(cr, 2, row[2] , border_currency)
    worksheet.write(cr, 3, row[3] , border_currency)
    worksheet.merge_range(cr, 4, cr, 5, row[4] , border_currency)
    worksheet.merge_range(cr, 6, cr, 7, row[6] , border_currency)
    worksheet.merge_range(cr, 8, cr, 9, row[8] , border_currency)
    worksheet.merge_range(cr, 10, cr, 12, row[10] , border_currency)
    worksheet.merge_range(cr, 13, cr, 14, '', border_currency)

    cr=cr+1
r2 = cr-1
worksheet.write(cr, 1, 'Общо', bold)
sumCol=2
worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=3
worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=4
worksheet.merge_range(cr, sumCol, cr, sumCol+1, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=6
worksheet.merge_range(cr, sumCol, cr, sumCol+1, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=8
worksheet.merge_range(cr, sumCol, cr, sumCol+1, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=10
worksheet.merge_range(cr, sumCol, cr, sumCol+2, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
sumCol=13
worksheet.merge_range(cr, sumCol, cr, sumCol+1, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency_bold)
#if r2-r1 > 0:
#    sumCols = (2,3,4,6,8,10,13)
#    for sumCol in sumCols:
#        worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', border_currency)
#    cr=cr+1

cr=cr+1
cr=cr+1

worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
cr=cr+1
worksheet.write(cr, 1, 'Изготвили: ')

conn.close()
worksheet.set_column(2, 2, 14)
worksheet.set_column(7, 7, 14)
worksheet.set_column(8, 8, 11)
worksheet.set_column(19,19, 11)
workbook.close()

print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^ResvDaily.+\.xlsx', f)]
for filename in files:
    #filename = "C:/Users/Parsing/Downloads/VAR41030_2020-12-05_07-55_BookingData.csv"
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
with smtplib.SMTP(mailserver) as server:
    #server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





