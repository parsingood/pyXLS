import os
import re
import datetime 
import cx_Oracle
from itertools import product

path = "C:/OPERA/"

def pax_variants(
    min_pax = 0,  # Минимален общ брой хора
    max_pax = 0,  # Максимален общ брой хора
    min_ad = 0,   # Минимален брой възрастни
    max_ad = 0,   # Максимален брой възрастни
    min_ch = 0,   # Минимален брой деца
    max_ch = 0,   # Максимален брой деца
    adult_age = 13, # Минимален години на възрастни
    gchild_age = 13, # Минимален години на порасналите деца
    child_age = 2 # Минимален години на дете
):
    combinations = []
    if adult_age == gchild_age :
        # Генериране на всички комбинации на възрастни и деца
        for adults, children in product(
            range(min_ad, max_ad + 1), 
            range(min_ch, max_ch + 1)
        ):
            if min_pax <= adults + children <= max_pax:
                combinations.append ([adult_age, gchild_age, child_age,  adults, 0, children, 0] )
                # [13,13,2,   2,0,1,0],
    else:
        # Генериране на всички комбинации на възрастни и деца
        for adults, children in product(
            range(min_ad, max_ad + 1), 
            range(min_ch, max_ch + 1)
        ):
            if min_pax <= adults + children <= max_pax:
                for gchildren in range(children + 1):
                    combinations.append ([
                        adult_age, gchild_age, child_age,  
                        adults, gchildren, children-gchildren, 0
                    ] )





    return combinations










