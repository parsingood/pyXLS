import cx_Oracle
import datetime
import requests

# Конфигурация за Oracle
lib_dir = r"C:\app\instantclient_19_19"  # Път до Oracle Instant Client
oracle_host = "10.10.21.33"
oracle_port = "1521"
service_name = "opera"
username = "opera"
password = "opera"

# Конфигурация за Parsing API
api_base_url = "https://portal.parsing.eu/api/"
token = "2dda759d18dc8a6c232e5065a35d9c89d0282024"
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

hotels='''
 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
'''

room_type_names = {('Althea','M2'):'One-bedroom maisonette',
('Althea','M4'):'Two-bedroom maisonette',
('Althea','DB'):'Double Room',
('Althea','DBI'):'Interconnected room',
('Arabela Beach','A22'):'One-bedroom aparatment with Park view',
('Arabela Beach','H22SEA'):'One-bedroom aparatment with Sea view',
('Arabela Beach','DB'):'Standard Room Seaside view',
('Arabela Beach','DBPN'):'Economy room',
('Arabela Beach','H12FSE'):'Standard Room Seaside view',
('Arabela Beach','H12PAN'):'Standard Room Seaside view',
('Arabela Beach','H12TOP'):'Standard Room Seaside view',
('Arabela Beach','A2'):'Standard room with kitchenette Park view',
('Arabela Beach','DBL'):'Standard room Large with Seaside view',
('Arabela Beach','DBN'):'Standard room Large no balcony',
('Arabela Beach','DBS'):'Standard room Large with Park view',
('Boryana','A4'):'Two-bedroom apartament with Sea view',
('Boryana','A2'):'One-bedroom apartament with Sea view',
('Boryana','DB'):'Double Room with Sea view',
('Boryana','DBI'):'Interconnected room',
('Boryana','DBL'):'Double Room (2+2)',
('Boryana','SG'):'Single room with Sea view',
('Boryana','DBP'):'Double Room with Park view',
('Boryana','DBPN'):'Economy room',
('Boryana','SGP'):'Single room with Park view',
('Paradise Blue','A2'):'One-bedroom apartment with Sea view',
('Paradise Blue','A2VIP'):'One-bedroom VIP apartment with Sea view',
('Paradise Blue','A2P'):'One-bedroom apartment with Park view',
('Paradise Blue','DBVIP'):'Executive room with Sea view',
('Paradise Blue','POOL'):'Deluxe room with shared Pool',
('Paradise Blue','DB'):'Deluxe room  with Sea view',
('Paradise Blue','DBS'):'Deluxe room with Seaside view',
('Paradise Blue','DBPVIP'):'Executive room with Park view',
('Paradise Blue','DBP'):'Deluxe room  with Park view',
('Paradise Blue','SG'):'Single room',
('Paradise Blue','SGP'):'Single room with Park view',
('Paradise Blue','ST'):'Deluxe Studio with Sea view',
('Paradise Blue','ST'):'Deluxe Studio with Sea view',
('Paradise Blue','STVIP'):'Executive Studio with Sea view',
('Amelia','A2PVIP'):'Executive apartment Park side',
('Amelia','A4N'):'Two-bedroom apartment with Graden view',
('Amelia','A2P'):'Deluxe apartment Park side ',
('Amelia','DBVIP'):'Executive room with Sea view',
('Amelia','DB'):'Deluxe room with Sea view',
('Amelia','DBP'):'Double Room with Park view',
('Amelia','DBS'):'Deluxe room with Garden view ',
('Kaliakra Mare','A2'):'One-bedroom apartment',
('Kaliakra Mare','DB'):'Double room',
('Kaliakra Mare','DBI'):'Interconnected room',
('Kaliakra Mare','DBN'):'Double Room (2+2)',
('Kaliakra Mare','SG'):'Single room',
('Kaliakra Mare','SGP'):'Single room',
('Kaliakra Mare','DBPN'):'Economy room',
('Elitsa','A2'):'One-bedroom apartment with Sea view',
('Elitsa','DB'):'Double Room with Sea view',
('Elitsa','DBI'):'Interconnected room',
('Elitsa','SG'):'Single room',
('Elitsa','DBN'):'Double Room with Sea view (2+2)',
('Elitsa','DBP'):'Double Room with Park view',
('Elitsa','DBPN'):'Economy room',
('Flamingo','M4'):'Maisonette',
('Flamingo','H12-2X'):'Double room',
('Flamingo','H12POL'):'Double room pool view',
('Flamingo','SG'):'Single room',
('Flamingo','SGP'):'Single room economy',
('Flamingo Grand','PENT'):'Penthouse Azure',
('Flamingo Grand','PENTCO'):'Penhouse Sunrise/Sunset',
('Flamingo Grand','STEXEC'):'Studio Executive',
('Flamingo Grand','SUCORN'):'Corner Suite',
('Flamingo Grand','GRAP'):'Apartment Grand Superior',
('Flamingo Grand','GRME'):'Maisonettes Grand Superior',
('Flamingo Grand','ST'):'Studio Standard',
('Flamingo Grand','STDELX'):'Studio Deluxe',
('Flamingo Grand','STSUP'):'Studio Superior',
('Flamingo Grand','SUPAN'):'Panorama Superior Suite',
('Gergana','A2'):'One-bedroom apartment with Sea view',
('Gergana','A4'):'Two-bedroom apartament with Sea view',
('Gergana','SUSEA'):'Studio with Sea view',
('Gergana','DBVIP'):'Superior Room with Sea view',
('Gergana','M2'):'Maisonette with Sea view',
('Gergana','DB'):'Double Room with Sea view',
('Gergana','SG'):'Single room',
('Gergana','DBH'):'Superior Room with Sea view',
('Gergana','DBP'):'Double Room with Park view',
('Gergana','DBPN'):'Economy room',
('Gergana','SGP'):'Single room',
('Gergana','DBN'):'Double Room with River view',
('Gergana','DBF'):'Double room with bunk beds',
('Gergana','DBI'):'Interconnected room',
('Gergana','SURIV'):'Studio with Riverside view',
('Kaliakra','A4'):'Two-bedroom apartament with Sea view',
('Kaliakra','DB'):'Double Room with Sea view',
('Kaliakra','DBPN'):'Economy room',
('Kaliakra','DBL'):'Superior Room with Sea view',
('Kaliopa','A12-2X'):'Double room with kitchenette with Sea view',
('Kaliopa','A12-2C'):'Double room with kitchenette with Sea view',
('Kaliopa','A12LRG'):'Large room with kitchenette with Park view',
('Kaliopa','A22-3X'):'Studio with kitchenette Sea view',
('Kaliopa','A4'):'Two-bedroom apartament with Sea view',
('Kaliopa','H12LRX'):'Double Room with Park view',
('Kaliopa','H12LRG'):'Double Room with Park view',
('Kaliopa','H12-2C'):'Double Room with Sea view',
('Kaliopa','H12'):'Economy room',
('Kaliopa','H12-2X'):'Double room with bunk beds Sea view',
('Com','DB'):'Double Room',
('Com','SG'):'Single room',
('Com','DBPN'):'Economy room',
('Kompas','A2'):'One-bedroom apartment',
('Kompas','DB'):'Double Room',
('Kompas','DBI'):'Interconnected room',
('Kompas','SG'):'Single room',
('Laguna Beach','ST'):'Studio',
('Laguna Beach','DB'):'Double room Seaside view',
('Laguna Beach','DBI'):'Interconnected room',
('Laguna Beach','DBIST'):'Studio Interconnected',
('Laguna Beach','DBN'):'Double room with bunk beds',
('Laguna Beach','DBPN'):'Economy room',
('Laguna Beach','SG'):'Single room',
('Laguna Beach','DBL'):'Deluxe room',
('Laguna Garden','ST'):'Studio',
('Laguna Garden','DB'):'Double Room',
('Laguna Garden','DBF'):'Double room with bunk beds',
('Laguna Garden','DBI'):'Interconnected room',
('Laguna Garden','DBIST'):'Studio Interconnected',
('Laguna Garden','SG'):'Single room',
('Laguna Mare','ST'):'Studio',
('Laguna Mare','DB'):'Double Room',
('Laguna Mare','DBI'):'Interconnected room',
('Laguna Mare','DBIST'):'Studio Interconnected',
('Laguna Mare','DBPN'):'Economy room',
('Laguna Mare','SG'):'Single room',
('Laguna Mare','DBN'):'Double room with bunk beds',
('Magnolia','DB'):'Double room Plus',
('Magnolia','DBI'):'Interconnected room',
('Magnolia','SG'):'Single room',
('Magnolia','DBP'):'Double room Standard',
('Malibu','DB'):'Double Room',
('Malibu','DBI'):'Interconnected room',
('Malibu','SG'):'Single room',
('Malibu','DBPN'):'Economy room',
('Mura','A4'):'Two-bedroom apartament with Sea view',
('Mura','A2'):'One-bedroom apartment with Sea view',
('Mura','DB'):'Double Room with Sea view',
('Mura','DBI'):'Interconnected room',
('Mura','SG'):'Single room',
('Mura','DBN'):'Double Room with bunk beds',
('Mura','DBP'):'Double Room with Park view',
('Mura','DBPI'):'Interconnected room',
('Mura','DBPN'):'Economy room',
('Mura','SGP'):'Single room with Park view',
('Nona','A4'):'Two-bedroom apartament with Sea view',
('Nona','A2'):'One-bedroom apartment with Sea view',
('Nona','DB'):'Double Room with Sea view',
('Nona','DBI'):'Interconnected room',
('Nona','DBL'):'Double Room (2+2)',
('Nona','SG'):'Single room',
('Nona','DBN'):'Double room with bunk beds',
('Nona','DBP'):'Double Room with Park view',
('Nona','DBPN'):'Economy room',
('Nona','SGP'):'Single room',
('Oasis','DB'):'Double Room',
('Oasis','DBI'):'Interconnected room',
('Oasis','SG'):'Single room',
('Oasis','DBL'):'Double Room (2+2)',
('Orchidea','A4'):'Two-bedroom apartament',
('Orchidea','DB'):'Double Room',
('Orchidea','DBI'):'Interconnected room',
('Orchidea','DBL'):'Double Room',
('Orchidea','SG'):'Single room',
('Orchidea Park','DB'):'Double Room',
('Orchidea Park','DBI'):'Interconnected room',
('Orchidea Park','SG'):'Single room',
('Sandy Beach','DB'):'Double Room',
('Sandy Beach','DBI'):'Interconnected room',
('Sandy Beach','DBN'):'Double room with bunk beds',
('Sandy Beach','SG'):'Single room',
('Sandy Beach','DBL'):'Superior Room',
('Panorama','A4'):'Two-bedroom apartament',
('Panorama','M4'):'Maisonette',
('Panorama','DB'):'Double Room',
('Panorama','DBI'):'Interconnected room',
('Ralitsa Aquaclub','A2'):'One-bedroom apartment',
('Ralitsa Aquaclub','A4L'):'Villa',
('Ralitsa Aquaclub','DB'):'Double Room',
('Ralitsa Aquaclub','DBN'):'Double Room (2+2)',
('Ralitsa Aquaclub','SG'):'Single room',
('Ralitsa Aquaclub','SUGAR'):'Double room first floor',
('Ralitsa Aquaclub','DBI'):'Interconnected room',
('Slavuna','A2'):'One-bedroom apartment with Sea view',
('Slavuna','A4'):'Two-bedroom apartament with Sea view',
('Slavuna','M2'):'Maisonette',
('Slavuna','DB'):'Double Room with Sea view',
('Slavuna','DBPN'):'Economy room',
('Ralitsa Superior','A2L'):'One-bedroom apartment Deluxe',
('Ralitsa Superior','A2'):'Calimera Room',
('Ralitsa Superior','DB'):'Double Room Main Building',
('Ralitsa Superior','DBI'):'Interconnected room',
('Ralitsa Superior','DBPN'):'Economy room',
('Ralitsa Superior','SG'):'Single room',
('Ralitsa Superior','DBP'):'Double room Graden (economy)',
('Ralitsa Superior','DBIL'):'Interconnected Room Deluxe',
('Ralitsa Superior','DBL'):'Double Room Deluxe',
('Vitapark','A2'):'One-bedroom apartment',
('Vitapark','A4'):'Villa',
('Vitapark','DB'):'Double Room',
('Vitapark','DBI'):'Interconnected room',
('Vitapark','DBPN'):'Economy room',
('Vitapark','SG'):'Single room',
('Vili Magnolia','A4'):'Villa',

('Arabela Beach','H12FSE'):'Standard Front Sea',
('Arabela Beach','H12PAN'):'Standard Panorama',
('Arabela Beach','H12TOP'):'Standard Top',

('Kaliakra Mare','SGP'):'Single room Park view',
('Flamingo','A22-3X'):'A22-3X',

('Gergana','DBH'):'Superior Room Sea view High',
('Gergana','SGP'):'Single room Park view',
('Kaliopa','A12-2X'):'Double room with kitchenette with Sea view X',
('Kaliopa','H12LRX'):'Double Room with Park view X',
('Mura','DBPI'):'Interconnected room Park view',
('Nona','SGP'):'Single room Park view',
('Oasis','DB'):'Double Room',
('Oasis','DBI'):'Interconnected room',
('Oasis','SG'):'Single room',
('Oasis','DBL'):'Double Room (2+2)',
('Orchidea','DBL'):'Double Room L',

}

