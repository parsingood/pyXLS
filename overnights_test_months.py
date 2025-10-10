# -*- coding: utf-8 -*-
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
import calendar

import cx_Oracle

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========================
#  НАСТРОЙКИ ЗА E-MAIL
# ==========================
to_email ="ivanm@albena.bg"
receiver_email = ["ivanm@albena.bg"]

to_email ="mtodorova@albena.bg"
receiver_email = [
    "mtodorova@albena.bg",
    "velina.gyumova@albena.bg",
    "ivanm@albena.bg",
    "maya.lazarova@albena.bg"
]

mailserver = "mail.wservices.ch"
sender_email = "ivanm@albena.life"
sender_password = "Y_gJ5Ect?N+k9,)"   # Препоръчително: вземи от ENV var

directory = "C:/test/"

# ==========================
#  Създаване на Excel файл
# ==========================
workbook = xlsxwriter.Workbook(
    f'C:/test/Overnights-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx'
)

# Формати
bold = workbook.add_format({'bold': True})
merge_bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
border = workbook.add_format({'border': 1})
border_bold = workbook.add_format({'bold': True, 'border': 1})

border_light_blue = workbook.add_format({
    'bg_color': '#f0f7fa',
    'border': 1,
})
border_light_blue_bold = workbook.add_format({
    'bg_color': '#f0f7fa',
    'border': 1,
    'bold': True
})
border_light_green = workbook.add_format({
    'bg_color': '#d9ead3',
    'border': 1
})
border_light_green_bold = workbook.add_format({
    'bg_color': '#d9ead3',
    'border': 1,
    'bold': True
})

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

# ==========================
#  Аргументи
# ==========================
parser = argparse.ArgumentParser(
    description="Справка за нощувките - общ брой към дадена дата или изменението им от определени дни назад до дадена дата",
    epilog="""Примери: 
  py overnights_months.py --date 2025-04-09 --back 1
  py overnights_months.py --back 1 
  py overnights_months.py --back 7
  py overnights_months.py --month1 1 --month2 12
""",
    add_help=True
)

parser.add_argument('--date', type=str,
                    help="Датата към която правим справката (YYYY-MM-DD). 'this' или 'now' за днес.")
parser.add_argument('--back', type=str,
                    help="Дата или брой дни назад за разликата. Формат YYYY-MM-DD или положително число. Ако липсва: показва се пълното състояние.")
parser.add_argument('--by', type=str,
                    help="По какво да групира: market(s)-total/resort(s)-hotel(s)-agent/source(s)-both/full")
parser.add_argument('--date1', type=str,
                    help="Допълнителна дата 1 за сравнение (YYYY-MM-DD). 'last' - аналогичният ден миналата година.")
parser.add_argument('--date2', type=str,
                    help="Допълнителна дата 2 за сравнение (YYYY-MM-DD). 'last'/'end' - 10.10 миналата година.")
parser.add_argument('--year1', type=str,
                    help="Година за date1 (например 2024). 'last' - миналата година.")
parser.add_argument('--year2', type=str,
                    help="Година за date2 (например 2023). 'last' - миналата година.")
parser.add_argument('--email', type=str,
                    help="Имейли за пращане, разделени с ';'")
parser.add_argument('--file', type=str,
                    help="test/exit/end - да не се праща имейл.")
# >>> Новите аргументи:
parser.add_argument('--month1', type=int, default=2,
                    help="Начален месец (1-12). По подразбиране 2 (февруари).")
parser.add_argument('--month2', type=int, default=11,
                    help="Краен месец (1-12). По подразбиране 11 (ноември).")

args = parser.parse_args()

# ==========================
#  Обработка на датите
# ==========================
today = datetime.date.today()
yesterday = None

if args.email:
    receiver_email = args.email.split(";")
    to_email = receiver_email[0]

if args.date:
    if args.date in ("this", "now"):
        today = datetime.date.today()
    else:
        try:
            today = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
        except:
            pass

if args.back:
    try:
        yesterday = datetime.datetime.strptime(args.back, "%Y-%m-%d").date()
    except:
        try:
            yesterday = today - datetime.timedelta(days=int(args.back))
        except:
            parser.print_help()
            sys.exit(1)

# Допълнителни дати
today1 = today2 = None
yesterday1 = yesterday2 = None

