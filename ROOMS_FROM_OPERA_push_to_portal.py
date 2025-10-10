import requests
import cx_Oracle
import datetime

# Настройки
BASE_URL = "https://portal.parsing.eu/api/"
TOKEN = "2dda759d18dc8a6c232e5065a35d9c89d0282024"
HEADERS = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
BULK_SIZE = 200  # По-малък размер, защото JSON обектите ще са по-големи

DATE_FROM = datetime.datetime.now().date().strftime("%d%m%Y")  # '19062025'  # DDMMYYYY

# Получаване на хотелските кодове
hotel_map = {}
map_hotel = {}
offset = 0
while True:
    hotels_api = requests.get(BASE_URL + f"Hotel/?corp__name=ALBENA&limit=50&offset={offset}", headers=HEADERS).json()
    if not hotels_api["results"]:
        break
    for h in hotels_api["results"]:
        hotel_map[h["id"]] = h["code"]
        map_hotel[h["code"]] = h["id"]
    offset += 50

# Получаване на стаите
room_map = {}
offset = 0
while True:
    rooms_api = requests.get(BASE_URL + f"Room/?hotel__corp__name=ALBENA&limit=50&offset={offset}", headers=HEADERS).json()
    if not rooms_api["results"]:
        break
    for r in rooms_api["results"]:
        hotel_code = hotel_map.get(int(r["hotel"].split("/")[-2]))
        if hotel_code:
            room_map[(hotel_code, r["name_pms"])] = r["code"]
    offset += 50

print(hotel_map)
print(map_hotel)

#print(room_map)
#exit()


