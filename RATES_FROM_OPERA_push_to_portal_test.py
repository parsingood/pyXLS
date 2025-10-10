import requests
import json
import os
import re
import datetime 
import cx_Oracle
from itertools import product

path = "C:/OPERA/"
corp_name = "ALBENA"
BULK_SIZE = 100 
rates=[
    {"rate_name":"ALBENA-BASE-AI","market_board":'ROMAI'},
    {"rate_name":"ALBENA-BASE-FB","market_board":'ROMFB'},
    {"rate_name":"ALBENA-BASE-HB","market_board":'ROMHB'},
    {"rate_name":"ALBENA-BASE-BB","market_board":'ROMBB'},
    {"rate_name":"ALBENA-BASE-RO","market_board":'ROMRO'},
]


DATE_FROM = '21012025'
DATE_TILL = '20112025'

adult_age_def = 12
gchild_age_def = 6
child_age_def = 2

room_defaults = {"min_pax": 1, "max_pax": 4, "min_ad": 1, "max_ad": 3, "min_ch": 0, "max_ch": 2}

ad_ch_age={
    "DOR":{"adult_age":12,"gchild_age":2,"child_age":2},
    "DRU":{"adult_age":12,"gchild_age":2,"child_age":2},
    "FLG":{"adult_age":12,"gchild_age":2,"child_age":2},
    "KLK":{"adult_age":12,"gchild_age":2,"child_age":2},
    "GER":{"adult_age":12,"gchild_age":2,"child_age":2},
    "RAL":{"adult_age":12,"gchild_age":2,"child_age":2},
    "SUP":{"adult_age":12,"gchild_age":2,"child_age":2},
}



BASE_URL = "https://portal.parsing.eu/api/"
BASE_ROOMRATE = "https://portal.parsing.eu/roomrate/"
TOKEN = "2dda759d18dc8a6c232e5065a35d9c89d0282024"
HEADERS = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

HOTELS = [
'GER', 'MRA', 'SLA', 'ELI', 
'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 
'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 
'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 
'PAN', 'VMG'    
]

HOTELS = [
'GER', 'KLK',  'DOR', 'DRU', 'FLG', 'SUP', 'RAL'     
]



rents={
("ROMBBFLG","FLG","GRAP"):{"max_ad":4,"max_ch":1},
("FLG","GRAP"):{"max_ad":4,"max_ch":1},
("FLG","GRME"):{"max_ad":6,"max_ch":1},
("FLG","SUCORN"):{"max_ad":2,"max_ch":2},
("FLG","SUPAN"):{"max_ad":2,"max_ch":2},
("FLG","PENTCO"):{"max_ad":2,"max_ch":1},
("FLG","PENT"):{"max_ad":2,"max_ch":1},



("DRU","A2P"):{"max_ad":2,"max_ch":2},
("FLA","M4"):{"max_ad":4,"max_ch":1},
("KLK","A4"):{"max_ad":4,"max_ch":1},
("GER","A4"):{"max_ad":4,"max_ch":1},
("GER","A2"):{"max_ad":2,"max_ch":1},
("GER","M2"):{"max_ad":2,"max_ch":1},
("GER","SURIV"):{"max_ad":2,"max_ch":2},
("GER","SUSEA"):{"max_ad":2,"max_ch":2},
("SUP","A2L"):{"max_ad":2,"max_ch":2},
("DTC","A2"):{"max_ad":2,"max_ch":2},
("SLA","A2"):{"max_ad":2,"max_ch":1},
("SLA","M2"):{"max_ad":2,"max_ch":1},
("SLA","A4"):{"max_ad":4,"max_ch":1},
("MRA","A2"):{"max_ad":2,"max_ch":1},
("SLA","A4"):{"max_ad":4,"max_ch":1},

("BOR","A2"):{"max_ad":2,"max_ch":1},
("BOR","A4"):{"max_ad":4,"max_ch":1},

("ELI","A2"):{"max_ad":2,"max_ch":1},

("NON","A2"):{"max_ad":2,"max_ch":1},
("NON","A4"):{"max_ad":4,"max_ch":1},

("VIT","A2"):{"max_ad":4,"max_ch":0},
("VIT","A4"):{"max_ad":4,"max_ch":1},
    }