if args.date1:
    if args.date1 in ("last", "prev"):
        today1 = datetime.date.today() - datetime.timedelta(days=364)
    else:
        try:
            today1 = datetime.datetime.strptime(args.date1, "%Y-%m-%d").date()
        except:
            pass

if args.date2:
    if args.date2 in ("last", "prev", "end"):
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

# ==========================
#  Oracle
# ==========================
cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') 

# ==========================
#  Месеци според аргументите
# ==========================
month1 = max(1, min(12, args.month1 or 2))
month2 = max(1, min(12, args.month2 or 11))
if month1 > month2:
    raise ValueError("month1 трябва да е <= month2")

MONTHS = list(range(month1, month2 + 1))
MONTH_NAMES = [calendar.month_abbr[m].upper() for m in MONTHS]  # ['FEB', 'MAR', ...]

# Първи и последен ден на сезона според month1/2
year_this = today.year

import calendar as cal
date_from = datetime.datetime(year_this, month1, 1)
date_till = datetime.datetime(year_this, month2, cal.monthrange(year_this, month2)[1])

# Период за надписи (пример: 01.02-30.11.2025)
for_period = f"{date_from.strftime('%d.%m')}-{date_till.strftime('%d.%m')}.{date_till.strftime('%Y')}"
TODAY_STR = today.strftime("%d.%m.%Y")

# Хотелски групи
HOTELS = [
    ([
    'DDJ','GER','MRA','SLA','ELI','NON','BOR','LAB','LAM','LAG','KLP','ARB','KLK',
    'DTC','ORL','MAL','DOR','DRU','OAS','FLG','FLA','OR1','OR2','MAG','SUP','RAL',
    'VIT','KOM','ALT','KPS','PAN','VMG'
    ], 'Albena'),
    (['MUR'], 'White Lagoon'),
    (['MGS','ROP','HOL','NEP'], 'Primorsko')
]

cols_ignore = []
cols_sum_ignore = [0, 1]
cols_with_sum = [2]
cols_blue = [6, 7, 8]

if args.by:
    report_by = args.by.split("-")
else:
    report_by = []

if "market" in report_by or "markets" in report_by:
    TourOperatorSelector = 'train.SourceGrouping(OCC.TourOperator)'
else:
    TourOperatorSelector = 'OCC.TourOperator'

# ============== Помощни функции ==============

def generate_sql(today, yesterday, date_from, date_till, tour_operator_selector,
                 months, for_hotels=False, for_touroperators=False, for_both=False):
    """
    Генерира SQL с динамични колони по месеци.
    """
    month_columns = []
    for month in months:
        start_date = datetime.datetime(date_from.year, month, 1)
        end_date = datetime.datetime(date_from.year, month, calendar.monthrange(date_from.year, month)[1])
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

def generate_all_sql(today, yesterday,
                     today1, yesterday1, today2, yesterday2,
                     year_this, year1, year2,
                     month1, month2, tour_operator_selector,
                     months):
    sqls = {}

    df_this_from = datetime.datetime(year_this, month1, 1)
    df_this_till = datetime.datetime(year_this, month2, calendar.monthrange(year_this, month2)[1])

    df1_from = datetime.datetime(year1, month1, 1)
    df1_till = datetime.datetime(year1, month2, calendar.monthrange(year1, month2)[1])

    df2_from = datetime.datetime(year2, month1, 1)
    df2_till = datetime.datetime(year2, month2, calendar.monthrange(year2, month2)[1])

    sqls['total'] = generate_sql(today, yesterday, df_this_from, df_this_till,
                                 tour_operator_selector, months)
    sqls['full']  = generate_sql(today, yesterday, df_this_from, df_this_till,
                                 tour_operator_selector, months, for_both=True)
    sqls['hotels']= generate_sql(today, yesterday, df_this_from, df_this_till,
                                 tour_operator_selector, months, for_hotels=True)
    sqls['touroperators']= generate_sql(today, yesterday, df_this_from, df_this_till,
                                 tour_operator_selector, months, for_touroperators=True)

    if today1:
        sqls['total1'] = generate_sql(today1, yesterday1, df1_from, df1_till,
                                      tour_operator_selector, months)
        sqls['full1']  = generate_sql(today1, yesterday1, df1_from, df1_till,
                                      tour_operator_selector, months, for_both=True)
        sqls['hotels1']= generate_sql(today1, yesterday1, df1_from, df1_till,
                                      tour_operator_selector, months, for_hotels=True)
        sqls['touroperators1']= generate_sql(today1, yesterday1, df1_from, df1_till,
                                      tour_operator_selector, months, for_touroperators=True)

    if today2:
        sqls['total2'] = generate_sql(today2, yesterday2, df2_from, df2_till,
                                      tour_operator_selector, months)
        sqls['full2']  = generate_sql(today2, yesterday2, df2_from, df2_till,
                                      tour_operator_selector, months, for_both=True)
        sqls['hotels2']= generate_sql(today2, yesterday2, df2_from, df2_till,
                                      tour_operator_selector, months, for_hotels=True)
        sqls['touroperators2']= generate_sql(today2, yesterday2, df2_from, df2_till,
                                      tour_operator_selector, months, for_touroperators=True)

    return sqls

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

