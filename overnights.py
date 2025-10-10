import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import sys
import datetime
import argparse

import cx_Oracle

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

to_email ="ivanm@albena.bg" #"velina.gyumova@albena.bg",
receiver_email = ["ivanm@albena.bg"]

to_email ="mtodorova@albena.bg"
receiver_email = ["mtodorova@albena.bg","velina.gyumova@albena.bg","ivanm@albena.bg","maya.lazarova@albena.bg"]

#"viktoriya.valkova@albena.bg,"maya.lazarova@albena.bg"

#mailserver = "mail.albena.bg"
directory = "C:/test/"

sender_email = "ivanm.albena@gmail.com"
sender_password = "npdkxrfpkmiwqmng" 
mailserver = "smtp.gmail.com"


# ---- Създаване на Excel файл ----
workbook = xlsxwriter.Workbook(f'C:/test/Overnights-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx')

#Формати
bold = workbook.add_format({'bold': True})
merge_bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
border = workbook.add_format({'border': 1})
border_bold = workbook.add_format({'bold': True, 'border': 1})
# Създаваме формат със светло синкаво-сив фон
border_light_blue = workbook.add_format({
    'bg_color': '#f0f7fa',  # Светло синкаво-сив цвят
    'border': 1,            # Добавяме рамка за видимост
})
border_light_blue_bold = workbook.add_format({
    'bg_color': '#f0f7fa',  # Светло синкаво-сив цвят
    'border': 1,            # Добавяме рамка за видимост
    'bold':     True,
})
border_light_green = workbook.add_format({
    'bg_color': '#d9ead3',  # Светло зелен фон
    'border': 1             # Черна рамка около клетката
})
border_light_green_bold = workbook.add_format({
    'bg_color': '#d9ead3',  # Светлозелен фон (същия като border_light_green)
    'border': 1,            # Черна рамка около клетката
    'bold': True            # Текста да е получер
})


print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')


# Четем аргументите
parser = argparse.ArgumentParser(
    description="Справка за нощувките - общ брой към дадена дата или изменението им от определени дни назад до дадена дата",
    epilog="""Примери: 
    py overnights_months.py --date 2025-04-09 date1 --back 1
    py overnights_months.py --back 1 
    py overnights_months.py --back 7

""",
    add_help=True
)
parser.add_argument('--date', type=str, help="Датата към която правим справката във формат YYYY-MM-DD, this - днешната дата")
parser.add_argument('--back', type=str, help="Дата или брой дни назад, от която правим разликата - ако е дата да е във формат YYYY-MM-DD или число(положително число), ако липсва се дава пълното състояние към дадената дата, а не разликите")
parser.add_argument('--by', type=str, help="По какво да групира: market(s)-total/resort(s)-hotel(s)-agent/source(s)-both/full, ако е подадено market ще групира туроператорите по пазари")
parser.add_argument('--date1', type=str, help="Допълнителна дата 1 за сравнение (формат YYYY-MM-DD), last - днешншя ден в миналата година")
parser.add_argument('--date2', type=str, help="Допълнителна дата 2 за сравнение (формат YYYY-MM-DD), last/end - миналата година - края 10.10")
parser.add_argument('--year1', type=str, help="Година за дата1 (примерно 2024), last - миналата година")
parser.add_argument('--year2', type=str, help="Година за дата2 (примерно 2024 или 2023), last - миналата година")
parser.add_argument('--email', type=str, help="Имели на които да се праща --email mtodorova@albena.bg;velina.gyumova@albena.bg;ivanm@albena.bg;maya.lazarova@albena.bg;marinela.tsaneva@albena.bg")
parser.add_argument('--file', type=str, help="test")

args = parser.parse_args()

# Дати за днес и вчера
today = datetime.date.today()
yesterday = None #today - datetime.timedelta(days=1)


# Имели на които да се праща
if args.email:
    receiver_email = args.email.split(";")
    to_email = receiver_email[0]

# Основна дати
if args.date:
    if args.date == "this" or args.date == "now":
        today = datetime.date.today()
    else:
        try:
            today = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
        except:
            pass

# Датата, спрямо която се гледа разликата до основната дата
if args.back:
    try:
        yesterday = datetime.datetime.strptime(args.back, "%Y-%m-%d").date()
        
    except:
        try:
            yesterday = today - datetime.timedelta(days=int(args.back))
            
        except:
            parser.print_help()
            exit()
       
