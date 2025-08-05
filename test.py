# test.py
from db import supabase

print("Bağlantı başarılı mı:", supabase)  # Supabase client'ı gör

data = supabase.table("ogretmenler").select("*").execute()
print("Gelen veri:")
print(data.data)