# Функция за вземане на списък с хотели от API-то
# def get_hotels():
    # response = requests.get(f"{api_base_url}Hotel/", headers=headers)
    # if response.status_code == 200:
        # return {hotel["code"]: hotel["id"] for hotel in response.json()["results"]}
    # return {}

def get_hotels():
    hotels = {}
    url = f"{api_base_url}Hotel/"
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {}

        data = response.json()
        for hotel in data["results"]:
            if hotel["code"]:  # Проверка, за да избегнем null ключове
                hotels[hotel["code"]] = hotel["id"]

        url = data.get("next")  # Взимаме следващия URL, ако има такъв

    return hotels


# Функция за създаване на хотел в API-то
def create_hotel(hotel_pms, hotel_name):
    data = {
        "name": f"ALBENA - {hotel_name}",
        "name_pms": hotel_pms,
        "code": hotel_pms,
        "place": None,
        "corp": "https://portal.parsing.eu/api/Corp/21/",
        "last_update": None,
        "update_delay_seconds": 180,
        "valid_to": None,
        "valid_done_steps": 0,
        "valid_step_seconds": 120,
        "valid_lull_after": 5,
        "valid_end_minutes": 90
    }
    response = requests.post(f"{api_base_url}Hotel/", headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"Failed to create hotel {hotel_pms}. Response: {response.status_code}, {response.text}")
        return None

