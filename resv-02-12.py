import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
subject = "Reservations daily report - 25.12"
body = "Reservations daily report  - 25.12"
sender_email = "ivanm@albena.bg"
to_email ="mtodorova@albena.bg"
receiver_email = ["mtodorova@albena.bg","marinela.tsaneva@albena.bg","maya.lazarova@albena.bg","ivanm@albena.bg"]
#to_email ="ivanm@albena.bg"
#receiver_email = ["ivanm@albena.bg"]
#to_email ="ivan.mihaylov.bg@gmail.com"
#receiver_email = ["ivan.mihaylov.bg@gmail.com"]

#password = ""
mailserver = "mail.albena.bg"
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
lastay = today - datetime.timedelta(365)
otherstay = today - datetime.timedelta(365+365+365) #2019
THEDATE = today.strftime("%d.%m.%Y")
THEDATE_SHORT = today.strftime("%d.%m.%y")

month_day_from = (3,1) # (month, day)
month_day_till = (10,31) # (month, day)
first_week_day = (1,3) # (month, day)
new_year_this = "22/23"
new_year_last = "21/22"


SQL1='''
SELECT 
 HOTEL
, SOURCE_NAME
, SUM(RMS) ROOMS
, SUM(OVNTS) OVNTS
 , SUM(AD) AD
 , SUM(CH) CH
 , SUM(AD)+SUM(CH) PAX
 FROM ( 
  SELECT 
 R.RESORT HOTEL
 , E.PHYSICAL_QUANTITY RMS, EN.ADULTS AD, EN.CHILDREN CH
 , (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) OVNTS 
 , SO.COMPANY SOURCE_NAME
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT       
 AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   AND NVL(RT.PSEUDO_YN ,'N')='N'
   AND (EN.ADULTS + EN.CHILDREN > 0) 
   AND R.TRUNC_END_DATE > TO_DATE('25122022','DDMMYYYY')
   AND R.TRUNC_BEGIN_DATE<= TO_DATE('25122022','DDMMYYYY')
 AND R.RESORT = '@hotel'
 AND SO.COMPANY NOT IN (
  'KT-SPECIAL GUESTS',
  'CONTRACTORS','STF-ERROR1','XX'
  )
) X 
 GROUP BY  HOTEL , SOURCE_NAME
order by  HOTEL , SOURCE_NAME
'''

pass



SQL2 = '''
SELECT 'on ' || to_char(INSERT_DATE,'dd.mm') "Date",

CASE WHEN FLG_RL > 0 THEN '+' || TO_CHAR(FLG_RL) ELSE ' ' END FLG_RL, SUM(FLG_RL) OVER (ORDER BY INSERT_DATE) FLG_RL_T,
CASE WHEN FLG_RT > 0 THEN '+' || TO_CHAR(FLG_RT) ELSE ' ' END FLG_RT, SUM(FLG_RT) OVER (ORDER BY INSERT_DATE) FLG_RT_T,
CASE WHEN FLG_PL > 0 THEN '+' || TO_CHAR(FLG_PL) ELSE ' ' END FLG_PL, SUM(FLG_PL) OVER (ORDER BY INSERT_DATE) FLG_PL_T, 
CASE WHEN FLG_PT > 0 THEN '+' || TO_CHAR(FLG_PT) ELSE ' ' END FLG_PT, SUM(FLG_PT) OVER (ORDER BY INSERT_DATE) FLG_PT_T 
FROM (
select INSERT_DATE,

SUM(case when HOTEL = 'FLG' THEN RL ELSE 0 END) FLG_RL,
SUM(case when HOTEL = 'FLG' THEN PL ELSE 0 END) FLG_PL,
SUM(case when HOTEL = 'FLG' THEN RT ELSE 0 END) FLG_RT,
SUM(case when HOTEL = 'FLG' THEN PT ELSE 0 END) FLG_PT
from(
SELECT NVL(TY.INSERT_DATE,LY.INSERT_DATE) INSERT_DATE
,NVL(TY.HOTEL,LY.HOTEL) HOTEL
,NVL(LY.ROOMS,0)   RL
,NVL(LY.PAX,0)  PL
,NVL(TY.ROOMS,0 ) RT
,NVL(TY.PAX,0)  PT
FROM 
(
SELECT INSERT_DATE+365 INSERT_DATE,
 HOTEL
, SUM(RMS) ROOMS
, SUM(AD)+SUM(CH) PAX
 FROM ( 
  SELECT TRUNC(R.INSERT_DATE,'DD') INSERT_DATE,
 R.RESORT HOTEL
 , E.PHYSICAL_QUANTITY RMS, EN.ADULTS AD, EN.CHILDREN CH
 , (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) OVNTS 
 , SO.COMPANY SOURCE_NAME
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  
 JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT       
 AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   AND NVL(RT.PSEUDO_YN ,'N')='N'
   AND (EN.ADULTS + EN.CHILDREN > 0) 
   AND R.TRUNC_END_DATE > TO_DATE('25122022','DDMMYYYY')
   AND R.TRUNC_BEGIN_DATE<= TO_DATE('25122022','DDMMYYYY')
   AND R.RESORT IN ( 'FLG'))
AND SO.COMPANY NOT IN (
  'KT-SPECIAL GUESTS',
  'CONTRACTORS','STF-ERROR1','XX'
  )
) X 
 GROUP BY INSERT_DATE,  HOTEL
) LY
 FULL JOIN
 (
SELECT INSERT_DATE,
 HOTEL
, SUM(RMS) ROOMS
, SUM(AD)+SUM(CH) PAX
 FROM ( 
  SELECT TRUNC(R.INSERT_DATE,'DD') INSERT_DATE,
   R.RESORT HOTEL
   , E.PHYSICAL_QUANTITY RMS, EN.ADULTS AD, EN.CHILDREN CH
   , (EN.ADULTS + EN.CHILDREN) * (R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE) OVNTS 
   , SO.COMPANY SOURCE_NAME
   FROM OPERA.RESERVATION_NAME R   
   JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  
   JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT       
   AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
   LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
   LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
   AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
   WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
     AND NVL(RT.PSEUDO_YN ,'N')='N'
     AND (EN.ADULTS + EN.CHILDREN > 0) 
   AND R.TRUNC_END_DATE > TO_DATE('25122022','DDMMYYYY')
   AND R.TRUNC_BEGIN_DATE<= TO_DATE('25122022','DDMMYYYY')
   AND R.RESORT IN ( 'FLG')
  AND SO.COMPANY NOT IN (
    'KT-SPECIAL GUESTS',
    'CONTRACTORS','STF-ERROR1','XX'
    )
  ) X 
  GROUP BY INSERT_DATE,  HOTEL
) TY ON TY.HOTEL=LY.HOTEL AND TY.INSERT_DATE = LY.INSERT_DATE
) Y
GROUP by Y.INSERT_DATE
)
order by INSERT_DATE
'''