# Oracle връзка
cx_Oracle.init_oracle_client(lib_dir=r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA')
conn = cx_Oracle.connect(user='OPERA', password='opera', dsn=dsn_tns)
cursor = conn.cursor()

# SQL заявка за наличности
# trunc(current_date, 'DD') 
sql = f"""
WITH ExistingRooms AS (
    SELECT 
        t.resort, 
        to_number(t.ROOM_CATEGORY) ROOM_CATEGORY, 
        t.ROOM_CLASS, 
        t.LABEL,  
        COUNT(*) AS ROOMS
    FROM opera.room r 
    JOIN OPERA.RESORT$_ROOM_CATEGORY t 
        ON t.resort = r.resort 
        AND t.ROOM_CATEGORY = r.ROOM_CATEGORY
        AND t.ROOM_CATEGORY > 0
    GROUP BY t.resort, t.ROOM_CATEGORY, t.ROOM_CLASS, t.LABEL
),
Avail AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        av.ROOM_CLASS,  
        to_number(av.ROOM_CATEGORY) ROOM_CATEGORY,
        av.AVAIL
    FROM TRAIN.ALB_RESV_AVAILABILITY av
    WHERE av.ROOM_CATEGORY > 0 
    AND av.THE_DATE BETWEEN TO_DATE('{DATE_FROM}','DDMMYYYY') AND trunc(current_date, 'DD') + 365
    AND av.resort in (
      'GER', 'MRA', 'SLA', 'ELI', 
      'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
      'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 
      'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
      'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 
      'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 
      'PAN', 'VMG') 
    AND EXISTS ( 
      SELECT 1 FROM TRAIN.ALB_HOTEL_OPENCLOSE H 
      WHERE H.RESORT = av.resort AND H.OPEN_DATE <= av.THE_DATE AND av.THE_DATE <= H.CLOSE_DATE
    )
     
),
Avail_Exist AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        av.ROOM_CATEGORY, 
        av.AVAIL
    FROM Avail av
    JOIN ExistingRooms e 
        ON av.resort = e.resort 
        AND av.ROOM_CATEGORY = e.ROOM_CATEGORY
),
MissAvail AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        av.ROOM_CLASS,  
        av.ROOM_CATEGORY, 
        av.AVAIL
    FROM Avail av
    LEFT JOIN ExistingRooms e 
        ON av.resort = e.resort 
        AND av.ROOM_CATEGORY = e.ROOM_CATEGORY
    WHERE e.ROOM_CATEGORY IS NULL
),
Avail_InMain AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        m.MAIN_ROOM_CATEGORY AS ROOM_CATEGORY, 
        av.AVAIL
    FROM MissAvail av
    JOIN train.ALB_MAIN_ROOM_CLASS_TYPES m 
        ON m.RESORT = av.resort 
        AND m.ROOM_CLASS = av.ROOM_CLASS
    WHERE m.MAIN_ROOM_CATEGORY IS NOT NULL
),
MissAvail_NotInMain AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        av.ROOM_CLASS,  
        av.ROOM_CATEGORY, 
        av.AVAIL
    FROM MissAvail av
    LEFT JOIN train.ALB_MAIN_ROOM_CLASS_TYPES m 
        ON m.RESORT = av.resort 
        AND m.ROOM_CLASS = av.ROOM_CLASS
    WHERE m.MAIN_ROOM_CATEGORY IS NULL
),
ExistingClass AS (
    SELECT 
        e.resort, 
        e.ROOM_CLASS,
        MIN(TO_NUMBER(e.ROOM_CATEGORY)) AS MIN_ROOM_CATEGORY
    FROM ExistingRooms e
    GROUP BY e.resort, e.ROOM_CLASS
),
Avail_InExistClass AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        m.MIN_ROOM_CATEGORY AS ROOM_CATEGORY, 
        av.AVAIL
    FROM MissAvail_NotInMain av
    JOIN ExistingClass m 
        ON m.RESORT = av.resort 
        AND m.ROOM_CLASS = av.ROOM_CLASS
    WHERE m.MIN_ROOM_CATEGORY IS NOT NULL
),
MissAvail_NotInExistClass AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        av.ROOM_CLASS,  
        av.ROOM_CATEGORY, 
        av.AVAIL
    FROM MissAvail_NotInMain av
    LEFT JOIN ExistingClass m 
        ON m.RESORT = av.resort 
        AND m.ROOM_CLASS = av.ROOM_CLASS
    WHERE m.MIN_ROOM_CATEGORY IS NULL
),
DefRoomCategory AS (
    SELECT 
        ex.resort, 
        MIN(ex.ROOM_CATEGORY) AS DEF_ROOM_CATEGORY
    FROM ExistingRooms ex
    GROUP BY ex.resort
),
Avail_NotInExistClass AS (
    SELECT 
        av.RESORT,
        av.the_date, 
        m.DEF_ROOM_CATEGORY AS ROOM_CATEGORY, 
        av.AVAIL
    FROM MissAvail_NotInExistClass av
    JOIN DefRoomCategory m 
        ON m.RESORT = av.resort 
    WHERE m.DEF_ROOM_CATEGORY IS NOT NULL
),
FinalAvailability AS (
    SELECT RESORT, the_date, ROOM_CATEGORY, AVAIL FROM Avail_Exist
    UNION ALL
    SELECT RESORT, the_date, ROOM_CATEGORY, AVAIL FROM Avail_InMain
    UNION ALL
    SELECT RESORT, the_date, ROOM_CATEGORY, AVAIL FROM Avail_InExistClass
    UNION ALL
    SELECT RESORT, the_date, ROOM_CATEGORY, AVAIL FROM Avail_NotInExistClass
)
SELECT 
    f.the_date, 
    f.resort, 
    t.label, 
    f.ROOM_CATEGORY, 
    SUM(f.AVAIL) AS TOTAL_AVAILABLE_ROOMS
FROM FinalAvailability f
LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY t 
    ON t.resort = f.resort 
    AND t.ROOM_CATEGORY = f.ROOM_CATEGORY
GROUP BY f.the_date, f.resort, t.label, t.ROOM_CLASS, f.ROOM_CATEGORY
ORDER BY f.the_date, f.resort, t.ROOM_CLASS

"""
# Извличане на наличностите
cursor.execute(sql)
room_availabilities = cursor.fetchall()

# Групиране на данните по хотел и дата
grouped_data = {}

missing = []

for date, hotel, room_name, room_category, avail in room_availabilities:

    hotel_id = map_hotel.get(hotel)
    room_code = room_map.get((hotel, room_name))
#    print(f'--{hotel_id}--')
#    print(f'--{room_code}--')
#    exit()
    if not hotel_id or not room_code:
        missing.append(f"В хотел {hotel} не е намерена стая {room_name} в API-то!")
        continue

    date_str = date.strftime("%Y-%m-%d")

    if hotel_id not in grouped_data:
        grouped_data[hotel_id] = {}

    if date_str not in grouped_data[hotel_id]:
        grouped_data[hotel_id][date_str] = {"hotel_id": hotel_id, "date": date_str, "rooms": {}}

    grouped_data[hotel_id][date_str]["rooms"][room_code] = avail

# Преобразуване в списък за изпращане
bulk_data = [data for hotel in grouped_data.values() for data in hotel.values()]

# Изпращане на групирани данни на партиди
for i in range(0, len(bulk_data), BULK_SIZE):
    chunk = bulk_data[i:i + BULK_SIZE]
    response = requests.post(BASE_URL + "RoomDate/bulk_create/", json=chunk, headers=HEADERS)
    if response.status_code in [200, 201]:
        print(f"Добавени {len(chunk)} записа в RoomDate.")
    else:
        print(f"Грешка при групово добавяне: {response.status_code} - {response.text}")

# Затваряне на връзката
cursor.close()
conn.close()

missing=list(set(missing))
missing.sort()
# Показване на липсващите стаи
for miss in missing:
    print(miss)
