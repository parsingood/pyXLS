import pyodbc
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


delete_stop_sale_by_logid([221359, 221358, 221357], user_id='STOYAN')