# Допълнителни дати
today1, today2 = None, None
yesterday1, yesterday2 = None, None

if args.date1:
    if args.date1 == "last" or args.date1 == "prev":
        today1 = datetime.date.today() - datetime.timedelta(days=364) 
    else:
        try:
            today1 = datetime.datetime.strptime(args.date1, "%Y-%m-%d").date()
        except:
            pass




if args.date2:
    
    if args.date2 == "last" or args.date2 == "prev" or args.date2 == "end":
        today2 = datetime.date(datetime.date.today().year - 1, 10, 10)  
    else:
        try:
            today2 = datetime.datetime.strptime(args.date2, "%Y-%m-%d").date()
        except:
            pass


if args.back:
    try:
        back_days = int(args.back)
        if today1:
            yesterday1 = today1 - datetime.timedelta(days=back_days)
        if today2:
            yesterday2 = today2 - datetime.timedelta(days=back_days)
    except:
        if yesterday:
            diff_days = (today - yesterday).days
            if today1:
                yesterday1 = today1 - datetime.timedelta(days=diff_days)
            if today2:
                yesterday2 = today2 - datetime.timedelta(days=diff_days)

# print("PATH=", os.environ.get("PATH", ""))
# print("ORACLE_HOME from environment:", os.environ.get("ORACLE_HOME"))
# print("Working dir:", os.getcwd())
# print("sqlnet.ora exists:", os.path.exists(r"C:\app\instantclient_19_19\sqlnet.ora"))


cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') 

# Основни параметри за периода
month_day_from = (3, 1)     # (месец, ден) - начало
month_day_till = (11, 30)   # (месец, ден) - край

year_this = today.year  # това е текущата година, по подразбиране

if args.year1:
    
    if args.year1 == "this":
        year1 = year_this

    elif args.year1 == "last":
         year1 = datetime.date.today().year - 1

    else:
        try:
            year1 = int(args.year1)
        except:
            year1 = year_this
else:
    year1 = year_this

if args.year2:
    
    if args.year2 == "this":
        year2 = year_this

    elif args.year2 == "last":
         year2 = datetime.date.today().year - 1

    else:
        try:
            year2 = int(args.year2)
        except:
            year2 = year_this
else:
    year2 = year_this

# Дати за началото и края на сезона
date_from = datetime.datetime(year_this, month_day_from[0], month_day_from[1])
date_till = datetime.datetime(year_this, month_day_till[0], month_day_till[1])

# Период за надписи (пример: 01.03-30.11.2025)
for_period = f"{date_from.strftime('%d.%m')}-{date_till.strftime('%d.%m')}.{date_till.strftime('%Y')}"

# Форматирани дати за текстове и репорти
TODAY_STR = today.strftime("%d.%m.%Y")

# HOTELS групите
HOTELS = [
    ([
    'DDJ', 'GER', 'MRA', 'SLA', 'ELI', 'NON', 'BOR', 'LAB', 'LAM', 'LAG', 
    'KLP', 'ARB', 'KLK', 'DTC', 'ORL', 'MAL', 'DOR', 'DRU', 'OAS', 'FLG', 
    'FLA', 'OR1', 'OR2', 'MAG', 'SUP', 'RAL', 'VIT', 'KOM', 'ALT', 'KPS', 'PAN', 'VMG'
    ], 'Albena'),
    ([ 'MUR' ], 'White Lagoon'),
    ([ 'MGS', 'ROP', 'HOL', 'NEP' ], 'Primorsko')
]

# Генериране на SQL колони за месеци
columns_by_month = []



# Обединени колони за SQL
month_columns_sql = ", ".join(columns_by_month)

# За специфични обработки в Excel
cols_ignore = []
cols_sum_ignore = [0, 1]
cols_with_sum = [2]
cols_blue = [6, 7, 8]

if args.by:
    report_by=args.by.split("-")
else:
    report_by=[]

if "market" in report_by or "markets" in report_by:
    TourOperatorSelector = 'train.SourceGrouping(OCC.TourOperator)'

else:
    TourOperatorSelector = 'OCC.TourOperator'   

