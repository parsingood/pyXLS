import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import datetime 
import cx_Oracle

# Днес и вчера
today = datetime.date.today()
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday_day = yesterday.strftime("%d.%m %a")

sender_email = "ivanm.albena@gmail.com"
sender_password = "npdkxrfpkmiwqmng" 
mailserver = "smtp.gmail.com"


to_email = "marinela.tsaneva@albena.bg"
receiver_email = ["ivanm@albena.bg", "marinela.tsaneva@albena.bg","marin.linchev@albena.bg"]
# receiver_email = ["ivanm@albena.bg"]
subject = f"Нощувки към {yesterday_day}"
body = "Приложена е справката за нощувките."

# Списъци с хотели
HOTELS = [('''
'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
''','Albena'),
(''' 'MUR' ''','White Lagoon'),
(''' 'MGS', 'ROP', 'HOL', 'NEP' ''','Primorsko'),
]

HOTELS = [(''' 'FLG' ''','Albena'),
]

HOTELS = [(''' 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'FLG', 
'FLA','SUP', 'RAL' ''','Albena'),
]

# Период за справката

start_date = datetime.date(2024, 12, 13)
end_date = datetime.date(2025, 3, 31)

start_date = datetime.date(2025, 4, 17)
end_date = datetime.date(2025, 5, 24)

# нощувки или стаи: 'pax' или 'rooms'
paxrooms='rooms'


#към коя дата
ISSUE_DATE=today.strftime('%Y%m%d')
#ISSUE_DATE=datetime.date(2025, 1, 5).strftime('%Y%m%d')

# име на прикачени файл
filename='HotelNightStays.xlsx'
#filename='DecemberStays.xlsx'

# Речник с кодовете на хотелите и съответните имена и стаи
hotel_info = {
    "GER": ("GERGANA", 318),
    "MRA": ("MURA", 186),
    "SLA": ("SLAVUNA", 128),
    "ELI": ("ELITSA", 176),
    "NON": ("NONA", 176),
    "BOR": ("BORIANA", 176),
    "LAB": ("LAGUNA BEACH", 189),
    "LAM": ("LAGUNA MARE", 155),
    "LAG": ("LAGUNA GARDEN", 145),
    "KLP": ("KALIOPA", 141),
    "ARB": ("ARABELA BEACH", 108),
    "KLK": ("KALIAKRA", 272),
    "DTC": ("DOBROTIZA", 148),
    "ORL": ("SANDY BEACH", 163),
    "MAL": ("MALIBU", 157),
    "DOR": ("MARITIM PARADISE", 238),
    "DRU": ("MARITIM AMELIA", 141),
    "OAS": ("OASIS", 162),
    "FLG": ("FLAMINGO GRAND", 263),
    "FLA": ("FLAMINGO", 186),
    "OR1": ("ORCHIDEA", 210),
    "MAG": ("MAGNOLIA", 340),
    "SUP": ("RALITSA SUPER.", 342),
    "RAL": ("RALITSA", 341),
    "VIT": ("VITAPARK", 268),
    "KPS": ("KOMPAS", 169),
    "VMG": ("VILI MAGNOLIA", 84),
    "GOR": ("GORSKA FEA", 196),
    "ARA": ("VILLA ALBENA", 1),
    "MUR": ("WHITE LAGOON", 305),
    "MGS": ("LES MAGNOLIAS", 190),
    "ROP": ("ROPOTAMO", 77),
    "HOL": ("HOLIDAY", 106),
    "NEP": ("NEPTUN", 189),
    "KED": ("KEDAR", 93),
    "BIS": ("BISER", 163),
    "DDJ": ("DOBRUDJA", 286),
    "OR2": ("ORCHIDEA PARK", 187),
    "KOM": (".COM", 327),
    "ALT": ("ALTHEA", 200),
    "PAN": ("PANORAMA", 169),
    "BRI": ("BRIGANTINA", 141),
    "LOR": ("LORA", 0),
    "MGG": ("AMELIA SUPERIOR", 40),
    "BRB": ("BOR", 60),
    "EDW": ("EDELWEISS", 71),
    "BLK": ("BALKAN", 68),
    "MSQ": ("DES MASQUES", 40),
    "LAZ": ("LAZUR", 96),
    "KML": ("KAMELIA", 60),
    "KDM": ("KARDAM", 172),
    "DNE": ("DNEPAR", 36),
    "VZA": ("VILI ZAPAD", 54),
    "WLA": ("WHITE LAGOON", 83)
}

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