# Ком. такса евро на човек/ден (възрастен, дете)
# taxes={
#     '': (1, 0.5),        # (възрастен, дете) по подразбиране, ако няма друго
#     'DOR': (1.5, 0.75),  # (възрастен, дете)
#     'DRU': (1.5, 0.75),  # (възрастен, дете)
#     'FLG': (1.5, 0.75),  # (възрастен, дете)
# }


# Кеширане на вече извлечени данни
board_cache = {}  # {"hotel|board": board_url, board_uid}
agepick_cache = {}  # {"adAge|gchAge|chAge": agepick_url}
paxpick_cache = {}  # {"ad|gch|ch|inf|agepick_url": paxpick_url}
room_cache = {}  # {"hotel|roomtype": room_id}



# Извличане на ID от URL (ако трябва)
def extract_id(url):
    return url.rstrip('/').split('/')[-1] if url else None

def fetch_data(endpoint, params=None):
    response = requests.get(BASE_URL + endpoint, params=params, headers=HEADERS)
    # print(f"url: {response.url}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {endpoint}: {response.status_code}")
        return None

def fetch_data(endpoint, params=None):
    all_results = []
    url = BASE_URL + endpoint
    
    while url:
        response = requests.get(url, params=params, headers=HEADERS)
        # print(f"url: {response.url}")
        if response.status_code == 200:
            data = response.json()
            all_results.extend(data.get("results", []))
            url = data.get("next")  # Следващият URL за пейджинация
        else:
            print(f"Error fetching {endpoint}: {response.status_code}")
            exit()
            return None
    
    return {"results": all_results}



def delete_price_spans(rate_id, hotel_name, board_name):
    """
    Изтрива всички `PriceSpan` за даден `rate_id`, хотел и борд.
    Връща списък с `PriceItem` ID-та, които са били засегнати.
    """
    hotel_data = fetch_data("Hotel", {"name_pms": hotel_name})
    if not hotel_data or "results" not in hotel_data or not hotel_data["results"]:
        print(f"❌ Грешка: Хотел {hotel_name} не е намерен!")
        return []

    hotel_id = hotel_data["results"][0]["id"]

    board = get_board(hotel_name, board_name)
    board_id = board.get("id")


    create_url = f"{BASE_ROOMRATE}priceitms/pricespans_delete/"
    response = requests.post(
        create_url, 
        json={"rate_id": rate_id, "board_id": board_id, "hotel_id": hotel_id,}, 
        headers=HEADERS
    )

    if response.status_code in [200, 201]:
        deleted_items = response.json()
        print(f"✅ Изтрити {deleted_items} pricespans.")
        return deleted_items  # Връща създадените записи с ID
    else:
        print(f"❌ Грешка при изтриване на pricespans: {response.status_code} - {response.text}")
        return []



def create_data(endpoint, data):
    response = requests.post(BASE_URL + endpoint, json=data, headers=HEADERS)
    print ("----------------------------------------")
    print (BASE_URL + endpoint)
    print (data)
    print (response.text)
    print ("----------------------------------------")
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating {endpoint}: {response.status_code} - {response.text}")
        return None


# Функции за кеширане
def get_board(hotel, board):
    key = f"{hotel}|{board}"
    if key in board_cache:
        return board_cache[key]
    
    board_data = fetch_data("Board", {"hotel__name_pms": hotel, "name_pms": board})
    if board_data and board_data['results']:
        board = board_data['results'][0]
        board.update({"url":f"{BASE_URL}Board/{board.get('id')}/"})
        board_cache[key] = board
        return board
    print(f"❌ Error: Board not found for hotel={hotel}, board={board}")
    return None, None


def get_room(hotel, roomtype):
    key = f"{hotel}|{roomtype}"
    if key in room_cache:
        return room_cache[key]

    room_data = fetch_data("Room", {"hotel__name_pms": hotel, "code": roomtype})
    if room_data and room_data['results']:
        room = room_data['results'][0]
        room.update({"url":f"{BASE_URL}Room/{room.get('id')}/"})
        room_cache[key] = room
        return room
    print(f"❌ Error: Room not found for hotel={hotel}, roomtype={roomtype}")
    return None

