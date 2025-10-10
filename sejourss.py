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



insert_stop_sale(
        otel='DTC',
        turop='VASSY',
        start_date='2025-08-26',
        end_date='2025-08-28',
        aciklama='STOP SALE',  # <- можеш да го смениш
        oda='',
        oda_tipi='',
        user_id='STOYAN'
    )