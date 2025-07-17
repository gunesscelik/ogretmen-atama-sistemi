# --- Veritabanı Bağlantısı ---
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="dpg-d1s52hh5pdvs73aenf3g-a.oregon-postgres.render.com",
        database="yeniatama",
        user="yeniatama_user",
        password="l7t6EuA6OD5YuTDhiKLdmfO4eRqUBm6x",
        port=5432
    )
