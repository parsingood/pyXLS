import cx_Oracle
import datetime
import os

# -------- Конфигурация --------
RESORTS = [
    'GER','MRA','SLA','ELI','NON','BOR','LAB','LAM','LAG','KLP','ARB','KLK','DTC','ORL','MAL',
    'DOR','DRU','OAS','FLG','FLA','OR1','MAG','SUP','RAL','VIT','KPS','VMG','GOR'
]
YEARS = list(range(2016, 2006, -1))  # 2016..2007 (от нови към стари)
OUT_FILE = "visits_with_dob_2016.tsv"     # растящ файл

ORACLE_CLIENT = r"C:\app\instantclient_19_19"
DSN_HOST = '10.10.21.33'
DSN_PORT = '1521'
DSN_SERVICE = 'opera'
DB_USER = 'opera'
DB_PASS = 'opera'

# -------- Помощни --------
def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def ensure_header(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("RESORT\tARRIVAL_DATE\tNAME_ID\tRESV_NAME_ID\tDOB\n")

# -------- Свързване --------
cx_Oracle.init_oracle_client(lib_dir=ORACLE_CLIENT)
dsn = cx_Oracle.makedsn(DSN_HOST, DSN_PORT, service_name=DSN_SERVICE)
conn = cx_Oracle.connect(user=DB_USER, password=DB_PASS, dsn=dsn)
cur = conn.cursor()
cur.arraysize = 1000  # по-голям fetch пакет
# (prefetchrows влияе при statement handle; cx_Oracle 8+ може да го контролира през cursor)

ensure_header(OUT_FILE)

print(f"\n🟢 Старт: {datetime.datetime.now():%A, %d.%m.%Y %H:%M:%S}\n")

# -------- SQL-и --------
SQL_IDS = """
SELECT /* уникални гости за да дръпнем DOB само веднъж */
       DISTINCT R.NAME_ID
FROM OPERA.RESERVATION_NAME R
JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN
  ON EN.RESORT = R.RESORT
 AND EN.RESV_NAME_ID = R.RESV_NAME_ID
 AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E
  ON E.RESORT = R.RESORT
 AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ
LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT
  ON RT.RESORT = R.RESORT
 AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY
WHERE R.RESORT = :resort
  AND R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
  AND NVL(RT.PSEUDO_YN, 'N') = 'N'
  AND R.TRUNC_BEGIN_DATE BETWEEN TO_DATE(:d1,'DD.MM.YYYY') AND TO_DATE(:d2,'DD.MM.YYYY')
"""

# партидно дърпане на DOB само от OPERA.NAME; функциите се викат веднъж на NAME_ID
def fetch_dob_map(cursor, name_ids):
    dob_map = {}
    if not name_ids:
        return dob_map
    BATCH = 900  # под лимита 1000 за IN (...)
    for chunk in chunked(name_ids, BATCH):
        binds = ",".join([f":id{j}" for j in range(len(chunk))])
        sql = f"""
            SELECT N.NAME_ID,
                   NVL(OPERA.bts_sh_sens.dob(N.NAME_ID), OPERA.bit_sh_sens.dob(N.NAME_ID)) AS DOB
            FROM OPERA.NAME N
            WHERE N.NAME_ID IN ({binds})
        """
        params = {f"id{j}": chunk[j] for j in range(len(chunk))}
        cursor.execute(sql, params)
        for nid, dob in cursor:
            dob_map[str(nid)] = dob  # пазим като string за лесно записване
    return dob_map

SQL_VISITS = """
SELECT 
  R.RESORT,
  R.TRUNC_BEGIN_DATE,
  R.NAME_ID,
  R.RESV_NAME_ID
FROM OPERA.RESERVATION_NAME R
JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN
  ON EN.RESORT = R.RESORT
 AND EN.RESV_NAME_ID = R.RESV_NAME_ID
 AND EN.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
LEFT JOIN OPERA.RESERVATION_DAILY_ELEMENTS E
  ON E.RESORT = R.RESORT
 AND E.RESERVATION_DATE = R.TRUNC_BEGIN_DATE
 AND E.RESV_DAILY_EL_SEQ = EN.RESV_DAILY_EL_SEQ
LEFT JOIN OPERA.RESORT$_ROOM_CATEGORY RT
  ON RT.RESORT = R.RESORT
 AND RT.ROOM_CATEGORY = E.ROOM_CATEGORY
WHERE R.RESORT = :resort
  AND R.RESV_STATUS NOT IN ('CANCELLED', 'NO SHOW')
  AND NVL(RT.PSEUDO_YN, 'N') = 'N'
  AND R.TRUNC_BEGIN_DATE BETWEEN TO_DATE(:d1,'DD.MM.YYYY') AND TO_DATE(:d2,'DD.MM.YYYY')
ORDER BY R.TRUNC_BEGIN_DATE DESC
"""

# -------- Основен цикъл --------
with open(OUT_FILE, "a", encoding="utf-8") as out:
    for resort in RESORTS:
        print(f"🏨 Хотел/RESORT: {resort}")
        for year in YEARS:
            d1 = f"01.01.{year}"
            d2 = f"31.12.{year}"
            print(f"  📅 Година {year} | Период {d1}–{d2}")

            # 1) Събери уникални NAME_ID за дадения хотел и година
            cur.execute(SQL_IDS, resort=resort, d1=d1, d2=d2)
            unique_ids = [str(row[0]) for row in cur]  # може да са много — но само за текущия отрязък
            print(f"    🔎 Уникални NAME_ID: {len(unique_ids)} (дърпаме DOB партидно)")

            # 2) Изтегли DOB в партиди и кеширай в памет
            dob_map = fetch_dob_map(cur, unique_ids)

            # 3) Стрийм на посещенията (същите филтри), сортирано по дата (DESC),
            #    печатай само при смяна на дата + момента на четене; записвай DOB от кеша
            cur.execute(SQL_VISITS, resort=resort, d1=d1, d2=d2)
            last_dt = None
            rows = 0

            for resort_val, begin_dt, name_id, resv_name_id in cur:
                if last_dt != begin_dt:
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"    🔄 {begin_dt:%Y-%m-%d} (четене в {now})")
                    last_dt = begin_dt

                dob = dob_map.get(str(name_id), '')  # може да е None → записваме празно
                out.write(f"{resort_val}\t{begin_dt:%Y-%m-%d}\t{name_id}\t{resv_name_id}\t{dob or ''}\n")
                rows += 1

            print(f"    ✅ Записани {rows} реда за {resort} / {year}")

cur.close()
conn.close()
print(f"\n🏁 Готово: {datetime.datetime.now():%A, %d.%m.%Y %H:%M:%S}")
print(f"📄 Файлът расте тук: {OUT_FILE}\n")