def safe_write(worksheet, row, col, value, cell_format=None):
    if value is None:
        if cell_format:
            worksheet.write(row, col, 0, cell_format)
        else:
            worksheet.write(row, col, "")
    else:
        worksheet.write(row, col, value, cell_format)

def auto_adjust_column_widths(worksheet, widths_dict, min_width=8, max_width=40):
    for col_num, max_len in widths_dict.items():
        final_width = max(min_width, min(max_len + 2, max_width))
        worksheet.set_column(col_num, col_num, final_width)

def generate_sheet_combined(workbook, sheet_name, title, all_keys,
    data_today, data_today1, data_today2, headers_base, num_data_columns,
    month_headers):
    
    worksheet = workbook.add_worksheet(name=sheet_name)

    key_columns_count = len(headers_base)
    add_date_column = bool(today1 or today2)
    cr = 0
    widths = {}

    # Заглавие
    worksheet.merge_range(cr, 0, cr, key_columns_count + num_data_columns + (1 if add_date_column else 0) - 1,
                          title, merge_bold)
    cr += 2

    # Заглавия
    headers = headers_base.copy()
    if add_date_column:
        headers.insert(0, "Към Дата")
    headers += month_headers

    for c, h in enumerate(headers):
        safe_write(worksheet, cr, c, h, header_format)
        widths[c] = len(str(h))

    worksheet.freeze_panes(3, 0)
    cr += 1

    totals_today  = [0] * (num_data_columns - 1)  # -1 защото първият е "Нощувки"
    totals_today1 = [0] * (num_data_columns - 1)
    totals_today2 = [0] * (num_data_columns - 1)

    for key in sorted(all_keys):
        offset = 0

        # today
        if add_date_column:
            safe_write(worksheet, cr, 0, today.strftime('%d.%m.%Y'))
            offset = 1

        for idx, val in enumerate(key):
            safe_write(worksheet, cr, offset + idx, val)
            if val is not None:
                widths[offset + idx] = max(widths.get(offset + idx, 0), len(str(val)))

        values = data_today.get(key, [0] * (num_data_columns - 1))
        # първа колона "Нощувки", после месеците
        safe_write(worksheet, cr, offset + key_columns_count + 0, values[0], border)
        widths[offset + key_columns_count + 0] = max(widths.get(offset + key_columns_count + 0, 0),
                                                     len(str(values[0])) if values[0] is not None else 1)
        for idx, val in enumerate(values[1:], start=1):
            safe_write(worksheet, cr, offset + key_columns_count + idx, val, border)
            if val is not None:
                widths[offset + key_columns_count + idx] = max(
                    widths.get(offset + key_columns_count + idx, 0), len(str(val))
                )
        # sum
        for i, v in enumerate(values):
            if isinstance(v, (int, float)):
                totals_today[i] += v

        cr += 1

        # today1
        if data_today1:
            if add_date_column:
                safe_write(worksheet, cr, 0, today1.strftime('%d.%m.%Y'), border_light_blue)
                offset = 1
            else:
                offset = 0

            for idx, val in enumerate(key):
                safe_write(worksheet, cr, offset + idx, val, border_light_blue)

            values = data_today1.get(key, [0] * (num_data_columns - 1))
            safe_write(worksheet, cr, offset + key_columns_count + 0, values[0], border_light_blue)
            for idx, val in enumerate(values[1:], start=1):
                safe_write(worksheet, cr, offset + key_columns_count + idx, val, border_light_blue)

            for i, v in enumerate(values):
                if isinstance(v, (int, float)):
                    totals_today1[i] += v

            cr += 1

        # today2
        if data_today2:
            if add_date_column:
                safe_write(worksheet, cr, 0, today2.strftime('%d.%m.%Y'), border_light_green)
                offset = 1
            else:
                offset = 0

            for idx, val in enumerate(key):
                safe_write(worksheet, cr, offset + idx, val, border_light_green)

            values = data_today2.get(key, [0] * (num_data_columns - 1))
            safe_write(worksheet, cr, offset + key_columns_count + 0, values[0], border_light_green)
            for idx, val in enumerate(values[1:], start=1):
                safe_write(worksheet, cr, offset + key_columns_count + idx, val, border_light_green)

            for i, v in enumerate(values):
                if isinstance(v, (int, float)):
                    totals_today2[i] += v

            cr += 1

    # Тотали
    if key_columns_count > 0:
        # today
        if add_date_column:
            safe_write(worksheet, cr, 0, today.strftime('%d.%m.%Y'), border_bold)
            safe_write(worksheet, cr, 1, "Общо", border_bold)
            offset = 2
        else:
            safe_write(worksheet, cr, 0, f"Общо ({today.strftime('%d.%m.%Y')})", border_bold)
            offset = 1

        safe_write(worksheet, cr, offset + 0, totals_today[0], border_bold)
        for idx, val in enumerate(totals_today[1:], start=1):
            safe_write(worksheet, cr, offset + idx, val, border_bold)
        cr += 1

        # today1
        if data_today1:
            if add_date_column:
                safe_write(worksheet, cr, 0, today1.strftime('%d.%m.%Y'), border_light_blue_bold)
                safe_write(worksheet, cr, 1, "Общо", border_light_blue_bold)
                offset = 2
            else:
                safe_write(worksheet, cr, 0, f"Общо ({today1.strftime('%d.%m.%Y')})", border_light_blue_bold)
                offset = 1

            safe_write(worksheet, cr, offset + 0, totals_today1[0], border_light_blue_bold)
            for idx, val in enumerate(totals_today1[1:], start=1):
                safe_write(worksheet, cr, offset + idx, val, border_light_blue_bold)
            cr += 1

        # today2
        if data_today2:
            if add_date_column:
                safe_write(worksheet, cr, 0, today2.strftime('%d.%m.%Y'), border_light_green_bold)
                safe_write(worksheet, cr, 1, "Общо", border_light_green_bold)
                offset = 2
            else:
                safe_write(worksheet, cr, 0, f"Общо ({today2.strftime('%d.%m.%Y')})", border_light_green_bold)
                offset = 1

            safe_write(worksheet, cr, offset + 0, totals_today2[0], border_light_green_bold)
            for idx, val in enumerate(totals_today2[1:], start=1):
                safe_write(worksheet, cr, offset + idx, val, border_light_green_bold)
            cr += 1

    cr += 2
    safe_write(worksheet, cr, 1, 'Дата: ' + TODAY_STR)
    cr += 1
    safe_write(worksheet, cr, 1, 'Изготвил: Иван Михайлов')

    auto_adjust_column_widths(worksheet, widths)