print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
conn = cx_Oracle.connect(user=r'OPERA', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'

today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")



yesterday = today - datetime.timedelta(days=365) # days=7 
THEDATE = yesterday.strftime("%d.%m.%Y")
THEDATE_SHORT = yesterday.strftime("%d.%m.%y")

DATEFROM =  yesterday.strftime("%d.%m.%Y")
DATETILL =  today.strftime("%d.%m.%Y")


HOTELS = '''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 
'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 
'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 
'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 
'PAN', 'VMG'
'''

HOTELS="'FLG'"

sql="""
SELECT RATE_CODE,RESORT,BEGIN_DATE,END_DATE,AMOUNT_1,AMOUNT_2,AMOUNT_3,AMOUNT_4,AMOUNT_5,ADULT_CHARGE,CHILD_CHARGE_1,CHILD_CHARGE_2,CHILD_CHARGE_3,RATE_SET_ID, 
SUBSTR(DECODE(MAX(H0),NULL,'',',''' || MAX(H0) || '''') || DECODE(MAX(H1),NULL,'',',''' || MAX(H1) || '''') || DECODE(MAX(H2),NULL,'',',''' || MAX(H2) || '''') || DECODE(MAX(H3),NULL,'',',''' || MAX(H3) || '''') || DECODE(MAX(H4),NULL,'',',''' || MAX(H4) || '''') || DECODE(MAX(H5),NULL,'',',''' || MAX(H5) || '''') || DECODE(MAX(H6),NULL,'',',''' || MAX(H6) || '''') || DECODE(MAX(H7),NULL,'',',''' || MAX(H7) || '''') || DECODE(MAX(H8),NULL,'',',''' || MAX(H8) || '''') || DECODE(MAX(H9),NULL,'',',''' || MAX(H9) || '''') || DECODE(MAX(H10),NULL,'',',''' || MAX(H10) || '''')
 || DECODE(MAX(H11),NULL,'',',''' || MAX(H11) || '''') || DECODE(MAX(H12),NULL,'',',''' || MAX(H12) || '''') || DECODE(MAX(H13),NULL,'',',''' || MAX(H13) || '''') || DECODE(MAX(H14),NULL,'',',''' || MAX(H14) || '''') || DECODE(MAX(H15),NULL,'',',''' || MAX(H15) || '''') || DECODE(MAX(H16),NULL,'',',''' || MAX(H16) || '''') || DECODE(MAX(H17),NULL,'',',''' || MAX(H17) || '''') || DECODE(MAX(H18),NULL,'',',''' || MAX(H18) || '''') || DECODE(MAX(H19),NULL,'',',''' || MAX(H19) || ''''),2)
 ROOMTYPES,NULL DO,LINK_RATE_SET_ID,CHILD_OWN_CHARGE_1,CHILD_OWN_CHARGE_2,CHILD_OWN_CHARGE_3,CHILD_OWN_CHARGE_4 FROM (SELECT CASE WHEN N-N_MIN = 0 THEN LABEL END H0,CASE WHEN N-N_MIN = 1 THEN LABEL END H1,CASE WHEN N-N_MIN = 2 THEN LABEL END H2,CASE WHEN N-N_MIN = 3 THEN LABEL END H3,CASE WHEN N-N_MIN = 4 THEN LABEL END H4,CASE WHEN N-N_MIN = 5 THEN LABEL END H5,CASE WHEN N-N_MIN = 6 THEN LABEL END H6,CASE WHEN N-N_MIN = 7 THEN LABEL END H7, 
 CASE WHEN N-N_MIN = 8 THEN LABEL END H8,CASE WHEN N-N_MIN = 9 THEN LABEL END H9,CASE WHEN N-N_MIN = 10 THEN LABEL END H10,CASE WHEN N-N_MIN = 11 THEN LABEL END H11,CASE WHEN N-N_MIN = 12 THEN LABEL END H12,CASE WHEN N-N_MIN = 13 THEN LABEL END H13,CASE WHEN N-N_MIN = 14 THEN LABEL END H14,CASE WHEN N-N_MIN = 15 THEN LABEL END H15,CASE WHEN N-N_MIN = 16 THEN LABEL END H16,CASE WHEN N-N_MIN = 17 THEN LABEL END H17,CASE WHEN N-N_MIN = 18 THEN LABEL END H18,CASE WHEN N-N_MIN = 19 THEN LABEL END H19,
 X.RATE_SET_ID,X.RATE_CODE,X.RESORT,BEGIN_DATE,END_DATE,AMOUNT_1,AMOUNT_2,AMOUNT_3,AMOUNT_4,AMOUNT_5,ADULT_CHARGE,CHILD_CHARGE_1,CHILD_CHARGE_2,CHILD_CHARGE_3,LINK_RATE_SET_ID,CHILD_OWN_CHARGE_1,CHILD_OWN_CHARGE_2,CHILD_OWN_CHARGE_3,CHILD_OWN_CHARGE_4
 FROM  (    SELECT ROWNUM N,X1.* FROM (  SELECT RS.RESORT,RS.RATE_CODE,RS.RATE_SET_ID,RRC.LABEL,TO_CHAR(RS.BEGIN_DATE,'DD.MM.YYYY') BEGIN_DATE,TO_CHAR(RS.END_DATE,'DD.MM.YYYY') END_DATE        ,AMOUNT_1,AMOUNT_2,AMOUNT_3,AMOUNT_4,AMOUNT_5,ADULT_CHARGE,CHILD_CHARGE_1,CHILD_CHARGE_2,CHILD_CHARGE_3,LINK_RATE_SET_ID,CHILD_OWN_CHARGE_1,CHILD_OWN_CHARGE_2,CHILD_OWN_CHARGE_3,CHILD_OWN_CHARGE_4  FROM  RATE_SET RS   LEFT JOIN RATE_SET_ROOM_CATEGORIES RSRC ON RS.RATE_SET_ID=RSRC.RATE_SET_ID LEFT JOIN RESORT$_ROOM_CATEGORY RRC ON RRC.ROOM_CATEGORY= RSRC.ROOM_CATEGORY AND RS.RESORT= RRC.RESORT 
 WHERE  (RS.RATE_CODE IS NOT NULL)  AND RS.RESORT IN (""" + HOTELS + """) AND UPPER(RS.RATE_CODE) LIKE 'ROM_____' AND trunc(RS.END_DATE, 'DDD') >= TO_DATE('21012025','DDMMYYYY') AND trunc(RS.BEGIN_DATE, 'DDD')<= TO_DATE('20112025','DDMMYYYY')
 ORDER BY RS.RESORT,RS.RATE_CODE,RS.RATE_SET_ID,RRC.LABEL  ) X1  ) X  JOIN   (    SELECT MIN(N) N_MIN, RESORT, RATE_CODE, RATE_SET_ID      FROM (      SELECT ROWNUM N,Y1.*  FROM (  SELECT RS.RESORT,RS.RATE_CODE,RS.RATE_SET_ID,RRC.LABEL,TO_CHAR(RS.BEGIN_DATE,'DD.MM.YYYY') BEGIN_DATE,TO_CHAR(RS.END_DATE,'DD.MM.YYYY') END_DATE        ,AMOUNT_1,AMOUNT_2,AMOUNT_3,AMOUNT_4,AMOUNT_5,ADULT_CHARGE,CHILD_CHARGE_1,CHILD_CHARGE_2,CHILD_CHARGE_3,LINK_RATE_SET_ID,CHILD_OWN_CHARGE_1,CHILD_OWN_CHARGE_2,CHILD_OWN_CHARGE_3,CHILD_OWN_CHARGE_4  FROM  RATE_SET RS   LEFT JOIN RATE_SET_ROOM_CATEGORIES RSRC ON RS.RATE_SET_ID=RSRC.RATE_SET_ID LEFT JOIN RESORT$_ROOM_CATEGORY RRC ON RRC.ROOM_CATEGORY= RSRC.ROOM_CATEGORY AND RS.RESORT= RRC.RESORT 
 WHERE  (RS.RATE_CODE IS NOT NULL)  AND RS.RESORT IN (""" + HOTELS + """) AND UPPER(RS.RATE_CODE) LIKE 'ROM_____' AND trunc(RS.END_DATE, 'DDD') >= TO_DATE('21012025','DDMMYYYY') AND trunc(RS.BEGIN_DATE, 'DDD')<= TO_DATE('20112025','DDMMYYYY')
 ORDER BY RS.RESORT,RS.RATE_CODE,RS.RATE_SET_ID,RRC.LABEL  ) Y1  )  GROUP BY   RATE_SET_ID, RESORT, RATE_CODE  ) Y  ON X.RESORT = Y.RESORT AND X.RATE_CODE = Y.RATE_CODE AND X.RATE_SET_ID = Y.RATE_SET_ID) GROUP BY RATE_SET_ID,RATE_CODE,RESORT,BEGIN_DATE,END_DATE,AMOUNT_1,AMOUNT_2,AMOUNT_3,AMOUNT_4,AMOUNT_5,ADULT_CHARGE,CHILD_CHARGE_1,CHILD_CHARGE_2,CHILD_CHARGE_3,LINK_RATE_SET_ID,CHILD_OWN_CHARGE_1,CHILD_OWN_CHARGE_2,CHILD_OWN_CHARGE_3,CHILD_OWN_CHARGE_4 
 ORDER BY RESORT,RATE_CODE,BEGIN_DATE,ROOMTYPES
"""


c = conn.cursor()
c.execute(sql)

base={
("ROMBBFLG","FLG","SUCORN"):{"max_ad":4,"max_ch":1},

}

rms = {('FLG','ST'):{'max_pax':4,'max_ad':3,'max_ch':2}}

f = open(path + "rates.txt", "w", encoding="utf-8")
#column_names = [desc[0] for desc in c.description]
#f.write('\t'.join(column_names))
f.write("rate\thotel\tdate_from\tdate_till\t"
    +'\t'.join([f'ad{i}' for i in range(5+1)[1:]]) 
    +f"\tex\t"
    +'\t'.join([f'ch{i}' for i in range(3+1)[1:]])
    +"\t"
    +'roomtypes'
    + '\n')
for row in c.fetchall():
    rate=row[0]
    hotel=row[1]
    date_from=row[2]
    date_till=row[3]
    ad=[None,row[4],row[5],row[6],row[7],row[8]]
    ex=row[9]
    ch=[None,row[10],row[11],row[12]]
    rt_str=row[14].split(",")
    rt = [x.replace("'", "") for x in rt_str]

    # f.write('\t'.join(str(value) for value in row) + '\n')
    f.write(f"{rate}\t{hotel}\t{date_from}\t{date_till}\t"
    +'\t'.join(str(v) for v in ad[1:]) 
    +f"\t{ex}\t"
    +'\t'.join(str(v) for v in ch[1:])
    +"\t"
    +'\t'.join(str(v) for v in rt)
    + '\n')

    try:
        ad1 = float(ad[1] + 1)
        ad2 = float(ad[2] + 2)
        ch = float(ch[1])
    except:
        continue
    
    
    f.write(f'1+0\t{ ad1 :.2f}\n')
    f.write(f'1+1\t{ ad1 + ch :.2f}\n')
    f.write(f'1+2\t{ ad1 + ch * 2 :.2f}\n')
    
    f.write(f'2+0\t{ ad2 :.2f}\n')
    f.write(f'2+1\t{ ad2 + ch :.2f}\n')
    f.write(f'2+2\t{ ad2 + ch * 2 :.2f}\n')
    
    f.write(f'3+0\t{ ad2 * 1.4 :.2f}\n')
    f.write(f'3+1\t{ ad2 * 1.4 + ch :.2f}\n')
    
    #print(f"{row}")
    for roomtype in rt:
        if (hotel,roomtype) in rms:
            max_pax = rms[(hotel,roomtype)]["max_pax"]
            max_ad = rms[(hotel,roomtype)]["max_ad"]
            max_ch = rms[(hotel,roomtype)]["max_ch"]
            pax_var = pax_variants(1,max_pax,1,max_ad,0,max_ch,13,13,2)
            print(f"{(hotel,rate,roomtype,date_from,date_till)}")
            for pax in pax_var:
                print(pax)
                
        

    
    
    
    
    
    

    
    
    
    
    
    
    
f.close()