# Функция за вземане на списък със стаи на даден хотел
def get_hotel_rooms(hotel_id):
    response = requests.get(f"{api_base_url}Room/?hotel={hotel_id}", headers=headers)
    if response.status_code == 200:
        return {room["code"] for room in response.json()["results"]}
    return set()

# Свързване към Oracle базата и изтегляне на данни
cx_Oracle.init_oracle_client(lib_dir=lib_dir)
print('Started at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

dsn_tns = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=service_name)
try:
    with cx_Oracle.connect(user=username, password=password, dsn=dsn_tns) as connection:
        print("Successfully connected to the Oracle database.\n")
        with connection.cursor() as cursor:
            sql_query = f"""
                SELECT 
                    R.RESORT AS hotel_id, 
                    RC.SHORT_DESCRIPTION AS room_type, 
                    RC.LABEL AS room_type_id,
                    RC.MAX_OCCUPANCY AS max_pax,
                    RC.MAX_OCCUPANCY_ADULTS AS max_ad,
                    RC.MAX_OCCUPANCY_CHILDREN AS max_ch,
                    R.SEASON2 AS hotel_name
                FROM 
                    RESORT$_ROOM_CATEGORY RC
                JOIN 
                    RESORT R 
                ON 
                    R.RESORT = RC.RESORT
                WHERE 
                    (RC.LABEL NOT IN ('PI','PM','CATERING'))  
                    AND R.RESORT IN ({hotels}) 
                    AND RC.NUMBER_ROOMS <> 0
                ORDER BY 
                    R.RESORT, RC.ROOM_CLASS, RC.LABEL
            """
            cursor.execute(sql_query)
            result = cursor.fetchall()
            print(f"Found {len(result)} room types.\n")

            parsing_hotels = get_hotels()
            print(parsing_hotels)
            
            for row in result:
                hotel_pms = row[0]

                room_type_id = row[2]
                max_pax = row[3] if row[3] else 3
                max_ad = row[4] if row[4]  else 3
                max_ch = row[5] if row[5]  else 2
                hotel_name = row[6]
                
                room_type = room_type_names.get((hotel_name,room_type_id))
                if not room_type:
                    continue
                    room_type = row[1]                
                
                hotel_id = parsing_hotels.get(hotel_pms)
                if not hotel_id:
                    print(f"Hotel {hotel_pms} not found in Parsing API, creating it...")
                    hotel_id = create_hotel(hotel_pms, hotel_name)
                    parsing_hotels = get_hotels()
                    if not hotel_id:
                        print(f"Skipping room {room_type} as hotel {hotel_pms} could not be created.")
                        continue

                existing_rooms = get_hotel_rooms(hotel_id)
                if room_type_id in existing_rooms:
                    print(f"Room {room_type} ({room_type_id}) already exists for hotel {hotel_pms}, skipping.")
                    continue
                
                data = {
                    "hotel": f"{api_base_url}Hotel/{hotel_id}/",
                    "name": room_type,
                    "code": room_type_id,
                    "name_pms": room_type_id,
                    "rang": 1,
                    "size": 1,
                    "is_active": True,
                    "min_pax": 1,
                    "max_pax": max_pax,
                    "min_ad": 1,
                    "max_ad": max_ad,
                    "min_ch": 0,
                    "max_ch": max_ch,
                    "ex_inf": 0,
                    "regular_beds": 2,
                    "extra_beds": 1
                }
                
                response = requests.post(f"{api_base_url}Room/", headers=headers, json=data)
                if response.status_code == 201:
                    print(f"Successfully added room type: {room_type} (ID: {room_type_id})")
                else:
                    print(f"Failed to add room type: {room_type} (ID: {room_type_id})")
                    print("Response:", response.status_code, response.text)

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print("Database connection failed!")
    print("Error code:", error.code)
    print("Error message:", error.message)

print("\nScript finished.")