# ==========================
#  Подготвяме SQL-ите
# ==========================
# Вземаме year1/year2
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
    month1=month1,
    month2=month2,
    tour_operator_selector=TourOperatorSelector,
    months=MONTHS
)

# Excel заглавия
month_headers = ["Нощувки"] + MONTH_NAMES
NUM_DATA_COLUMNS = len(month_headers)  # Нощувки + броя месеци

# ==========================
#  Обхождаме групите хотели
# ==========================
for hotel_list in HOTELS:
    hotels_str = ", ".join(f"'{h}'" for h in hotel_list[0])

    if yesterday:
        if (today - yesterday).days == 1:
            title_base = f"Движение през {yesterday.strftime('%d.%m')} на нощувки"
        else:
            title_base = f"Движение в интервала {yesterday.strftime('%d.%m')}-{(today - datetime.timedelta(days=1)).strftime('%d.%m')}"
    else:
        title_base = f"Нощувки до {today.strftime('%d.%m.%Y')}"

    title_full = f"{title_base} за периода {for_period} в {hotel_list[1]}"

    print(f"\n▶️ Генерирам справка за {hotel_list[1]}...")

    if "total" in report_by or "resorts" in report_by or "resort" in report_by:
        all_data_total = load_all_data({
            'total': sqls['total'],
            'total1': sqls.get('total1'),
            'total2': sqls.get('total2')
        }, hotels_str, key_columns_count=0)

        generate_sheet_combined(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-общо",
            title=title_full + " общо",
            all_keys=set().union(*[d.keys() for d in all_data_total.values()]) if all_data_total else set(),
            data_today=all_data_total.get('total', {}),
            data_today1=all_data_total.get('total1', {}),
            data_today2=all_data_total.get('total2', {}),
            headers_base=[],
            num_data_columns=NUM_DATA_COLUMNS,
            month_headers=month_headers
        )

    if "hotel" in report_by or "hotels" in report_by:
        all_data_hotels = load_all_data({
            'hotels': sqls['hotels'],
            'hotels1': sqls.get('hotels1'),
            'hotels2': sqls.get('hotels2')
        }, hotels_str, key_columns_count=1)

        generate_sheet_combined(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-Хотели",
            title=title_full + " по хотели",
            all_keys=set().union(*[d.keys() for d in all_data_hotels.values()]) if all_data_hotels else set(),
            data_today=all_data_hotels.get('hotels', {}),
            data_today1=all_data_hotels.get('hotels1', {}),
            data_today2=all_data_hotels.get('hotels2', {}),
            headers_base=['Хотел'],
            num_data_columns=NUM_DATA_COLUMNS,
            month_headers=month_headers
        )

    if ("market" in report_by or "markets" in report_by or
        "agent" in report_by or "agents" in report_by or
        "source" in report_by or "sources" in report_by):
        all_data_touroperators = load_all_data({
            'touroperators': sqls['touroperators'],
            'touroperators1': sqls.get('touroperators1'),
            'touroperators2': sqls.get('touroperators2')
        }, hotels_str, key_columns_count=1)

        generate_sheet_combined(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}-Туроператори",
            title=title_full + " по туроператори",
            all_keys=set().union(*[d.keys() for d in all_data_touroperators.values()]) if all_data_touroperators else set(),
            data_today=all_data_touroperators.get('touroperators', {}),
            data_today1=all_data_touroperators.get('touroperators1', {}),
            data_today2=all_data_touroperators.get('touroperators2', {}),
            headers_base=['Туроператор'],
            num_data_columns=NUM_DATA_COLUMNS,
            month_headers=month_headers
        )

    if "both" in report_by or "full" in report_by:
        all_data_full = load_all_data({
            'full': sqls['full'],
            'full1': sqls.get('full1'),
            'full2': sqls.get('full2')
        }, hotels_str, key_columns_count=2)

        generate_sheet_combined(
            workbook=workbook,
            sheet_name=f"{hotel_list[1]}",
            title=title_full + " по туроператори и хотели",
            all_keys=set().union(*[d.keys() for d in all_data_full.values()]) if all_data_full else set(),
            data_today=all_data_full.get('full', {}),
            data_today1=all_data_full.get('full1', {}),
            data_today2=all_data_full.get('full2', {}),
            headers_base=['Хотел','Туроператор'],
            num_data_columns=NUM_DATA_COLUMNS,
            month_headers=month_headers
        )

    print(f"✅ Справка за {hotel_list[1]} готова.")