# ---- Параметри за периода ----
month_day_from = (3, 1)     # Начало на сезона (март)
month_day_till = (11, 30)   # Край на сезона (ноември)

def generate_sheet_from_data(workbook, sheet_name, title, all_data, 
    key, key1=None, key2=None, headers_base=None, num_data_columns=10):
    """
    Генерира лист в ексела с основни данни + допълнителни дати, автоматично.
    """
    if headers_base is None:
        headers_base = []

    data_today = all_data.get(key, {})
    data_today1 = all_data.get(key1, {}) if key1 else {}
    data_today2 = all_data.get(key2, {}) if key2 else {}

    all_keys = set(data_today.keys()).union(data_today1.keys()).union(data_today2.keys())

    generate_sheet_combined(
        workbook=workbook,
        sheet_name=sheet_name,
        title=title,
        all_keys=all_keys,
        data_today=data_today,
        data_today1=data_today1,
        data_today2=data_today2,
        headers_base=headers_base,
        num_data_columns=num_data_columns,
    )

def load_data(sql, hotel_list, key_columns_count):
    conn = cx_Oracle.connect(user='opera', password='opera', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute(sql.replace('@HOTELS', hotel_list))

    result = {}
    for row in cursor.fetchall():
        key = tuple(row[:key_columns_count])
        values = list(row[key_columns_count:])
        result[key] = values

    conn.close()
    return result

def load_all_data(sqls, hotels_str, key_columns_count):
    data = {}
    for key, sql in sqls.items():
        if sql:
            print(f"Изпълнявам заявка за {key}...")
            data[key] = load_data(sql.replace('@HOTELS', hotels_str), hotels_str, key_columns_count)
    return data

def generate_sql(today, yesterday, date_from, date_till, tour_operator_selector, for_hotels=False, for_touroperators=False, for_both=False):
    month_columns = []
    for month in range(3, 12):
        start_date = datetime.datetime(date_from.year, month, 1)
        end_date = (datetime.datetime(date_from.year, month + 1, 1) - datetime.timedelta(days=1)) if month < 12 else datetime.datetime(date_from.year, 12, 31)
        month_name = start_date.strftime('%b').upper()

        if yesterday:
            column = f'''
            SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') 
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END)
            -
            SUM(CASE WHEN the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') 
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD') 
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END) AS "{month_name}"
            '''
        else:
            column = f'''
            SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD')
                     AND reservation_date BETWEEN TO_DATE('{start_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                                              AND TO_DATE('{end_date.strftime('%Y%m%d')}', 'YYYYMMDD')
                     THEN paxrooms ELSE 0 END) AS "{month_name}"
            '''
        month_columns.append(column)

    month_columns_sql = ",\n".join(month_columns)

    select_parts = []

    if for_hotels:
        select_parts.append('R.SEASON2 "Хотел"')
    elif for_touroperators:
        select_parts.append(f'{tour_operator_selector} "Туроператор"')
    elif for_both:
        select_parts.append(f'{tour_operator_selector} "Туроператор"')
        select_parts.append('R.SEASON2 "Хотел"')

    if yesterday:
        select_parts.append(f'''
        SUM(CASE WHEN OCC.the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END)
        -
        SUM(CASE WHEN OCC.the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END) AS "updown"
        ''')
    else:
        select_parts.append(f'''
        SUM(CASE WHEN OCC.the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN OCC.paxrooms ELSE 0 END) AS "total"
        ''')

    select_parts.append(month_columns_sql)

    full_select = ",\n".join(select_parts)

    if for_hotels:
        group_by = "GROUP BY R.SEASON2, R.RESORT_TYPE"
        order_by = "ORDER BY R.RESORT_TYPE"
    elif for_touroperators:
        group_by = f"GROUP BY {tour_operator_selector}"
        order_by = f"ORDER BY {tour_operator_selector}"
    elif for_both:
        group_by = f"GROUP BY {tour_operator_selector}, R.SEASON2, R.RESORT_TYPE"
        order_by = f"ORDER BY {tour_operator_selector}, R.RESORT_TYPE"
    else:
        group_by = ""
        order_by = ""

    if yesterday:
        having_condition = f'''
        SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END)
        -
        SUM(CASE WHEN the_date = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0
        '''
    else:
        having_condition = f'''
        SUM(CASE WHEN the_date = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD') THEN paxrooms ELSE 0 END) <> 0
        '''

    sql = f'''
    SELECT
    {full_select}
    FROM (
        SELECT TourOperator, RESORT, the_date, reservation_date, SUM(paxrooms) paxrooms
        FROM (
            SELECT resort, SR.COMPANY TourOperator, e.reservation_date, e.ISSUE_DATE the_date,
                   SUM(e.pax) paxrooms
            FROM train.ALB_OCCUPANCY_RATE_JURNAL e
            LEFT JOIN OPERA.NAME SR ON E.SOURCE_ID = SR.NAME_ID
            WHERE
              ({f"e.ISSUE_DATE = TO_DATE('{yesterday.strftime('%Y%m%d')}', 'YYYYMMDD') OR" if yesterday else ""}
               e.ISSUE_DATE = TO_DATE('{today.strftime('%Y%m%d')}', 'YYYYMMDD'))
              AND e.reservation_date BETWEEN TO_DATE('{date_from.strftime('%Y%m%d')}', 'YYYYMMDD')
                                         AND TO_DATE('{date_till.strftime('%Y%m%d')}', 'YYYYMMDD')
              AND e.RESORT IN (@HOTELS)
              AND SR.COMPANY NOT IN ('STF', 'CONTRACTS', 'Block for future overbookings')
            GROUP BY e.ISSUE_DATE, e.reservation_date, SR.COMPANY, e.RESORT
        )
        GROUP BY TourOperator, RESORT, the_date, reservation_date
    ) OCC
    JOIN OPERA.RESORT R ON R.RESORT = OCC.RESORT
    {group_by}
    HAVING {having_condition}
    {order_by}
    '''

    return sql

def generate_all_sql(today, yesterday, today1, yesterday1, today2, yesterday2, year_this, year1, year2, month_day_from, month_day_till, tour_operator_selector):
    sqls = {}

    date_from_this = datetime.datetime(year_this, month_day_from[0], month_day_from[1])
    date_till_this = datetime.datetime(year_this, month_day_till[0], month_day_till[1])

    date_from_1 = datetime.datetime(year1, month_day_from[0], month_day_from[1])
    date_till_1 = datetime.datetime(year1, month_day_till[0], month_day_till[1])

    date_from_2 = datetime.datetime(year2, month_day_from[0], month_day_from[1])
    date_till_2 = datetime.datetime(year2, month_day_till[0], month_day_till[1])

    sqls['total'] = generate_sql(today, yesterday, date_from_this, date_till_this, tour_operator_selector)
    sqls['full'] = generate_sql(today, yesterday, date_from_this, date_till_this, tour_operator_selector, for_both=True)
    sqls['hotels'] = generate_sql(today, yesterday, date_from_this, date_till_this, tour_operator_selector, for_hotels=True)
    sqls['touroperators'] = generate_sql(today, yesterday, date_from_this, date_till_this, tour_operator_selector, for_touroperators=True)

    if today1:
        sqls['total1'] = generate_sql(today1, yesterday1, date_from_1, date_till_1, tour_operator_selector)
        sqls['full1'] = generate_sql(today1, yesterday1, date_from_1, date_till_1, tour_operator_selector, for_both=True)
        sqls['hotels1'] = generate_sql(today1, yesterday1, date_from_1, date_till_1, tour_operator_selector, for_hotels=True)
        sqls['touroperators1'] = generate_sql(today1, yesterday1, date_from_1, date_till_1, tour_operator_selector, for_touroperators=True)

    if today2:
        sqls['total2'] = generate_sql(today2, yesterday2, date_from_2, date_till_2, tour_operator_selector)
        sqls['full2'] = generate_sql(today2, yesterday2, date_from_2, date_till_2, tour_operator_selector, for_both=True)
        sqls['hotels2'] = generate_sql(today2, yesterday2, date_from_2, date_till_2, tour_operator_selector, for_hotels=True)
        sqls['touroperators2'] = generate_sql(today2, yesterday2, date_from_2, date_till_2, tour_operator_selector, for_touroperators=True)

    return sqls

def safe_write(worksheet, row, col, value, cell_format=None):
    if value is None:
        if cell_format:
            # Ако е цветен формат, слагаме 0
            worksheet.write(row, col, 0, cell_format)
        else:
            # Ако няма формат - оставяме празно
            worksheet.write(row, col, "")
    else:
        worksheet.write(row, col, value, cell_format)

def auto_adjust_column_widths(worksheet, widths_dict, min_width=8, max_width=40):
    """
    Автоматично наглася ширините на колоните.
    
    widths_dict - речник от {колона: макс дължина на текста}
    """
    for col_num, max_len in widths_dict.items():
        final_width = max(min_width, min(max_len + 2, max_width))  # +2 допълнително пространство
        worksheet.set_column(col_num, col_num, final_width)

def generate_sheet_combined(workbook, sheet_name, title, all_keys, 
    data_today, data_today1, data_today2, headers_base, num_data_columns):
    
    worksheet = workbook.add_worksheet(name=sheet_name)

    key_columns_count = len(headers_base)
    add_date_column = bool(today1 or today2)  # Дали да има нова колона "Дата"
    cr = 0

    widths = {}

    # Заглавие
    worksheet.merge_range(cr, 0, cr, key_columns_count + num_data_columns + (1 if add_date_column else 0) - 1, title, merge_bold)
    cr += 2

    # Заглавия на колоните
    month_headers = ["Нощувки", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
    headers = headers_base.copy()
    if add_date_column:
        headers.insert(0, "Към Дата")
    headers += month_headers

    for c, h in enumerate(headers):
        safe_write(worksheet, cr, c, h, header_format)
        widths[c] = len(str(h))

    worksheet.freeze_panes(3, 0)
    cr += 1

    # Суми по видове
    totals_today = [0] * num_data_columns
    totals_today1 = [0] * num_data_columns
    totals_today2 = [0] * num_data_columns

    for key in sorted(all_keys):
        offset = 0

        # --- Основен today ред ---
        if add_date_column:
            safe_write(worksheet, cr, 0, today.strftime('%d.%m.%Y'))
            offset = 1

        for idx, val in enumerate(key):
            safe_write(worksheet, cr, offset + idx, val)

            if val is not None:
                value_len = len(str(val))
                widths[offset + idx] = max(widths.get(offset + idx, 0), value_len)

        values = data_today.get(key, [0] * num_data_columns)
        for idx, val in enumerate(values):
            safe_write(worksheet, cr, offset + key_columns_count + idx, val, border)

            if val is not None:
                value_len = len(str(val))
                widths[offset + key_columns_count + idx] = max(widths.get(offset + key_columns_count + idx, 0), value_len)

            if isinstance(val, (int, float)):
                totals_today[idx] += val

        cr += 1

        # --- today1 ред ---
        if data_today1:
            if add_date_column:
                safe_write(worksheet, cr, 0, today1.strftime('%d.%m.%Y'), border_light_blue)
                offset = 1
            else:
                offset = 0

            for idx, val in enumerate(key):
                safe_write(worksheet, cr, offset + idx, val, border_light_blue)

            values = data_today1.get(key, [0] * num_data_columns)
            for idx, val in enumerate(values):
                safe_write(worksheet, cr, offset + key_columns_count + idx, val, border_light_blue)

                if isinstance(val, (int, float)):
                    totals_today1[idx] += val

            cr += 1

        # --- today2 ред ---
        if data_today2:
            if add_date_column:
                safe_write(worksheet, cr, 0, today2.strftime('%d.%m.%Y'), border_light_green)
                offset = 1
            else:
                offset = 0

            for idx, val in enumerate(key):
                safe_write(worksheet, cr, offset + idx, val, border_light_green)

            values = data_today2.get(key, [0] * num_data_columns)
            for idx, val in enumerate(values):
                safe_write(worksheet, cr, offset + key_columns_count + idx, val, border_light_green)

                if isinstance(val, (int, float)):
                    totals_today2[idx] += val

            cr += 1

    if key_columns_count > 0:

        # --- Totals редове ---
        if add_date_column:
            safe_write(worksheet, cr, 0, today.strftime('%d.%m.%Y'), border_bold)
            safe_write(worksheet, cr, 1, f"Общо", border_bold)
            offset = 2
        else:
            safe_write(worksheet, cr, 0, f"Общо ({today.strftime('%d.%m.%Y')})", border_bold)
            offset = 1

        for idx, val in enumerate(totals_today):
            safe_write(worksheet, cr, offset + idx, val, border_bold)
        cr += 1

        if data_today1:
            if add_date_column:
                safe_write(worksheet, cr, 0, today1.strftime('%d.%m.%Y'), border_light_blue_bold)
                safe_write(worksheet, cr, 1, f"Общо", border_light_blue_bold)
                offset = 2
            else:
                safe_write(worksheet, cr, 0, f"Общо ({today1.strftime('%d.%m.%Y')})", border_light_blue_bold)
                offset = 1

            for idx, val in enumerate(totals_today1):
                safe_write(worksheet, cr, offset + idx, val, border_light_blue_bold)
            cr += 1

        if data_today2:
            if add_date_column:
                safe_write(worksheet, cr, 0, today2.strftime('%d.%m.%Y'), border_light_green)
                safe_write(worksheet, cr, 1, f"Общо", border_light_green)
                offset = 2
            else:
                safe_write(worksheet, cr, 0, f"Общо ({today2.strftime('%d.%m.%Y')})", border_light_green)
                offset = 1

            for idx, val in enumerate(totals_today2):
                safe_write(worksheet, cr, offset + idx, val, border_light_green)
            cr += 1


    cr += 2

    safe_write(worksheet, cr, 1, 'Дата: ' + TODAY_STR)
    cr += 1
    safe_write(worksheet, cr, 1, 'Изготвил: Иван Михайлов')

    # --- Автоматична ширина
    auto_adjust_column_widths(worksheet, widths)

# ---- Генериране на всички SQL заявки ----
sqls = generate_all_sql(
    today=today,
    yesterday=yesterday,
    today1=today1,
    yesterday1=yesterday1,
    today2=today2,
    yesterday2=yesterday2,
    year_this=year_this,
    year1=year1,
    year2=year2,
    month_day_from=month_day_from,
    month_day_till=month_day_till,
    tour_operator_selector='train.SourceGrouping(OCC.TourOperator)'
)

# ---- Обхождане на групите хотели ----
for hotel_list in HOTELS:
    hotels_str = ", ".join(f"'{h}'" for h in hotel_list[0])

    # заглавия
    if yesterday:
        if (today - yesterday).days == 1:
            title_base = f"Движение през {yesterday.strftime('%d.%m')} на нощувки"
        else:
            title_base = f"Движение в интервала {yesterday.strftime('%d.%m')}-{(today - datetime.timedelta(days=1)).strftime('%d.%m')}"
    else:
        title_base = f"Нощувки до {today.strftime('%d.%m.%Y')}"

    title_full = f"{title_base} за периода {month_day_from[0]:02d}.{month_day_from[1]:02d}-{month_day_till[0]:02d}.{month_day_till[1]:02d}.{year_this} в {hotel_list[1]}"

    print(f"\n▶️ Генерирам справка за {hotel_list[1]}...")

    if "total" in report_by or "resorts" in report_by or "resort" in report_by:
        # само по хотели
        all_data_total = load_all_data({
            'total': sqls['total'],
            'total1': sqls.get('total1'),
            'total2': sqls.get('total2')
        }, hotels_str, key_columns_count=0)

        generate_sheet_from_data(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-общо",
            title=title_full + " общо",
            all_data=all_data_total,
            key='total',
            key1='total1',
            key2='total2',
            headers_base=[],
            num_data_columns=10
        )

    if "hotel" in report_by or "hotels" in report_by:
        # само по хотели
        all_data_hotels = load_all_data({
            'hotels': sqls['hotels'],
            'hotels1': sqls.get('hotels1'),
            'hotels2': sqls.get('hotels2')
        }, hotels_str, key_columns_count=1)

        generate_sheet_from_data(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-Хотели",
            title=title_full + " по хотели",
            all_data=all_data_hotels,
            key='hotels',
            key1='hotels1',
            key2='hotels2',
            headers_base=['Хотел'],
            num_data_columns=10
        )

    if "market" in report_by or "markets" in report_by or "agent" in report_by or "agents" in report_by or "source" in report_by or "sources" in report_by:
        all_data_touroperators = load_all_data({
            'touroperators': sqls['touroperators'],
            'touroperators1': sqls.get('touroperators1'),
            'touroperators2': sqls.get('touroperators2')
        }, hotels_str, key_columns_count=1)

        generate_sheet_from_data(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-Туроператори",
            title=title_full + " по туроператори",
            all_data=all_data_touroperators,
            key='touroperators',
            key1='touroperators1',
            key2='touroperators2',
            headers_base=['Туроператор'],
            num_data_columns=10
        )


    if "both" in report_by or "full" in report_by:
        # ---- Зареждаме данните за групата хотели ----
        all_data_full = load_all_data({
            'full': sqls['full'],
            'full1': sqls.get('full1'),
            'full2': sqls.get('full2')
        }, hotels_str, key_columns_count=2)

        # ---- Генерираме листовете ----
        generate_sheet_from_data(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}",
            title=title_full + " по туроператори и хотели",
            all_data=all_data_full,
            key='full',
            key1='full1',
            key2='full2',
            headers_base=['Хотел','Туроператор'],
            num_data_columns=10
        )

    print(f"✅ Справка за {hotel_list[1]} готова.")

# ---- Затваряме файла ----
workbook.close()

print("\n✅ Всички справки са успешно генерирани!")

if args.file == "test" or args.file == "exit" or args.file == "end":
    exit()

yesterday_day=(today + datetime.timedelta(-1)).strftime("%d.%m %a")

# Първо генерираме subject
if yesterday:
    if (today - yesterday).days == 1:
        period_text = f"Движение за {yesterday.strftime('%d.%m.%Y')}"
    else:
        period_text = f"Движение от {yesterday.strftime('%d.%m.%Y')} до {(today - datetime.timedelta(days=1)).strftime('%d.%m.%Y')}"
else:
    period_text = f"Нощувки към {today.strftime('%d.%m.%Y')}"

group_parts = []


if "market" in report_by or "markets" in report_by:
    group_parts.append("по пазари")
if "hotel" in report_by or "hotels" in report_by:
    group_parts.append("по хотели")
if "agent" in report_by or "source" in report_by or "sources" in report_by:
    group_parts.append("по туроператори")
if "both" in report_by or "full" in report_by:
    group_parts.append("по туроператори и хотели")
if "total" in report_by or "resort" in report_by  or "resorts" in report_by:
    group_parts.append("общия тотал")

group_text = ", ".join(group_parts)


subject = f"{period_text} {group_text} и по месеци".strip()
comparison_parts = []
if today1:
    comparison_parts.append(f"сравнение {today1.strftime('%d.%m.%Y %A')}")
if today2:
    comparison_parts.append(f"сравнение {today2.strftime('%d.%m.%Y')}")

if comparison_parts:
    subject += " + " + ", ".join(comparison_parts)



# След това генерираме body
body = f"""\
Здравейте,

Прикачена е справка за {period_text}.
"""

if today1:
    body += f"\nСправката включва и сравнение с дата {today1.strftime('%d.%m.%Y')}."
if today2:
    body += f"\nСправката включва и втора сравнение дата {today2.strftime('%d.%m.%Y')}."

if group_text:
    body += f"\nДанните са групирани {group_text}."

body = f"""\
Здравейте,

Прикачена е справка за {period_text}.
"""

if today1:
    body += f"\nСравнява се също спрямо {today1.strftime('%d.%m.%Y %A')} (година {year1})."
if today2:
    body += f"\nДопълнително се сравнява и с {today2.strftime('%d.%m.%Y')} (година {year2})."

if group_text:
    body += f"\nДанните са групирани {group_text} и по месеци."

body += f"""

Генерирана на {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}.

Поздрави,
Иван Михайлов
"""



# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))
all_files = os.listdir(directory) 
files = [f for f in all_files if re.match(r'^Overnights.+\.xlsx', f)]
for filename in files:
    # Open file in binary mode
    with open(directory + filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Add attachment to message and convert message to string
    message.attach(part)
    os.remove(directory + filename)

text = message.as_string()
# Log in to server 
print('Sending email at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

#with smtplib.SMTP(mailserver) as server:
    #server.login(sender_email, password)
#    server.sendmail(sender_email, receiver_email, text)

#with smtplib.SMTP_SSL(mailserver, 465) as server:
#    server.login(sender_email, sender_password)
#    server.sendmail(sender_email, receiver_email, text)

server = smtplib.SMTP_SSL("smtp.gmail.com")
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_email , text)




print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





