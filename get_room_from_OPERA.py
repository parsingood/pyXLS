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
                    R.SEASON2 AS hotel, 
                    RC.SHORT_DESCRIPTION AS room_type, 
                    RC.LABEL AS room_type_code,
                    nvl(T.ROOM_CLASS,' ') main,
                    RC.ROOM_CLASS class,
                    RC.MAX_OCCUPANCY MAX_PAX  ,MAX_OCCUPANCY_ADULTS MAX_AD  ,MAX_OCCUPANCY_CHILDREN MAX_CH
                FROM 
                    OPERA.RESORT$_ROOM_CATEGORY RC
                JOIN 
                    OPERA.RESORT R 
                ON 
                    R.RESORT = RC.RESORT
                LEFT JOIN TRAIN.ALB_MAIN_ROOM_CLASS_TYPES T
                ON 
                    T.RESORT = RC.RESORT
                    AND T.MAIN_ROOM_TYPE_LABEL = RC.LABEL
                WHERE 
                    (RC.LABEL NOT IN ('PI','PM','CATERING'))  
                    AND R.RESORT IN ({hotels}) 
                    AND RC.NUMBER_ROOMS <> 0
                ORDER BY 
                    R.RESORT, RC.ROOM_CLASS, T.ROOM_CLASS, RC.LABEL
            """
            cursor.execute(sql_query)

            # Извличане на колоните (хедърите)
            headers = [desc[0] for desc in cursor.description]

            # Извличане на резултатите
            result = cursor.fetchall()

            # Принтиране на резултатите с хедърите
            print("\t".join(headers))  # Печат на заглавния ред
            for row in result:
                print("\t".join(map(str, row)))  # Печат на всеки ред от резултата
 

            # Запис във файл
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write("\t".join(headers) + "\n")  
                for row in result:
                    f.write("\t".join(map(str, row)) + "\n")

         

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print("Database connection failed!")
    print("Error code:", error.code)
    print("Error message:", error.message)

print("\nScript finished.")
