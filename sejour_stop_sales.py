import sys
import argparse
import pyodbc

def insert_stop_sale(otel, turop, start_date, end_date,
                     user_id='STOYAN', oda_tipi='', oda='',
                     aciklama='STOP'):
    print(f"📡 Въвеждам STOP за {otel}/{turop} от {start_date} до {end_date}")

    conn_str = (
        "Driver={SQL Server Native Client 11.0};"
        "Server=77.85.202.44;"
        "Database=ALBENASEJOUR;"
        "UID=sa;"
        "PWD=tDR*WXB9'K\\Nl+T?!=I&46yk"
    )
    conn = pyodbc.connect(conn_str, autocommit=False)
    cur = conn.cursor()

    try:
        # 🔧 Временна таблица с потребител
        cur.execute("IF OBJECT_ID('tempdb..#SejUser') IS NOT NULL DROP TABLE #SejUser;")
        cur.execute("CREATE TABLE #SejUser (UserID varchar(20));")
        cur.execute("INSERT INTO #SejUser VALUES (?)", (user_id,))

        # 📝 INSERT с явно подадени Aciklama и SejAciklama = ''
        cur.execute("""
            INSERT INTO dbo.StopSale (
                Otel, Turop, Oda, BasTarihi, GelTarihi, BitTarihi, Aciklama,
                OdaTipi, Aktif, WebYeniKayit, SejourYeniKayit, GarantiKontrolu,
                SejAciklama, GirKon, useMarket, SanTractAktif
            )
            VALUES (?, ?, ?, ?, ?, ?, ?,
                    ?, 'Y', 'N', 'Y', 'Y',
                    '', 'K', 'N', 'Y');
        """, (
            otel, turop, oda, start_date, start_date, end_date, aciklama,
            oda_tipi
        ))

        # 🔍 Вземи LogID
        cur.execute("""
            SELECT TOP 1 LogID FROM dbo.StopSale
            WHERE Crt_User = ?
            ORDER BY LogID DESC
        """, (user_id,))
        row = cur.fetchone()
        new_logid = row[0] if row else None
        print("✅ Въведен LogID:", new_logid)

        # 🔍 Проверка StopSaleInfo
        cur.execute("SELECT * FROM dbo.StopSaleInfo WHERE ID = ?", new_logid)
        print("📌 StopSaleInfo:", cur.fetchone())

        conn.commit()
        print("💾 STOP е записан успешно.")

    except Exception as e:
        conn.rollback()
        print("❌ ГРЕШКА:", e)

    finally:
        conn.close()
        print("🔚 Връзката е затворена.")

def delete_stop_sale_by_logid(log_ids, user_id='STOYAN'):
    conn_str = (
        "Driver={SQL Server Native Client 11.0};"
        "Server=77.85.202.44;"
        "Database=ALBENASEJOUR;"
        "UID=sa;"
        "PWD=tDR*WXB9'K\\Nl+T?!=I&46yk"
    )
    conn = pyodbc.connect(conn_str, autocommit=False)
    cur = conn.cursor()

    try:
        # За тригерите
        cur.execute("IF OBJECT_ID('tempdb..#SejUser') IS NOT NULL DROP TABLE #SejUser;")
        cur.execute("CREATE TABLE #SejUser (UserID varchar(20));")
        cur.execute("INSERT INTO #SejUser VALUES (?)", (user_id,))

        for log_id in log_ids:
            print(f"🗑 Изтривам StopSale и StopSaleInfo за LogID = {log_id}")
            cur.execute("DELETE FROM dbo.StopSale WHERE LogID = ?", (log_id,))
            cur.execute("DELETE FROM dbo.StopSaleInfo WHERE ID = ?", (log_id,))

        conn.commit()
        print("✅ Всичко е премахнато успешно.")

    except Exception as e:
        conn.rollback()
        print("❌ ГРЕШКА при изтриване:", e)

    finally:
        conn.close()
        print("🔚 Връзката е затворена.")


def print_usage_examples():
    print("""
📌 Примери за използване:

▶ Добавяне на STOP SALE:
    python sejour_stop_sales.py add DTC VASSY 2025-08-26 2025-08-28 --user_id STOYAN --oda_tipi STD --oda DBL

▶ Изтриване по LogID:
    python sejour_stop_sales.py delete 221359 221358 221357 --user_id STOYAN
""")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='📌 Добавяне или изтриване на STOP SALE записи.'
    )

    subparsers = parser.add_subparsers(dest='command', help='add или delete')

    # 📥 Подкоманда за добавяне
    add_parser = subparsers.add_parser('add', help='Добавяне на нов STOP SALE')
    add_parser.add_argument('otel', help='Код на хотел (напр. DTC)')
    add_parser.add_argument('turop', help='Код на туроператор (напр. VASSY)')
    add_parser.add_argument('start_date', help='Начална дата (формат: YYYY-MM-DD)')
    add_parser.add_argument('end_date', help='Крайна дата (формат: YYYY-MM-DD)')
    add_parser.add_argument('--user_id', default='STOYAN', help='Потребител (по подразбиране STOYAN)')
    add_parser.add_argument('--oda_tipi', default='', help='Тип стая (по желание)')
    add_parser.add_argument('--oda', default='', help='Код на стая (по желание)')

    # 🗑 Подкоманда за изтриване
    del_parser = subparsers.add_parser('delete', help='Изтриване на STOP SALE по LogID')
    del_parser.add_argument('log_ids', nargs='+', type=int, help='Списък от LogID стойности за изтриване')
    del_parser.add_argument('--user_id', default='STOYAN', help='Потребител (по подразбиране STOYAN)')

    # 📥 Ако няма аргументи или е невалидно извикване – покажи примери
    if len(sys.argv) == 1:
        parser.print_help()
        print_usage_examples()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'add':
        insert_stop_sale(
            otel=args.otel,
            turop=args.turop,
            start_date=args.start_date,
            end_date=args.end_date,
            user_id=args.user_id,
            oda_tipi=args.oda_tipi,
            oda=args.oda
        )
    elif args.command == 'delete':
        delete_stop_sale_by_logid(
            log_ids=args.log_ids,
            user_id=args.user_id
        )
    else:
        parser.print_help()
        print_usage_examples()
        sys.exit(1)
