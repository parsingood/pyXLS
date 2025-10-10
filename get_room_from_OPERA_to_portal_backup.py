import cx_Oracle
import datetime
import requests

# Конфигурация за Oracle
lib_dir = r"C:\app\instantclient_19_19"  # Път до Oracle Instant Client
oracle_host = "10.10.21.33"
oracle_port = "1521"
service_name = "opera"
username = "opera"  # Потребителско име за Oracle
password = "opera"  # Парола за Oracle

# Конфигурация за Parsing API
api_url = "https://portal.parsing.eu/api/Room/"
token = "2dda759d18dc8a6c232e5065a35d9c89d0282024"  # Вашият токен за достъп

hotels='''
 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
'''


headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

# Инициализиране на Oracle клиента
cx_Oracle.init_oracle_client(lib_dir=lib_dir)

print('Started at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

# Създаване на DSN (Data Source Name)
dsn_tns = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=service_name)

# Свързване към базата данни и изтегляне на данни
try:
    with cx_Oracle.connect(user=username, password=password, dsn=dsn_tns) as connection:
        print("Successfully connected to the Oracle database.\n")
        
        # Създаване на курсор и изпълнение на заявката
        with connection.cursor() as cursor:
            sql_query = f"""
                SELECT 
                    R.RESORT AS hotel_id, 
                    RC.SHORT_DESCRIPTION AS room_type, 
                    RC.LABEL AS room_type_id,
                    RC.MAX_OCCUPANCY MAX_PAX  ,MAX_OCCUPANCY_ADULTS MAX_AD  ,MAX_OCCUPANCY_CHILDREN MAX_CH 
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

            # Обработка на резултатите
            result = cursor.fetchall()
            print(f"Found {len(result)} room types.\n")
            
            for row in result:
                hotel_id = 31 # row[0]
                room_type = row[1]
                room_type_id = row[2]

                # Данни за POST заявка към Parsing API
                data = {
                    "hotel": f"https://portal.parsing.eu/api/Hotel/{hotel_id}/",
                    "name": room_type,
                    "code": room_type_id,
                    "name_pms": room_type,
                    "rang": 1,
                    "size": 30,
                    "is_active": True,
                    "min_pax": 1,
                    "max_pax": 3,
                    "min_ad": 1,
                    "max_ad": 2,
                    "min_ch": 0,
                    "max_ch": 1,
                    "ex_inf": 0,
                    "regular_beds": 2,
                    "extra_beds": 1
                }

                # Изпращане на данни към Parsing API
                response = requests.post(api_url, headers=headers, json=data)

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
