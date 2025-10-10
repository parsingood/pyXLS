
opera_arrival_from = "to_date('2025-03-01','YYYY-MM-DD')"
#opera_arrival_from = 'current_date'
sejour_arrival_from = "'2025-03-01'"
#sejour_arrival_from = 'CURRENT_TIMESTAMP'

import pandas as pd
import pyodbc 
import json
import imaplib
import base64
import os
import email
import datetime
from email.header import decode_header
from email.message import EmailMessage
from win32com import client as wc
import re
import base64
import quopri
from  os.path import splitext
import io
import csv
import sys
import docx2txt
import codecs
import win32com.client
import docx
import PyPDF2
import pikepdf
import chardet    
import subprocess
import traceback
import cx_Oracle

# Sejour - Database
#  "Data Source=77.85.202.44;Initial Catalog=ALBENASEJOUR;User ID=sa;Password=tDR*WXB9'K\Nl+T?!=I&46yk"
SconnStr = "Driver={SQL Server Native Client 11.0};Server=77.85.202.44;Database=ALBENASEJOUR;UID=sa;PWD=tDR*WXB9'K\\Nl+T?!=I&46yk"
Sconn = pyodbc.connect(SconnStr)
Scursor = Sconn.cursor()

# Parsing - Database
#  "Data Source=HOTELAGENT\SQLexpress;Initial Catalog=Parsing;User ID=onlineParsingMachime;Password=12A-dd7e34%3482*dwk^hoeDif-su2112@41!1G+Gjudu#643Edf"
PconnStr = "Driver={SQL Server Native Client 11.0};Server=HOTELAGENT\SQLEXPRESS;Database=Shuttle;UID=onlineParsingMachime;PWD=12A-dd7e34%3482*dwk^hoeDif-su2112@41!1G+Gjudu#643Edf"
Pconn = pyodbc.connect(PconnStr)
Pcursor = Pconn.cursor()


# OPERA - database
cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
Oconn = cx_Oracle.connect(user=r'OPERA', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
Ocursor = Oconn.cursor()


Pcursor.execute('''
    delete from  resv_opera
'''  )
Pcursor.commit()

Ocursor.execute('''

SELECT  R.RESV_STATUS
, R.RESORT
, RT.LABEL RT
, RTC.LABEL RTC 
,  R.CONFIRMATION_NO CONFIRM_NO
,  R.CUSTOM_REFERENCE CUSTOM_REFERENCE
, E.PHYSICAL_QUANTITY RMS
, EN.ADULTS AD
, EN.CHILDREN CH
, EN.RATE_CODE 

, R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE STAY 
, R.TRUNC_BEGIN_DATE ARRIVAL
, R.TRUNC_END_DATE DEPARTURE 
, NVL(N.LAST,'') LAST_NAME
, NVL(N.FIRST,'') FIRST_NAME
, SO.UDFC22 MARKET
, R.UDFD07 LAST_CHKD
, R.UDFC30 ORIG
, SUBSTR(NVL(R.UDFC30, R.RESORT),1,3) HOR
, SUBSTR(EN.RATE_CODE,6,3) HRT

, SO.COMPANY SOURCE_NAME
, R.UDFD15 BOOK_DATE 
, SO.UDFC21 AGENT

 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT       
 AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  
 LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT 
 AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY 
 LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY 
 LEFT JOIN OPERA.APPLICATION$_USER U ON U.APP_USER_ID = R.INSERT_USER 
 LEFT JOIN RESORT H1 ON H1.RESORT=R.RESORT
 LEFT JOIN RESORT H2 ON H2.RESORT=R.UDFC30
 LEFT JOIN RESORT$_ROOM_CATEGORY T2 ON T2.RESORT=R.UDFC30 AND T2.LABEL = RTC.LABEL 
  WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   AND NVL(RT.PSEUDO_YN ,'N')='N'
   AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND R.TRUNC_END_DATE > ''' + opera_arrival_from + ''' 
 AND R.RESORT IN ('DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 
 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 
 'VMG', 'GOR')

''')
# AND R.TRUNC_BEGIN_DATE <= current_date + 600 
Orows = Ocursor.fetchall()
for row in Orows:

    Pcursor.execute('''
        insert resv_opera(RESV_STATUS,RESORT,RT,RTC,CONFIRM_NO,CUSTOM_REFERENCE,RMS,AD,CH,RATE_CODE,
		STAY,ARRIVAL,DEPARTURE,LAST_NAME,FIRST_NAME,MARKET,LAST_CHKD,ORIG,HOR,HRT,
		SOURCE_NAME,BOOK_DATE,AGENT)
        select ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?  ,?,?,?
    ''' ,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]
        ,row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22]
    )
 #   row.RESV_STATUS,row.RESORT,row.RT,row.RTC,row.CONFIRM_NO,row.CUSTOM_REFERENCE,row.RMS,row.AD,row.CH,row.RATE_CODE,
	#row.STAY,row.ARRIVAL,row.DEPARTURE,row.LAST_NAME,row.FIRST_NAME,row.MARKET,row.LAST_CHKD,row.ORIG,row.HOR,row.HRT,row.SOURCE_NAME,row.BOOK_DATE )

    Pcursor.commit()

Pcursor.execute('''
update TableLastUpdates set LastUpdate = CURRENT_TIMESTAMP where TableName = 'resv_opera'
'''  )
Pcursor.commit()

########################################## resv_sej
Pcursor.execute('''
    delete from  resv_sej
'''  )
Pcursor.commit()
Scursor.execute('''
    SELECT r.[Turop]
    ,r.[Voucher] 
    ,r.[Sira]
    , m.SubVoucher
    ,r.[Bolge]
	
    ,r.[Otel]
    ,r.[GirisTarihi]
    ,r.[CikisTarihi]
    ,r.[Gun]
    ,r.[Oda]
    + ' ' + r.[OdaTipi] Oda_OdaTipi
	
    ,r.[Pans]
    ,r.[Yet]
    + r.[ExtB] Yet
    ,r.[Coc]
    ,r.[Beb]
    ,r.[OdaSayi]
    ,r.[RezStat]
    ,r.[RezType]
    ,r.[Conf]
    ,r.[OrjOtel]
    from RezOtel r
    join Musteri m on m.Turop=r.Turop
    and m.Voucher=r.Voucher and m.Sira = 1
    where r.[GirisTarihi] >= ''' + sejour_arrival_from + ''' 
''' )
Srows = Scursor.fetchall()
for row in Srows:

    Pcursor.execute('''
	insert resv_sej(Turop,Voucher,Sira,SubVoucher,Bolge,Otel,GirisTarihi,CikisTarihi,Gun,Oda_OdaTipi,
	Pans,Yet,Coc,Beb,OdaSayi,RezStat,RezType,Conf,OrjOtel)
	select ?,?,?,?,?,?,?,?,?,?,
		   ?,?,?,?,?,?,?,?,?
    ''' 
    , row.Turop,row.Voucher,row.Sira,row.SubVoucher,row.Bolge,row.Otel,row.GirisTarihi,row.CikisTarihi,row.Gun,row.Oda_OdaTipi
    ,row.Pans,row.Yet,row.Coc,row.Beb,row.OdaSayi,row.RezStat,row.RezType,row.Conf,row.OrjOtel )
    Pcursor.commit()

Pcursor.execute('''
update TableLastUpdates set LastUpdate = CURRENT_TIMESTAMP where TableName  ='resv_sej'
'''  )
Pcursor.commit()



