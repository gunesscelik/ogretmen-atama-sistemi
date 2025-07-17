from db import get_connection  # Artık sadece bağlantıyı alıyoruz

def sutun_ekle():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE ogretmenler ADD COLUMN baslangic TIME")
    except Exception as e:
        print("baslangic zaten var mı?", e)

    try:
        cur.execute("ALTER TABLE ogretmenler ADD COLUMN bitis TIME")
    except Exception as e:
        print("bitis zaten var mı?", e)

    conn.commit()
    conn.close()
    print("Sütunlar eklendi veya zaten vardı.")

sutun_ekle()
