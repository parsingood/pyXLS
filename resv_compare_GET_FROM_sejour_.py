
opera_arrival_from = "to_date('2022-03-01','YYYY-MM-DD')"
#opera_arrival_from = 'current_date'
sejour_arrival_from = "'2023-03-01'"
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
    try:
        Pcursor.execute('''
        insert resv_sej(Turop,Voucher,Sira,SubVoucher,Bolge,Otel,GirisTarihi,CikisTarihi,Gun,Oda_OdaTipi,
        Pans,Yet,Coc,Beb,OdaSayi,RezStat,RezType,Conf,OrjOtel)
        select ?,?,?,?,?,?,?,?,?,?,
               ?,?,?,?,?,?,?,?,?
        ''' 
        , row.Turop,row.Voucher,row.Sira,row.SubVoucher,row.Bolge,row.Otel,row.GirisTarihi,row.CikisTarihi,row.Gun,row.Oda_OdaTipi
        ,row.Pans,row.Yet,row.Coc,row.Beb,row.OdaSayi,row.RezStat,row.RezType,row.Conf,row.OrjOtel )

        Pcursor.commit()
    except:
        print(row.Turop,row.Voucher,row.Sira,row.SubVoucher,row.Bolge,row.Otel,row.GirisTarihi,row.CikisTarihi,row.Gun,row.Oda_OdaTipi,row.Pans,row.Yet,row.Coc,row.Beb,row.OdaSayi,row.RezStat,row.RezType,row.Conf,row.OrjOtel)

Pcursor.execute('''
update TableLastUpdates set LastUpdate = CURRENT_TIMESTAMP where TableName  ='resv_sej'
'''  )
Pcursor.commit()