# Затваряме файла
workbook.close()
print("\n✅ Всички справки са успешно генерирани!")

if args.file in ("test", "exit", "end"):
    sys.exit(0)

# ==========================
#  Имейл
# ==========================
yesterday_day=(today + datetime.timedelta(-1)).strftime("%d.%m %a")

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
if "total" in report_by or "resort" in report_by or "resorts" in report_by:
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

body = f"""\
Здравейте,

Прикачена е справка за {period_text}.
"""

if today1:
    body += f"\nСравнява се също спрямо {today1.strftime('%d.%m.%Y %A')} (година {year1})."
if today2:
    body += f"\nДопълнително се сравнява и с {today2.strftime('%d.%m.%Y')} (година {year2})."

if group_text:
    body += f"\nДанните са групирани {group_text} и по месеци (от {calendar.month_abbr[month1]} до {calendar.month_abbr[month2]})."

body += f"""

Генерирана на {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}.

Поздрави,
Иван Михайлов
"""

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = to_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

all_files = os.listdir(directory)
files = [f for f in all_files if re.match(r'^Overnights.+\.xlsx', f)]
for filename in files:
    with open(directory + filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(part)
    os.remove(directory + filename)

text = message.as_string()
print('Sending email at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

with smtplib.SMTP_SSL(mailserver, 465) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, text)

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
