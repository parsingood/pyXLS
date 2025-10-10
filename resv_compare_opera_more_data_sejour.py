
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
cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
Oconn = cx_Oracle.connect(user=r'OPERA', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'



Ocursor = Oconn.cursor()

Ocursor.execute('''

SELECT  R.RESV_STATUS, R.RESORT, RT.LABEL RT, RTC.LABEL RTC 
,  R.CONFIRMATION_NO CONFIRM_NO
,  R.CUSTOM_REFERENCE CUSTOM_REFERENCE
, E.PHYSICAL_QUANTITY RMS, EN.ADULTS AD, EN.CHILDREN CH
, EN.RATE_CODE 
, R.TRUNC_END_DATE-R.TRUNC_BEGIN_DATE STAY 
, TO_CHAR(R.TRUNC_BEGIN_DATE,'DD.MM.YYYY') ARRIVAL
, TO_CHAR(R.TRUNC_END_DATE,'DD.MM.YYYY') DEPARTURE 
, NVL(N.LAST,'') LAST_NAME
, NVL(N.FIRST,'') FIRST_NAME
, SO.UDFC22 MARKET, TO_CHAR(R.UDFD07,'DD.MM.YY HH24:MI:SS') LAST_CHKD
, R.UDFC30 ORIG
, SUBSTR(NVL(R.UDFC30, R.RESORT),1,3) HOR
, SUBSTR(EN.RATE_CODE,6,3) HRT
, SO.COMPANY SOURCE_NAME
, TO_CHAR(R.INSERT_DATE,'DD.MM.YYYY HH24:MI:SS') INSERT_DATE,
, TO_CHAR(R.UDFD15,'DD.MM.YYYY') BOOK_DATE 
, TO_CHAR(R.UPDATE_DATE,'DD.MM.YYYY HH24:MI:SS') UPDATE_DATE 
, SO.UDFC21 AGENT
 FROM OPERA.RESERVATION_NAME R   
 JOIN OPERA.NAME N ON N.NAME_ID = R.NAME_ID  JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN ON EN.RESORT = R.RESORT       AND EN.RESV_NAME_ID=R.RESV_NAME_ID AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    LEFT JOIN OPERA.NAME SO ON SO.NAME_ID = EN.SOURCE_ID  LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E ON E.RESORT = R.RESORT AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE    AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT ON RT.RESORT = R.RESORT AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RTC ON RTC.RESORT = R.RESORT AND RTC.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY LEFT JOIN OPERA.APPLICATION$_USER U ON U.APP_USER_ID = R.INSERT_USER 
 LEFT JOIN RESORT H1 ON H1.RESORT=R.RESORT
 LEFT JOIN RESORT H2 ON H2.RESORT=R.UDFC30
 LEFT JOIN RESORT$_ROOM_CATEGORY T2 ON T2.RESORT=R.UDFC30 AND T2.LABEL = RTC.LABEL 
  WHERE (R.RESV_STATUS <> 'CANCELLED') AND (R.RESV_STATUS <> 'NO SHOW') 
   AND NVL(RT.PSEUDO_YN ,'N')='N'
   AND (EN.ADULTS + EN.CHILDREN > 0) 
 AND R.TRUNC_END_DATE > current_date 
 AND R.TRUNC_BEGIN_DATE <= current_date + 600 
 AND R.RESORT IN ('DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG', 'GOR')

''')





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
    from RezOtel r
    join Musteri m on m.Turop=r.Turop
    and m.Voucher=r.Voucher and m.Sira = 1
    where r.[GirisTarihi] >= CURRENT_TIMESTAMP 
''' )
Srows = Scursor.fetchall()
for row in Srows:

    Pcursor.execute('''
        insert resv_sej(Turop,Voucher,Sira,SubVoucher,Bolge,
		Otel,GirisTarihi,CikisTarihi,Gun,Oda_OdaTipi,
		Pans,Yet,Coc,Beb,OdaSayi,RezStat,RezType,Conf,OrjOtel)
        select ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    ''' , row.Turop,row.Voucher,row.Sira,row.SubVoucher,row.Bolge,row.Otel,row.GirisTarihi,row.CikisTarihi,row.Gun,row.Oda_OdaTipi,row.Pans,row.Yet,row.Coc,row.Beb,row.OdaSayi,row.RezStat,row.RezType,row.Conf,row.OrjOtel )
    Pcursor.commit()

########################################## Odafiy_Board
Pcursor.execute('''
    delete from  Odafiy_Board
'''  )
Pcursor.commit()
Scursor.execute('''
    select t.Turop, t.Otel, t.pans +'#'+ p.Tanim board
	from Odafiy t
	left join Pansiyon p on p.Kodu=t.Pans
	where t.Sezno='S22'
	group by t.Turop,t.Otel, t.pans, p.Tanim
	order by t.Turop,t.Otel, t.pans
''' )
Srows = Scursor.fetchall()
for row in Srows:

    Pcursor.execute('''
        insert Odafiy_Board(Turop,Otel,board)
        select ?,?,?
    ''' , row.Turop,row.Otel,row.board )
    Pcursor.commit()

########################################## Otel
Pcursor.execute('''
    delete from  [Shuttle].[dbo].Otel
'''  )
Pcursor.commit()
Scursor.execute('''
    select Otel, Adi  from Otel
	where Adi is not null
    group by Otel, Adi
''' )
Srows = Scursor.fetchall()
for row in Srows:

    Pcursor.execute('''
        insert [Shuttle].[dbo].Otel(Otel, Adi)
        select ?,?
    ''' , row.Otel, row.Adi )
    Pcursor.commit()

####################################################################################
####################################################################################

########################################## Otel, ParamID=1
Pcursor.execute('''
     insert into Parsing.dbo.[CL_ParamValues](
[PMS_ServerID],[ParamID],[CL_ID_HOTEL],[CL_ID],[CL_DESCRIPTION],[CL_IsActive]
)
  select 10, 1, -1, x.PMS_HotelID, Otel+'#'+Adi ,1
  from
(SELECT [Otel],Adi,h.PMS_HotelID FROM [Shuttle].[dbo].[Otel] o
join Parsing.dbo.PMS_Hotels h on h.Code=o.[Otel] and PMS_ServerID=10
) x  
left join (
  SELECT code, [CL_DESCRIPTION]
  FROM Parsing.dbo.[CL_ParamValues] v
  left join Parsing.dbo.PMS_Hotels h on h.PMS_HotelID=v.CL_ID
  where v.[PMS_ServerID]=10 and v.ParamID=1
  and [CL_IsActive] = 1
  group by code ,CL_DESCRIPTION
) y on x.Otel collate SQL_Latin1_General_CP1_CI_AS =y.Code
 where CL_DESCRIPTION is null or  Otel+'#'+Adi <>CL_DESCRIPTION

'''  )
Pcursor.commit()


########################################## Odafiy_Roomtype, ParamID=4


Pcursor.execute('''
     select max(CL_ID) max_CL_ID from Parsing.dbo.CL_ParamValues
 where PMS_ServerID=10 and ParamID=4
''' )
Prows = Pcursor.fetchall()
max_CL_ID = Prows[0].max_CL_ID
Pcursor.commit()

Qconn = pyodbc.connect(PconnStr)
Qcursor = Qconn.cursor()


Pcursor.execute('''
select  h.PMS_HotelID, x.room_type
from (  SELECT [Otel],[room_type]
  FROM [Shuttle].[dbo].[Odafiy_Roomtype]
  group by [Otel] ,[room_type]
) x 
join Parsing.dbo.PMS_Hotels h on h.Code=x.Otel 
collate SQL_Latin1_General_CP1_CI_AS and h.[PMS_ServerID]=10 
left join (
 SELECT h.code
,[CL_DESCRIPTION]
  FROM [Parsing].[dbo].[CL_ParamValues] v
  left join Parsing.dbo.PMS_Hotels h on h.PMS_HotelID=v.CL_ID_HOTEL
  where v.[PMS_ServerID]=10 and v.ParamID=4
  and [CL_IsActive] = 1
  group by code ,CL_DESCRIPTION
  ) y on x.Otel collate SQL_Latin1_General_CP1_CI_AS =y.Code
  and x.room_type collate SQL_Latin1_General_CP1_CI_AS=y.CL_DESCRIPTION
where y.CL_DESCRIPTION is null
order by x.Otel, x.room_type
''' )
Prows = Pcursor.fetchall()
for prow in Prows:
    max_CL_ID = max_CL_ID + 1
    Qcursor.execute('''
    insert into Parsing.dbo.[CL_ParamValues](
    [PMS_ServerID],[ParamID],[CL_ID_HOTEL],[CL_ID],[CL_DESCRIPTION],[CL_IsActive]
    ) select 10,4,?,?,?,1
    ''' , prow.PMS_HotelID, max_CL_ID, prow.room_type)
    Qcursor.commit()

Pcursor.commit()

########################################## Odafiy_Board, ParamID=5


Pcursor.execute('''
     select max(CL_ID) max_CL_ID from Parsing.dbo.CL_ParamValues
 where PMS_ServerID=10 and ParamID=5
''' )
Prows = Pcursor.fetchall()
max_CL_ID = Prows[0].max_CL_ID
Pcursor.commit()

Qconn = pyodbc.connect(PconnStr)
Qcursor = Qconn.cursor()


Pcursor.execute('''
select  h.PMS_HotelID, x.board
from (  SELECT [Otel],[board]
  FROM [Shuttle].[dbo].[Odafiy_Board]
  group by [Otel] ,[board]
) x 
join Parsing.dbo.PMS_Hotels h on h.Code=x.Otel 
collate SQL_Latin1_General_CP1_CI_AS and h.[PMS_ServerID]=10 
left join (
 SELECT h.code
,[CL_DESCRIPTION]
  FROM [Parsing].[dbo].[CL_ParamValues] v
  left join Parsing.dbo.PMS_Hotels h on h.PMS_HotelID=v.CL_ID_HOTEL
  where v.[PMS_ServerID]=10 and v.ParamID=5
  and [CL_IsActive] = 1
  group by code ,CL_DESCRIPTION
  ) y on x.Otel collate SQL_Latin1_General_CP1_CI_AS =y.Code
  and x.board collate SQL_Latin1_General_CP1_CI_AS=y.CL_DESCRIPTION
where y.CL_DESCRIPTION is null
order by x.Otel, x.board
''' )
Prows = Pcursor.fetchall()
for prow in Prows:
    max_CL_ID = max_CL_ID + 1
    Qcursor.execute('''
    insert into Parsing.dbo.[CL_ParamValues](
    [PMS_ServerID],[ParamID],[CL_ID_HOTEL],[CL_ID],[CL_DESCRIPTION],[CL_IsActive]
    ) select 10,5,?,?,?,1
    ''' , prow.PMS_HotelID, max_CL_ID, prow.board)
    Qcursor.commit()

Pcursor.commit()