#   exec(open('roomrate\\from-clock-api.py').read())
# from mapping.models import *
# from mapping.fits import *
# from link.models import *
# from roomrate.models import *
from datetime import datetime, timedelta, date
import fdb
import re
import requests
import json

# def json_serial(obj):
#     """JSON serializer for objects not serializable by default json code"""

#     if isinstance(obj, (datetime, date)):
#         return obj.isoformat()
#     raise TypeError ("Type %s not serializable" % type(obj))


#base_url = "http://127.0.0.1:8000/"
base_url = "https://agent.parsing.eu/"
api_url = base_url +  "api/"
response = requests.post(api_url+'api-token-auth/', json={'username':'ivanm', 'password':'Plmdzm0pp'})
token=response.json().get('token')
headers = {'Authorization': 'Token ' + token}

def tb(cursor, sql):
    cursor.execute(sql) 
    columns = [column[0] for column in cursor.description]
    trs = []
    rows=cursor.fetchall()
    for row in rows:
        trs.append(dict(zip(columns, row)))
    return trs

def tbl(cursor):
    columns = [column[0] for column in cursor.description]
    trs = []
    rows=cursor.fetchall()
    for row in rows:
        trs.append(dict(zip(columns, row)))
    return trs

def goco(*arg):  # api_url, headers, 
    if len(arg)>=2:  
        model, par_names = arg[:2]
    else : 
        return None
    elements = requests.get(
        api_url+model+'/?'+"&".join([f"{x}={par_names[x]}" for x in par_names]),
        headers=headers
    ).json()
    if len(elements) == 0:
        if len(arg)>=3: 
            par_ids = arg[2]
            for p in par_ids:
                par_names[p[0]]=f"{api_url}{p[1]}/{p[2]}/" 
        if len(arg)>=4: 
            par_opt = arg[3]
            for p in par_opt:
                par_names[p]=par_opt[p] 

        response = requests.post(
            api_url+model+'/',
            json=par_names, 
            headers=headers
        )
        return response.json()
    if len(elements) == 1:
        return elements[0]
    if len(elements) > 1:
        return elements

def fitsearch(search_list, params_dict):
    response = requests.post(
            base_url+'mapping/fits/',
            json={"search":search_list, "params":params_dict}, 
            headers=headers
        )
    return response.json()

#from django.db.models import Q
#HotelName = ServerName = CorpName ='iHotel'
start_time =  datetime.now()
InfantsMaxCount = 1
default_adult_age = 40
#HotelName = ServerName = CorpName ='PrestigeDelux' 
HotelName = ServerName = CorpName = "GRIFID"
#HotelName = ServerName = CorpName = "MAJESTIC"

hotels={}
hotels[1]=('ХОТЕЛ БОЛЕРО','BOLERO')
hotels[2]=('ХОТЕЛ АРАБЕЛА','ARBELLA')
hotels[3]=('ХОТЕЛ ВИСТАМАР','VISTMAR')
hotels[4]=('ХОТЕЛ МЕТРОПОЛ','METROPOL')
hotels[5]=('ХОТЕЛ ЕНКАНТО БИЙЧ','ENCANTO')
hotels[6]=('ХОТЕЛ ФОРЕСТА','FORESTA')
hotels[7]=('ХОТЕЛ МАРЕА','MAREA')

corp = goco("Corp",{"name":CorpName},[])

# corp=goc(Corp,{"name":CorpName })
# hotel=goc(Hotel,{"name":HotelName , "corp":corp})

host,database,user,password =  fitsearch(['host','database','user','password'],{"ServerName":ServerName })
conn=fdb.connect(host=host,database=database,user=user,password=password, role='CLOCKBS_ROLE')
cursor=conn.cursor()

tarifi = tb(cursor,"select ID_HOTEL, ID_TARIFA , TARIFA_NAME , CURR  from TARIFA t where TARIFA_NAME LIKE '%ROM_RU_CIS_2023%' and ID_HOTEL=3 ")
#tarifi = tb(cursor,"select ID_HOTEL, ID_TARIFA , TARIFA_NAME , CURR  from TARIFA t where TARIFA_NAME LIKE '%23%' ")