current_time = datetime.datetime.now()
today = datetime.date.today()
yesterday = today - datetime.timedelta(1)
dt_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
workbook = xlsxwriter.Workbook('C:/test/resv-25-12-'+dt_string+'.xlsx')
bold = workbook.add_format({'bold': True})

ddmmyy_format = workbook.add_format({'num_format': 'dd.mm.yy'})

main =workbook.add_format({
})

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

merge_bold_border = workbook.add_format({
    'bold':     True,
    'align':    'center',
    'valign':   'vcenter',
	'border':   1,
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
border =workbook.add_format({
    'border':   1,
})
border_plus =workbook.add_format({
    'bold':     True,
    'align':    'right',
    'color': '#0000DD',
	'border':   1,
})
bold_right =workbook.add_format({
    'bold':     True,
    'align':    'right',
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



conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
cursor = conn.cursor()


################ - DoWorksheet 2

cols_with_sum = [2,3,4,5,6]

worksheet = workbook.add_worksheet(name="today")
cr = 0

## - Table 1

worksheet.merge_range(cr, 0, cr, 6, 'резервациите за 25.12 '
 + ' към ' + yesterday.strftime("%d.%m.%Y") 
 , merge_bold  )


cr+=2
worksheet.merge_range(cr, 0, cr, 6, 'Paradise Blue ',merge_bold )
cr+=1

conn = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
cursor = conn.cursor()
s1=SQL1.replace('@hotel','FLG')
cursor.execute(s1)
total1={c:0 for c in cols_with_sum}
cl = 0
c = 0
hdname=[]
for hd in [i[0] for i in cursor.description]:
	worksheet.write(cr, c, hd, merge_bold)
	c+=1
	cl=cl+1
cr=cr+1
r1 = cr
for row in cursor:
	cl = 0
	c = 0
	for col in row:
		worksheet.write(cr, c, col, main)
		if c in total1:
			total1[c] += col
		c+=1
		cl=cl+1
	cr=cr+1
r2 = cr-1
if r2-r1 > 0:
	r_tot1 = cr
	for sumCol in cols_with_sum:
		worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold, total1[sumCol]) 
#		worksheet.write_number(cr, sumCol, total1[sumCol] , bold)
		worksheet.write(cr, sumCol, total1[sumCol] , bold)
	cr=cr+1

cr=cr+2

worksheet.merge_range(cr, 0, cr, 6, 'Flamingo Grand ',merge_bold )
cr+=1


# s2=SQL1.replace('@hotel','FLG')
# cursor.execute(s2)
# total2={c:0 for c in cols_with_sum}
# cl = 0
# c = 0
# hdname=[]
# for hd in [i[0] for i in cursor.description]:
	# worksheet.write(cr, c, hd, merge_bold)
	# c+=1
	# cl=cl+1
# cr=cr+1
# r1 = cr
# for row in cursor:
	# cl = 0
	# c = 0
	# for col in row:
		# worksheet.write(cr, c, col, main)
		# if c in total2:
			# total2[c] += col
		# c+=1
		# cl=cl+1
	# cr=cr+1
# r2 = cr-1
# if r2-r1 > 0:
	# r_tot2 = cr
	# for sumCol in cols_with_sum:
		# worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold, total2[sumCol]) 
##		worksheet.write_number(cr, sumCol, total2[sumCol] , bold)
		# worksheet.write(cr, sumCol, total2[sumCol] , bold)
	# cr=cr+1

cr=cr+1

worksheet.write(cr, 1, 'Total:', bold_right)
for sumCol in cols_with_sum:
	worksheet.write_formula(cr, sumCol, '='+ xl_rowcol_to_cell(r_tot1, sumCol)  +'', bold, total1[sumCol] ) 
#	worksheet.write_number(cr, sumCol, total1[sumCol] + total2[sumCol] , bold)
	worksheet.write(cr, sumCol, total1[sumCol]  , bold)
cr=cr+2

worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
cr=cr+1
worksheet.write(cr, 1, 'Изготвил: Ив.Михайлов')


for w in [[0,7],[1,20],[2,9],[3,9],[4,7],[5,7],[5,9]]:
	worksheet.set_column(w[0], w[0], w[1])

#worksheet.set_column(0, 0, 5)










################ - DoWorksheet 1

cols_ignore = []
cols_with_sum = [] # list(range(1, 2*(days+2)+1))

w1=4
w2=7

cols = {
'DOR_RL':{'w':w1,'h':'21','f':border_plus},
'DOR_RL_T':{'w':w2,'h':'rooms','f':border},
'DOR_RT':{'w':w1,'h':'22','f':border_plus},
'DOR_RT_T':{'w':w2,'h':'rooms','f':border},

'DOR_PL':{'w':w1,'h':'21','f':border_plus},
'DOR_PL_T':{'w':w2,'h':'pax','f':border},
'DOR_PT':{'w':w1,'h':'22','f':border_plus},
'DOR_PT_T':{'w':w2,'h':'pax','f':border},

'FLG_RL':{'w':w1,'h':'21','f':border_plus},
'FLG_RL_T':{'w':w2,'h':'rooms','f':border},
'FLG_RT':{'w':w1,'h':'22','f':border_plus},
'FLG_RT_T':{'w':w2,'h':'rooms','f':border},

'FLG_PL':{'w':w1,'h':'21','f':border_plus},
'FLG_PL_T':{'w':w2,'h':'pax','f':border},
'FLG_PT':{'w':w1,'h':'22','f':border_plus},
'FLG_PT_T':{'w':w2,'h':'pax','f':border},

}

#worksheet = workbook.add_worksheet(name="compare")
#cr = 0

## - Table 1
# worksheet.merge_range(cr, 0, cr, 17, 'Движение на резервациите за нова година '
 # + new_year_this + ' спрямо ' + new_year_last
 # + ' към ' + yesterday.strftime("%d.%m.%Y") 
 # , merge_bold  )

# cr+=2
# worksheet.merge_range(cr, 1, cr, 8, 'Paradise Blue ' , merge_bold_border)
# worksheet.merge_range(cr, 9, cr, 16, 'Flamingo Grand ' , merge_bold_border)
# cr+=1

# cursor.execute(SQL2)

# print('T1 executed at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

# cl = 0
# c = 0
# hdname=[]
# for hd in [i[0] for i in cursor.description]:
	# if cl not in cols_ignore :
		# hdname.append(hd)
		# if hd in cols.keys():
			# cols[hd]['c'] = c
		# worksheet.write(cr, c, cols[hd]['h'] if hd in cols.keys() else hd, header_format)
		# c+=1

	# cl=cl+1
# cr=cr+1
# r1 = cr
# for row in cursor:
	# cl = 0
	# c = 0
	# for col in row:
		# if cl not in cols_ignore :
			# worksheet.write(cr, c, col, cols[hdname[c]]['f'] if len(hdname) > c and hdname[c] in cols.keys() else border )
			# c+=1
		# cl=cl+1
	# cr=cr+1
# r2 = cr-1
# if r2-r1 > 0:
	
	# for sumCol in cols_with_sum:
		# worksheet.write_formula(cr, sumCol, '=SUM('+ xl_rowcol_to_cell(r1, sumCol) +':'+  xl_rowcol_to_cell(r2, sumCol) +')', bold) 
	# cr=cr+1

# cr=cr+1


# cr=cr+1
# cr=cr+1

# worksheet.write(cr, 1, 'Дата: ' + TODAY_STR)
# cr=cr+1
# worksheet.write(cr, 1, 'Изготвил: Ив.Михайлов')


# for hd in cols:
	# if hd in cols.keys():
##		print(cols[hd]['c'])
		# if 'w' in cols[hd].keys():
			# worksheet.set_column(cols[hd]['c'], cols[hd]['c'], cols[hd]['w'])


# print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')






# print('Excel generated at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

conn.close()
workbook.close()


# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^resv-25-12.+\.xlsx', f)]
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
with smtplib.SMTP(mailserver) as server:
    #server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