cx_Oracle.init_oracle_client(lib_dir=r"C:\\app\\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera')

# Създаване на колони за дните в избрания период
date_columns = []
date_sums = []
date_conditions = []
date_str_list = []
total_column_indices = []  # Запомня индекси на колоните за тоталите
current_date = start_date
col_index = 3  # Започваме от 4-та колона (0-базиран индекс)
while current_date <= end_date:
    date_str = current_date.strftime('%d_%m')
    date_str_list.append(date_str)
    date_columns.append(f"SUM(CASE WHEN the_date = TO_DATE('{current_date.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) AS \"{date_str}\"")
    date_sums.append(f"SUM({date_str})")
    date_conditions.append(f"SUM(CASE WHEN the_date = TO_DATE('{current_date.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0")
    total_column_indices.append(col_index)
    col_index += 1
    current_date += datetime.timedelta(days=1)

columns_sql = ", ".join(date_columns)
conditions_sql = " OR ".join(date_conditions)


sql = f'''
SELECT RESORT "Хотел", TourOperator "Туроператор", {columns_sql}
FROM (
    SELECT RESORT, SR.COMPANY TourOperator, RESERVATION_DATE the_date, SUM({paxrooms}) paxrooms
    FROM train.ALB_OCCUPANCY_RATE_JURNAL e
    LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID = SR.NAME_ID
    WHERE e.ISSUE_DATE = TO_DATE('{ISSUE_DATE}', 'YYYYMMDD')
     AND  e.RESERVATION_DATE BETWEEN 
            TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
        AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
        AND e.RESORT IN ({HOTELS[0][0]})
        AND SR.COMPANY not in ('GUARANTEE ALLOTENTS')
    GROUP BY RESORT, SR.COMPANY, RESERVATION_DATE
)
GROUP BY RESORT, TourOperator
HAVING {conditions_sql}
ORDER BY RESORT, TourOperator
'''


# Генериране на Excel файла
workbook = xlsxwriter.Workbook(f'C:/test/{filename}')
header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
border_format = workbook.add_format({'border': 1})
total_format = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D9EAD3'})

# Свързване с базата
db_conn = cx_Oracle.connect(user='opera', password='opera', dsn=dsn_tns)
cursor = db_conn.cursor()
cursor.execute(sql)

date_header = ["Код", "Име на Хотел", "Туроператор"] + date_str_list
worksheet = workbook.add_worksheet("Night Stays")
worksheet.freeze_panes(1, 3)  # Замразяване на колоните
worksheet.write_row(0, 0, ["Код", "Име на Хотел", "Туроператор"] + [desc[0] for desc in cursor.description[2:]], header_format)
worksheet.set_column(0, 0, 10)  # Ширина за кода на хотела
worksheet.set_column(1, 1, 30)  # Увеличена ширина за името на хотела
worksheet.set_column(2, 2, 30)  # Ширина за туроператора
worksheet.set_column(3, len(total_column_indices) + 2, 6)  # Намалена ширина за останалите колони


row = 0
total_room_count = 0
total_sums = [0] * len(date_str_list)
worksheet.write_row(row, 0, date_header, header_format)
row += 1

total_row_start = row  # Запазва началния ред за текущия хотел
previous_hotel = None
previous_room_count = 0

print([desc[0] for desc in cursor.description])
data = cursor.fetchall()
for db_row in data:
    hotel_code = db_row[0]
    if hotel_code in hotel_info:
        hotel_name, room_count = hotel_info[hotel_code]
    else:
        hotel_name, room_count = "Unknown", 0

    if previous_hotel and previous_hotel != hotel_code:

        # Вмъкване на тоталния ред
        total_row_values = [previous_hotel, hotel_info.get(previous_hotel, ("Unknown", 0))[0], f"TOTAL ROOMS: {previous_room_count}"] + [f"=SUM({xl_rowcol_to_cell(total_row_start, col)}:{xl_rowcol_to_cell(row-1, col)})" for col in total_column_indices]
        worksheet.write_row(row, 0, total_row_values, total_format)
        row += 1
        worksheet.write_row(row, 0, ["" for _ in range(len(db_row) + 1)])  # Празен ред
        row += 1
        worksheet.write_row(row, 3, date_str_list, header_format)  # Добавяне на ред с датите
        row += 1
        total_row_start = row
        
        total_room_count += previous_room_count

    worksheet.write_row(row, 0, [hotel_code, hotel_name] + list(db_row[1:]), border_format)
    

    # print(f"Row length: {len(db_row)}, Expected: {len(total_sums) + 3}")
    # print(f"db_row: {db_row}")
    total_sums = [total_sums[i] + (db_row[i+2] if isinstance(db_row[i+2], int) else 0) for i in range(len(total_sums))]    
    # total_sums = [
    # total_sums[i] + (db_row[i+3] if (i+3) < len(db_row) and isinstance(db_row[i+3], int) else 0) 
    # for i in range(min(len(total_sums), len(db_row) - 3))
# ]
    
    row += 1
    previous_hotel = hotel_code
    previous_room_count = room_count

# Последен тотал
if previous_hotel:
    hotel_name, room_count = hotel_info.get(previous_hotel, ("Unknown", 0))
    total_row_values = [previous_hotel, hotel_name, f"TOTAL ROOMS: {previous_room_count}"] + [f"=SUM({xl_rowcol_to_cell(total_row_start, col)}:{xl_rowcol_to_cell(row-1, col)})" for col in total_column_indices] 
    worksheet.write_row(row, 0, total_row_values, total_format)
    total_room_count += previous_room_count

# Добавяне на последния тотален ред
row += 1
row += 1
worksheet.write_row(row, 0, ["" for _ in range(len(db_row) + 1)])  # Празен ред
row += 1
worksheet.write_row(row, 3, date_str_list, header_format)  # Добавяне на ред с датите
row += 1
final_total_row = ["", "GRAND TOTAL", f"GRAND TOTAL ROOMS: {total_room_count}"] + total_sums
worksheet.write_row(row, 0, final_total_row, total_format)

row += 1
row += 1
worksheet.write_row(row, 0, ["At:", today.strftime("%d.%m.%Y %a")], total_format)

workbook.close()
db_conn.close()

# Изпращане на справката по имейл
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

with open(f'C:/test/{filename}', "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")
    message.attach(part)

#with smtplib.SMTP_SSL("mail.wservices.ch", 465) as server:
#    server.login(sender_email, sender_password)
#    server.sendmail(sender_email, receiver_email, message.as_string())

server = smtplib.SMTP_SSL("smtp.gmail.com")
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_email , text)


print('Finished at ' + datetime.datetime.now().strftime("%A, %d.%m.%Y %X") + '\n')