rates=[]
for tarifa in tarifi[:2]:

    if CorpName == "GRIFID" : HotelName = hotels[tarifa['ID_HOTEL']][1]
    hotel = goco("Hotel",{"name":HotelName},[("corp","Corp",corp["id"])])
	
    rate = goco("Rate",
        {"name":f"{tarifa['TARIFA_NAME']} / {tarifa['CURR']}", 
         "currency":tarifa['CURR']} ,
        [("hotel","Hotel",hotel["id"])]  )
    # rate = goc(Rate,{"hotel":hotel, "name":f"{tarifa['TARIFA_NAME']} / {tarifa['CURR']}", "currency":tarifa['CURR']})

    brds= tb(cursor, 
f""" 
select m.ID_SERVICE, m.NAME, IS_BREAKFAST, IS_LUNCH, IS_DINNER, IS_EXTRAFOOD1, IS_EXTRAFOOD2
from tar_bo_base_position p 
join MEALS m on m.ID_SERVICE=p.ID_BOARD_INCLUDE
where ID_TAR_head = {tarifa['ID_TARIFA']}
group by m.ID_SERVICE, m.NAME, IS_BREAKFAST, IS_LUNCH, IS_DINNER, IS_EXTRAFOOD1, IS_EXTRAFOOD2
order by m.ID_SERVICE, m.NAME
"""
    )
    boards={}
    for brd in brds:
        # boards[brd['ID_SERVICE']]=goc(Board,{"name":brd['NAME'], "code":brd['ID_SERVICE'], "hotel":hotel})
        boards[brd['ID_SERVICE']]=goco("Board",
            {"name":brd['NAME'], "code":brd['ID_SERVICE']},
            [("hotel","Hotel",hotel["id"])],
            {"breakfast":brd['IS_BREAKFAST'],"lunch":brd['IS_LUNCH'],"dinner":brd['IS_DINNER'],
             "snacks":brd['IS_EXTRAFOOD1'],"other":brd['IS_EXTRAFOOD2']}
            )
    
    rts= tb(cursor, 
f""" 
select m.ID_ROOM_TYPE, m.TYPE_ROOM, BEDS
from tar_bo_base_position p 
join ROOM_TYPES m on m.ID_ROOM_TYPE=p.ID_ROOM_TYPE
where ID_TAR_head = {tarifa['ID_TARIFA']}
group by m.ID_ROOM_TYPE, m.TYPE_ROOM , BEDS
order by m.ID_ROOM_TYPE, m.TYPE_ROOM 
"""
)
    rooms={}
    for rt in rts:
        # rooms[rt['ID_ROOM_TYPE']]=goc(Room,{"name":rt['TYPE_ROOM'], "code":rt['ID_ROOM_TYPE'], "hotel":hotel})
        rooms[rt['ID_ROOM_TYPE']]=goco("Room",
            {"name":rt['TYPE_ROOM'], "code":rt['ID_ROOM_TYPE']},
            [("hotel","Hotel",hotel["id"])],
            {"regular_beds":rt['BEDS'], "extra_beds":rt['BEDS'], "max_infants":0,
             "max_adults":rt['BEDS'], "min_adults":1, "maxhalfpax":rt['BEDS'] * 2} 
            )

    dsDates= tb(cursor,f""" 
select p.id_tar_season , p.from_date, p.to_date from tar_bo_season s
join  tar_bo_season_period p on s.id_tar_season = p.id_tar_season
where s.ID_TAR_head = {tarifa['ID_TARIFA']}
order by  p.id_tar_season
    """)
    dates=[]
    for span in dsDates:
        d=span["FROM_DATE"]  # datetime.strptime(span["FROM_DATE"],"%Y-%m-%d")
        dates.append(d) if not d in dates else None
        d=span["TO_DATE"] + timedelta(1)    # datetime.strptime(span["TO_DATE"],"%Y-%m-%d")+datetime.timedelta(1)
        dates.append(d) if not d in dates else None

    dsRel= tb(cursor,f""" 
Select r.bo_type, r.param_filter
From TAR_BO_BASE_POSITION  b
Join TAR_BO_RELATION r  on b.id_tar_bp=r.id_tar_bp
Where ID_TAR_head = {tarifa['ID_TARIFA']}
Group By r.bo_type, r.param_filter
Order By r.bo_type, r.param_filter
    """)
    ages=[]
    book_dates=[]
    for rel in dsRel:
        limAge = re.search(":AGE\s*>=\s*(\d{1,})", rel["PARAM_FILTER"])
        ages.append(int(limAge.group(1))) if limAge != None and not int(limAge.group(1)) in ages else None
        limAge = re.search(":AGE\s*<=\s*(\d{1,})", rel["PARAM_FILTER"])
        ages.append(int(limAge.group(1))+1) if limAge != None and not int(limAge.group(1))+1 in ages else None

        # limDate = re.search(':TODAY>=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date()
        #     dates.append(d) if not d in dates else None
        # limDate = re.search(':TODAY<=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date() + timedelta(1)
        #     dates.append(d) if not d in dates else None

        # limDate = re.search(':FROM_DATE>=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date()
        #     dates.append(d) if not d in dates else None
        # limDate = re.search(':FROM_DATE<=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date() + timedelta(1)
        #     dates.append(d) if not d in dates else None

        # limDate = re.search(':VAUCHER_DATE>=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date()
        #     book_dates.append(d) if not d in book_dates else None
        # limDate = re.search(':VAUCHER_DATE<=DT\(\\"(\d\d/\d\d/\d\d\d\d)\\"\)', rel["PARAM_FILTER"])
        # if limDate != None:
        #     d=datetime.strptime(limDate.group(1) ,"%d/%m/%Y").date() + timedelta(1)
        #     book_dates.append(d) if not d in book_dates else None

    # book_dates.sort() 

    dates.sort()    
    idates=iter(dates)
    spans=[]
    date1=next(idates,None)
    while date1!=None:
        date2=next(idates,None)
        if date2==None:
            break
        spans.append((date1,date2+timedelta(-1)))
        date1=date2

    # if not 0 in ages : ages.append(0)
    ages.sort()
    if ages[0]==0 : ages=ages[1:]
    if ages[len(ages)-1]>30 : ages=ages[:len(ages)-1]


    # agepick = AgePick.goc(ages)
    try:
        agepick_id = fitsearch("AgePick",ages) 
    except:
        print(f"AgePick={ages}")
        exit()


    minChAge = minBgChAge = minAdAge = 0
    maxChAge = maxBgChAge = maxInfAge = 0
    if len(ages) == 1 :
        minChAge = 0
        minBgChAge = ages[0]
        minAdAge = ages[0]

        InfantsMaxCount=0
        maxInfAge = 0
        maxChAge = minAdAge - 1
        maxBgChAge = 99 # Should Not be used when Ages.Count = 1

    if len(ages) == 2 :

        if ages[0] > 4 :
            minChAge = 0
            minBgChAge = ages[0]
            minAdAge = ages[1]

            InfantsMaxCount=0
            maxInfAge = 0
            maxChAge = minBgChAge - 1
            maxBgChAge = minAdAge - 1
        else:
            minChAge = ages[0]
            minBgChAge = ages[1]
            minAdAge = ages[1]

            maxInfAge = minChAge - 1
            maxChAge = minAdAge - 1
            maxBgChAge = 99 # Should Not be used when Ages.Count = 2

    if len(ages) == 3 :
        minChAge = ages[0]
        minBgChAge = ages[1]
        minAdAge = ages[2]

        maxInfAge = minChAge - 1
        maxChAge = minBgChAge - 1
        maxBgChAge = minAdAge - 1

    dsAccom= tb(cursor,f""" 
select p.ID_ROOM_TYPE, p.ID_BOARD_INCLUDE, max( p.max_persons ) MAX_PERSONS
from tar_bo_base_position p
where ID_TAR_head = {tarifa['ID_TARIFA']}
group by p.id_room_type, p.id_board_include
order by p.id_room_type, p.id_board_include
    """)

    p={}
    p["ID_RATE"]=tarifa['ID_TARIFA']
    p["ID_TAR_CALC_COMMON"] = 1
    p["ID_HOTEL"]=tarifa['ID_HOTEL']
    p["CURR"]=tarifa['CURR']

    for a in dsAccom:  # a["ID_ROOM_TYPE"], a["ID_BOARD_INCLUDE"], a["MAX_PERSONS"]
        max_persons = a["MAX_PERSONS"]
        p["ID_ROOM_TYPE"] = a["ID_ROOM_TYPE"]
        p["ID_BOARD"] = a["ID_BOARD_INCLUDE"]

        room = rooms[p['ID_ROOM_TYPE']]
        board = boards[p['ID_BOARD']]

        for tot_persons in range(1, max_persons+1):
            for adults in range (1, tot_persons+1):
                maxbigChildren = tot_persons - adults if len(ages)==3 else 0
                for bigChildren in range(0, maxbigChildren+1):
                    maxInfants = min(InfantsMaxCount, tot_persons - adults - bigChildren)                                 \

                    for Infants in range(0, maxInfants+1):
                        children  = tot_persons - adults - bigChildren - Infants
                        p["ADULT_COUNT"] = adults
                        p["CHILD_COUNT"] = bigChildren + children + Infants

                        AGEstr = ""
                        for id in range (1, adults+1):
                            AGEstr = f"{AGEstr},{default_adult_age}"  
                        # Next
                        AGEstr = AGEstr[1:]  # AGEstr = Mid(AGEstr, 2)
                        p["ADULT_AGES"] = AGEstr
                        AGEstr = ""
                        for id in range(1,bigChildren+1):
                            AGEstr = f"{AGEstr},{maxBgChAge}" 
                        for id in range(1,children+1):
                            AGEstr = f"{AGEstr},{maxChAge}" 
                        for id in range(1,Infants+1):
                            AGEstr = f"{AGEstr},{maxInfAge}" 
                        AGEstr =  AGEstr[1:] 
                        p["CHILD_AGES"] = AGEstr

                        # 'p.ADULT_AGES = "33,33"
                        # 'p.CHILD_AGES = "6"


                        # paxpick = PaxPick(agepick,adults,bigChildren,children,Infants) 
                        paxpick_id = fitsearch("PaxPick",
                                list((agepick_id,adults,bigChildren,children,Infants)))
                        
                        # priceitem = goc(PriceItem,
                        #     {   "room":room,
                        #         "board":board, 
                        #         "rate":rate,
                        #         "paxpick":paxpick,
                        #     }
                        # )
                        priceitem = goco("PriceItem",
                            {   "room":room["id"],
                                "board":board["id"], 
                                "rate":rate["id"],
                                "paxpick":paxpick_id,
                            },
                            [("room","Room",room["id"]),
                             ("board","Board",board["id"]),
                             ("rate","Rate",rate["id"]),
                             ("paxpick","PaxPick",paxpick_id),
                             ]
                        )
                        
                        for  from_date, to_date in spans:
                            p["ARRIVAL_DATE"] = datetime.strftime(from_date, "%d.%m.%Y")
                            p["DEPARTURE_DATE"] = datetime.strftime(from_date + timedelta(1), "%d.%m.%Y") 

                            # CalculatePrice:
                            cursor.callproc("TAR_CALC_INPUT_PLAIN$INT", (
                            p["ADULT_COUNT"],p["CHILD_COUNT"],p["ID_ROOM_TYPE"],p["ID_BOARD"],
                            p["ARRIVAL_DATE"],p["DEPARTURE_DATE"],
                            "","",None,"",None,None,
                            p["ID_RATE"],p["ADULT_AGES"],p["CHILD_AGES"],p["ID_TAR_CALC_COMMON"],
                            ))
                            p1=tbl(cursor)
                            cursor.callproc("TAR_CALC_EVAL_ALL$INT", (p1[0]["ID_TAR_CALC"],))
                            cursor.callproc("TAR_CALC_POST_PREPARE$INT", (p1[0]["ID_TAR_CALC"],))
                            cursor.callproc("TAR_CALC_GET_PRICE$INT", (
                                p1[0]["ID_TAR_CALC"],p["ID_HOTEL"],p1[0]["ID_RESERV"],p["CURR"]
                            ))
                            p2=tbl(cursor)
                            amount = round(p2[0]["ROOM_PRICE"]*100)
                            if amount == 0:
                                continue

                            # pricespan = PriceSpan.update(
                            #     priceitem=priceitem,
                            #     weekdays=254, 
                            #     datemin=from_date,
                            #     datemax=to_date,
                            #     amount=amount
                            # )
                            pricespan = fitsearch("PriceSpan",
                                list((priceitem["id"],254,from_date.isoformat(),to_date.isoformat(),amount)))

                            print(f" {datetime.now()-start_time} / {datetime.now()-start_time} / {pricespan} -> {amount}"  )


    #                     Next d
    #                 Next Infants
    #             Next bigChildren
    #         Next adults
    #     Next tot_persons
    # Next a