def get_agepick(adAge, gchAge, chAge):
    key = f"{adAge}|{gchAge}|{chAge}"
    if key in agepick_cache:
        return agepick_cache[key]
    
    agepick_data = fetch_data("AgePick", {"adAge": adAge, "gchAge": gchAge, "chAge": chAge})

    if agepick_data and agepick_data['results']:
        agepick = agepick_data['results'][0]
        agepick.update({"url":f"{BASE_URL}AgePick/{agepick.get('id')}/"})

    else:
        agepick = create_data("AgePick/", {"adAge": adAge, "gchAge": gchAge, "chAge": chAge})
        if agepick:
            agepick.update({"url":f"{BASE_URL}AgePick/{agepick.get('id')}/"})
        else:
            return None
    
    agepick_cache[key] = agepick
    return agepick

def get_paxpick(ad, gch, ch, inf, adAge, gchAge, chAge):
    key = f"{ad}|{gch}|{ch}|{inf}|{adAge}|{gchAge}|{chAge}"
    if key in paxpick_cache:
        return paxpick_cache[key]
    
    agepick = get_agepick(adAge, gchAge, chAge)
    agepick_url = agepick.get("url")
    agepick_id = agepick.get("id")

    paxpick_data = fetch_data("PaxPick", {
        "agepick__id": agepick_id, "ad": ad, "gch": gch, "ch": ch, "inf": inf
    })
    if paxpick_data and paxpick_data['results']:
        paxpick = paxpick_data['results'][0]
        paxpick.update({"url":f"{BASE_URL}PaxPick/{paxpick.get('id')}/"})

    else:
        paxpick = create_data("PaxPick/", {
            "agepick": agepick_url, "ad": ad, "gch": gch, "ch": ch, "inf": inf
        })

        if paxpick:
            paxpick.update({"url":f"{BASE_URL}PaxPick/{paxpick.get('id')}/"})

        else:
            return None

    paxpick_cache[key] = paxpick
    return paxpick



def bulk_create_price_items(price_items):
    """Създава множество PriceItem с една заявка и връща създадените ID-та."""
    if not price_items:
        return []
    
    print("📤 Данни, които изпращаме към API:")
    for item in price_items:
        print(json.dumps(item, indent=4))

    create_url = f"{BASE_ROOMRATE}priceitms/bulk_get_or_create/"
    response = requests.post(create_url, json=price_items, headers=HEADERS)

    if response.status_code in [200, 201]:
        created_items = response.json()
        print(f"✅ Създадени {len(created_items)} PriceItem.")
        return created_items  # Връща създадените записи с ID
    else:
        print(f"❌ Грешка при създаване на PriceItem: {response.status_code} - {response.text}")
        return []

def bulk_create_price_spans(price_spans):
    """Създава множество PriceSpan с една заявка."""
    if not price_spans:
        return
    
    create_url = f"{BASE_URL}pricespans/bulk_create/"
    response = requests.post(create_url, json=price_spans, headers=HEADERS)
    
    if response.status_code in [200, 201]:
        print(f"✅ Създадени {len(price_spans)} PriceSpan.")
    else:
        print(f"❌ Грешка при създаване на PriceSpan: {response.status_code} - {response.text}")

def get_hotel_codes(corp_name):
    endpoint = f"Hotel/?corp__name={corp_name}"
    hotel_codes = {}

    while endpoint:
        hotels_data = fetch_data(endpoint)
        if not hotels_data or "results" not in hotels_data:
            print("Error fetching hotel data!")
            break

        for hotel in hotels_data["results"]:
            hotel_id = str(hotel["id"])  # ID на хотела от API-то
            hotel_codes[hotel_id] = hotel["name_pms"]  # Взимаме `name_pms`

        # Отиваме на следващата страница
        endpoint = hotels_data.get("next", None)
        if endpoint:
            endpoint = endpoint.replace(BASE_URL, "")  # Изчистваме пълния URL

    return hotel_codes

def chunkify(lst, size):
    """Разделя списък на части от `size` елемента."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
# Изтегляме хотелските кодове за ALBENA
hotel_codes = get_hotel_codes(corp_name)

def get_room_parameters(corp_name, hotel_codes):
    endpoint = f"Room/?hotel__corp__name={corp_name}"
    room_params = {}

    while endpoint:
        rooms_data = fetch_data(endpoint)
        if not rooms_data or "results" not in rooms_data:
            print("Error fetching room data!")
            break

        for room in rooms_data["results"]:
            hotel_id = room["hotel"].split("/")[-2]  # ID на хотела от API
            hotel_code = hotel_codes.get(hotel_id, "UNKNOWN")  # Преобразуваме ID в `name_pms`

            key = (hotel_code, room["code"])  # Ключ (код на хотел, код на стая)
            room_params[key] = {
                "min_pax": room["min_pax"],
                "max_pax": room["max_pax"],
                "min_ad": room["min_ad"],
                "max_ad": room["max_ad"],
                "min_ch": room["min_ch"],
                "max_ch": room["max_ch"],
            }

        # Отиваме на следващата страница
        endpoint = rooms_data.get("next", None)
        if endpoint:
            endpoint = endpoint.replace(BASE_URL, "")  # Премахваме пълния URL

    return room_params

# Изтегляме всички стаи за ALBENA
rms = get_room_parameters(corp_name, hotel_codes)
#rms = {('FLG','ST'):{'max_pax':4,'max_ad':3,'max_ch':2}}

#print(rms)

def pax_variants(
    min_pax = 0,  # Минимален общ брой хора
    max_pax = 0,  # Максимален общ брой хора
    min_ad = 0,   # Минимален брой възрастни
    max_ad = 0,   # Максимален брой възрастни
    min_ch = 0,   # Минимален брой деца
    max_ch = 0,   # Максимален брой деца
    adult_age = 12, # Минимален години на възрастни
    gchild_age = 12, # Минимален години на порасналите деца
    child_age = 2 # Минимален години на дете
):
    '''
    връща:
    - [
    - "ad": 2, "gch": 1, "ch": 1, "inf": 0, 
    - "agepick__adAge": 12, "agepick__gchAge": 6, "agepick__chAge": 2}
    - ]
    '''
    # print( f'{ (min_pax,max_pax,min_ad,max_ad,min_ch,max_ch,adult_age,gchild_age,child_age)}')

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
    #  [adult_age, gchild_age, child_age,  adults, 0, children, 0]
    #      0           1          2           3    4      5     6
    paxpick_filters = [
        {"ad": c[3], "gch": c[4], "ch": c[5], "inf": c[6], 
         "agepick__adAge": c[0], "agepick__gchAge": c[1], "agepick__chAge": c[2]}
        for c in combinations
    ]

    return paxpick_filters
    return combinations, paxpick_filters

print(f'Started at {datetime.datetime.now().strftime("%A, %d.%m.%Y %X")} \n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
conn = cx_Oracle.connect(user=r'OPERA', password='opera', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
cursor = conn.cursor()

for HOTEL in HOTELS:

    price_spans = []  # Временен масив за `PriceSpan`
    pending_price_items = []  # Временен масив за `PriceItem`
    price_item_map = {}  # Картографиране (room, board, pax) -> временен индекс


    for rt in rates:

        rate_name = rt.get("rate_name")
        market_board = rt.get("market_board")

        print(f'⏳ Обработва се: rate_name={rate_name} , market_board={market_board}  \n') 

        rate_data = fetch_data("Rate", {"corp__name": corp_name, "name": rate_name})

        if not rate_data or not rate_data.get("results"):
            print(f"❌ Грешка: Rate не е намерен за corp_name={corp_name} и rate_name={rate_name} !")
            continue

        rate_id = rate_data['results'][0].get('id')
        rate_url = f"{BASE_URL}Rate/{rate_id}/"

        # ✅ Изтриваме старите цени и взимаме списък с `PriceItem` ID-та
        delete_price_spans(rate_id, HOTEL, market_board[3:])

        sql=f"""
    SELECT 
        RATE_CODE,
        RESORT,
        BEGIN_DATE,
        END_DATE,
        AMOUNT_1, AMOUNT_2, AMOUNT_3, AMOUNT_4, AMOUNT_5,
        ADULT_CHARGE, CHILD_CHARGE_1, CHILD_CHARGE_2, CHILD_CHARGE_3,
        RATE_SET_ID, 
        SUBSTR(
            DECODE(MAX(H0), NULL, '', ',''' || MAX(H0) || '''') || 
            DECODE(MAX(H1), NULL, '', ',''' || MAX(H1) || '''') || 
            DECODE(MAX(H2), NULL, '', ',''' || MAX(H2) || '''') || 
            DECODE(MAX(H3), NULL, '', ',''' || MAX(H3) || '''') || 
            DECODE(MAX(H4), NULL, '', ',''' || MAX(H4) || '''') || 
            DECODE(MAX(H5), NULL, '', ',''' || MAX(H5) || '''') || 
            DECODE(MAX(H6), NULL, '', ',''' || MAX(H6) || '''') || 
            DECODE(MAX(H7), NULL, '', ',''' || MAX(H7) || '''') || 
            DECODE(MAX(H8), NULL, '', ',''' || MAX(H8) || '''') || 
            DECODE(MAX(H9), NULL, '', ',''' || MAX(H9) || '''') || 
            DECODE(MAX(H10), NULL, '', ',''' || MAX(H10) || '''') || 
            DECODE(MAX(H11), NULL, '', ',''' || MAX(H11) || '''') || 
            DECODE(MAX(H12), NULL, '', ',''' || MAX(H12) || '''') || 
            DECODE(MAX(H13), NULL, '', ',''' || MAX(H13) || '''') || 
            DECODE(MAX(H14), NULL, '', ',''' || MAX(H14) || '''') || 
            DECODE(MAX(H15), NULL, '', ',''' || MAX(H15) || '''') || 
            DECODE(MAX(H16), NULL, '', ',''' || MAX(H16) || '''') || 
            DECODE(MAX(H17), NULL, '', ',''' || MAX(H17) || '''') || 
            DECODE(MAX(H18), NULL, '', ',''' || MAX(H18) || '''') || 
            DECODE(MAX(H19), NULL, '', ',''' || MAX(H19) || ''''),2
        ) AS ROOMTYPES,
        NULL DO,
        LINK_RATE_SET_ID,
        CHILD_OWN_CHARGE_1, CHILD_OWN_CHARGE_2, CHILD_OWN_CHARGE_3, CHILD_OWN_CHARGE_4 
    FROM (
        SELECT 
            CASE WHEN N-N_MIN = 0 THEN LABEL END H0,
            CASE WHEN N-N_MIN = 1 THEN LABEL END H1,
            CASE WHEN N-N_MIN = 2 THEN LABEL END H2,
            CASE WHEN N-N_MIN = 3 THEN LABEL END H3,
            CASE WHEN N-N_MIN = 4 THEN LABEL END H4,
            CASE WHEN N-N_MIN = 5 THEN LABEL END H5,
            CASE WHEN N-N_MIN = 6 THEN LABEL END H6,
            CASE WHEN N-N_MIN = 7 THEN LABEL END H7,
            CASE WHEN N-N_MIN = 8 THEN LABEL END H8,
            CASE WHEN N-N_MIN = 9 THEN LABEL END H9,
            CASE WHEN N-N_MIN = 10 THEN LABEL END H10,
            CASE WHEN N-N_MIN = 11 THEN LABEL END H11,
            CASE WHEN N-N_MIN = 12 THEN LABEL END H12,
            CASE WHEN N-N_MIN = 13 THEN LABEL END H13,
            CASE WHEN N-N_MIN = 14 THEN LABEL END H14,
            CASE WHEN N-N_MIN = 15 THEN LABEL END H15,
            CASE WHEN N-N_MIN = 16 THEN LABEL END H16,
            CASE WHEN N-N_MIN = 17 THEN LABEL END H17,
            CASE WHEN N-N_MIN = 18 THEN LABEL END H18,
            CASE WHEN N-N_MIN = 19 THEN LABEL END H19,
            X.RATE_SET_ID, X.RATE_CODE, X.RESORT,
            BEGIN_DATE, END_DATE,
            AMOUNT_1, AMOUNT_2, AMOUNT_3, AMOUNT_4, AMOUNT_5,
            ADULT_CHARGE, CHILD_CHARGE_1, CHILD_CHARGE_2, CHILD_CHARGE_3,
            LINK_RATE_SET_ID, CHILD_OWN_CHARGE_1, CHILD_OWN_CHARGE_2, CHILD_OWN_CHARGE_3, CHILD_OWN_CHARGE_4
        FROM (
            SELECT ROWNUM N, X1.* 
            FROM (
                SELECT 
                    RS.RESORT, RS.RATE_CODE, RS.RATE_SET_ID, RRC.LABEL,
                    TO_CHAR(RS.BEGIN_DATE, 'YYYY-MM-DD') BEGIN_DATE,
                    TO_CHAR(RS.END_DATE, 'YYYY-MM-DD') END_DATE,
                    AMOUNT_1, AMOUNT_2, AMOUNT_3, AMOUNT_4, AMOUNT_5,
                    ADULT_CHARGE, CHILD_CHARGE_1, CHILD_CHARGE_2, CHILD_CHARGE_3,
                    LINK_RATE_SET_ID, CHILD_OWN_CHARGE_1, CHILD_OWN_CHARGE_2, CHILD_OWN_CHARGE_3, CHILD_OWN_CHARGE_4
                FROM RATE_SET RS
                LEFT JOIN RATE_SET_ROOM_CATEGORIES RSRC ON RS.RATE_SET_ID = RSRC.RATE_SET_ID
                LEFT JOIN RESORT$_ROOM_CATEGORY RRC ON RRC.ROOM_CATEGORY = RSRC.ROOM_CATEGORY AND RS.RESORT = RRC.RESORT 
                WHERE RS.RATE_CODE IS NOT NULL
                    AND RS.RESORT = '{HOTEL}'
                    AND UPPER(RS.RATE_CODE) LIKE '{market_board}' || RS.RESORT
                    AND TRUNC(RS.END_DATE, 'DDD') >= TO_DATE('{DATE_FROM}','DDMMYYYY')
                    AND TRUNC(RS.BEGIN_DATE, 'DDD') <= TO_DATE('{DATE_TILL}','DDMMYYYY')
                ORDER BY RS.RESORT, RS.RATE_CODE, RS.RATE_SET_ID, RRC.LABEL
            ) X1
        ) X
        JOIN (
            SELECT MIN(N) N_MIN, RESORT, RATE_CODE, RATE_SET_ID
            FROM (
                SELECT ROWNUM N, Y1.*
                FROM (
                    SELECT RS.RESORT, RS.RATE_CODE, RS.RATE_SET_ID, RRC.LABEL,
                        TO_CHAR(RS.BEGIN_DATE, 'DD.MM.YYYY') BEGIN_DATE,
                        TO_CHAR(RS.END_DATE, 'DD.MM.YYYY') END_DATE,
                        AMOUNT_1, AMOUNT_2, AMOUNT_3, AMOUNT_4, AMOUNT_5,
                        ADULT_CHARGE, CHILD_CHARGE_1, CHILD_CHARGE_2, CHILD_CHARGE_3,
                        LINK_RATE_SET_ID, CHILD_OWN_CHARGE_1, CHILD_OWN_CHARGE_2, CHILD_OWN_CHARGE_3, CHILD_OWN_CHARGE_4
                    FROM RATE_SET RS
                    LEFT JOIN RATE_SET_ROOM_CATEGORIES RSRC ON RS.RATE_SET_ID = RSRC.RATE_SET_ID
                    LEFT JOIN RESORT$_ROOM_CATEGORY RRC ON RRC.ROOM_CATEGORY = RSRC.ROOM_CATEGORY AND RS.RESORT = RRC.RESORT 
                    WHERE RS.RATE_CODE IS NOT NULL
                        AND RS.RESORT = '{HOTEL}'
                        AND UPPER(RS.RATE_CODE) LIKE '{market_board}' || RS.RESORT
                        AND TRUNC(RS.END_DATE, 'DDD') >= TO_DATE('{DATE_FROM}','DDMMYYYY')
                        AND TRUNC(RS.BEGIN_DATE, 'DDD') <= TO_DATE('{DATE_TILL}','DDMMYYYY')
                        AND RRC.LABEL <> 'PM'
                    ORDER BY RS.RESORT, RS.RATE_CODE, RS.RATE_SET_ID, RRC.LABEL
                ) Y1
            )
            GROUP BY RATE_SET_ID, RESORT, RATE_CODE
        ) Y ON X.RESORT = Y.RESORT AND X.RATE_CODE = Y.RATE_CODE AND X.RATE_SET_ID = Y.RATE_SET_ID
    )
    GROUP BY RATE_SET_ID, RATE_CODE, RESORT, BEGIN_DATE, END_DATE,
        AMOUNT_1, AMOUNT_2, AMOUNT_3, AMOUNT_4, AMOUNT_5,
        ADULT_CHARGE, CHILD_CHARGE_1, CHILD_CHARGE_2, CHILD_CHARGE_3,
        LINK_RATE_SET_ID, CHILD_OWN_CHARGE_1, CHILD_OWN_CHARGE_2, CHILD_OWN_CHARGE_3, CHILD_OWN_CHARGE_4
    ORDER BY RESORT, RATE_CODE, ROOMTYPES, BEGIN_DATE

        """

        try:
            cursor.execute(sql)

        except ex as Exception:
            print(f"ERROR:  {ex} \n \n")
            print(sql)
            # exit()
            continue

        rows = cursor.fetchall()
        if not rows:
            print(f"NO ROWS \n \n")
            #print(sql)
            continue   
        
        for row in rows:

            rate=row[0]
            board=rate[3:5]
            hotel=row[1] # = HOTEL
            date_from=row[2]
            date_till=row[3]

            print(f"row: {row} !")

            board = get_board(hotel, board)
            board_url = board.get("url")
            board_id = board.get("id")

            ad=[None,row[4],row[5],row[6],row[7],row[8]]
            ex=row[9]
            ch=[None,row[10],row[11],row[12]]
            rt_str=row[14].split(",")
            rt = [x.replace("'", "") for x in rt_str]

            try:
                ad1 = float(ad[1])
                ad2 = float(ad[2])

                try:
                    ch1 = float(ch[1])
                except:
                    ch1 = None

                try:
                    ch2 = float(ch[2])
                except:
                    ch2 = None

                if ch1:
                    ch = ch1
                elif ch2:
                    ch = ch2
                else:
                    ch = 0
                
            except:
                continue
            

            #print(f"{row}")
            for roomtype in rt:
                if (hotel,roomtype) in rms:

                    room_data = get_room(hotel, roomtype)

                    if room_data:
                        room_id = room_data.get('id')
                        room_url = room_data.get('url')

                    else:
                        print(f"error on Room for hotel = {hotel}, roomtype = {roomtype} !")
                        continue

                    max_pax = rms[(hotel,roomtype)]["max_pax"]
                    max_ad = rms[(hotel,roomtype)]["max_ad"]
                    max_ch = rms[(hotel,roomtype)]["max_ch"]

                    room_info = rms.get((hotel, roomtype), room_defaults)

                    min_pax = room_info["min_pax"]
                    max_pax = room_info["max_pax"]
                    min_ad = room_info["min_ad"]
                    max_ad = room_info["max_ad"]
                    min_ch = room_info["min_ch"]
                    max_ch = room_info["max_ch"]

                    adult_age = ad_ch_age.get(hotel, {}).get("adult_age", adult_age_def), 
                    gchild_age = ad_ch_age.get(hotel, {}).get("gchild_age", gchild_age_def), 
                    child_age = ad_ch_age.get(hotel, {}).get("child_age", child_age_def), 

                    paxpick_filters = pax_variants(
                        min_pax, max_pax, min_ad, max_ad, min_ch, max_ch,
                        adult_age = adult_age, 
                        gchild_age = gchild_age, 
                        child_age = child_age, 
                    )

                    for paxpick_filter in paxpick_filters:

                        paxpick_data = get_paxpick(
                                paxpick_filter["ad"],
                                paxpick_filter["gch"],
                                paxpick_filter["ch"],
                                paxpick_filter["inf"],
                                adult_age,
                                gchild_age,
                                child_age
                        )

                        paxpick_url = paxpick_data.get("url")
                        paxpick_id = paxpick_data.get("id")

                        a=paxpick_filter.get("ad") # count of adults 12+
                        gc=paxpick_filter.get("gch") # count of grown children 6-11.99
                        c=paxpick_filter.get("ch") # count of children 2-5.99

                        # максималния включен в наема брой възрастни и деца
                        rent_max = rents.get((rate, hotel, roomtype), rents.get((hotel, roomtype)))

                        if rent_max:
                            # наема се взема от втората позиция 
                            am = ad2 + a * 1 #  по 1 евро на възрастен надценка
                            try:
                                a_max, c_max = rent_max
                                if a > a_max:
                                    am += (a-a_max) * ex 
                                    am -= (a-a_max) # за възрастните над капацитета няма надценка
                                if c > c_max:
                                    am += (gc-c_max) * ch

                            except:
                                pass

                        else:
                            # нормална цена за стая - не наем
                            if (a,gc) == (1,0): am = (ad1 + 1)
                            if (a,gc) == (1,1): am = (ad1 + 1) + ch
                            if (a,gc) == (1,2): am = (ad1 + 1) + ch * 2
                            if (a,gc) == (2,0): am = (ad2 + 2)
                            if (a,gc) == (2,1): am = (ad2 + 2) + ch
                            if (a,gc) == (2,2): am = (ad2 + 2) + ch * 2
                            if (a,gc) == (3,0): am = (ad2 + 2) * 1.4 # =(ad2 + 2) + 0.8 * (ad2 + 2)/2
                            if (a,gc) == (3,1): am = (ad2 + 2) * 1.4 + ch

                        # tax_ad, tax_ch = taxes.get(hotel, taxes.get('', (0, 0)))
                        # am = am + a*tax_ad + c*tax_ch


                        # Определяме ключа като комбинация от URL-овете
                        key = (rate_id, room_id, board_id, paxpick_id)

                        if key not in price_item_map:
                            pending_price_items.append({
                                "rate_id": rate_id,  # Линк към `Rate`
                                "room_id": room_id,  # Линк към `Room`
                                "board_id": board_id,  # Линк към `Board`
                                "paxpick_id": paxpick_id  # Линк към `PaxPick`
                            })
                            price_item_map[key] = None  # Засега няма ID, защото `PriceItem` не е създаден

                        # Добавяме `PriceSpan`, но без `priceitem` засега
                        price_spans.append({
                            "priceitem_key": key,  # Използваме временен ключ вместо ID
                            "datemin": date_from,
                            "datemax": date_till,
                            "amount": int(am * 100)
                        })

    # print(f"price_spans:{price_spans[:5]}")

    # print(f"price_item_map:{price_item_map}")


    # Етап 2: Масово създаваме `PriceItem` на части

    created_price_items = []
    for batch in chunkify(pending_price_items, BULK_SIZE):
        created_price_items.extend(bulk_create_price_items(batch))

    # print(f"created_price_items:{created_price_items[:5]}")


    # Обновяваме `price_item_map` с реалните ID-та
    for item, original in zip(created_price_items, pending_price_items):
        key = (original["rate_id"], original["room_id"], original["board_id"], original["paxpick_id"])
        price_item_map[key] = item


    # print(f"created_price_items:{pending_price_items[:5]}")


    # Етап 3: Присвояваме `priceitem` на `PriceSpan`
    for span in price_spans:
        key = span.pop("priceitem_key")
        if key in price_item_map and price_item_map[key]:
            span["priceitem"] = f"{BASE_URL}PriceItem/{price_item_map[key]}/"

    # print(f"price_spans:{price_spans[:5]}")

    # Етап 4: Масово създаваме `PriceSpan` на части
    for batch in chunkify(price_spans, BULK_SIZE):
        bulk_create_price_spans(batch)











