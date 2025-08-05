# helpers/sinif.py
from db import supabase
import streamlit as st

@st.cache_data(ttl=0)
def siniflari_getir(ilce_id):
    try:
        response = supabase.table("siniflar").select("*").eq("ilce_id", ilce_id).execute()
        if response.data:
            return sorted(response.data, key=lambda x: x["ad"])
        return []
    except Exception as e:
        st.error(f"Sınıflar alınırken hata oluştu: {e}")
        return []

def sinif_ekle(ad, ogrenci, ilce_id, gun, seviye, baslangic, bitis):
    try:
        supabase.table("siniflar").insert({
            "ad": ad,
            "ogrenci": ogrenci,
            "ilce_id": ilce_id,
            "gun": gun,
            "seviye": seviye,
            "baslangic": baslangic,
            "bitis": bitis
        }).execute()
    except Exception as e:
        st.error(f"Sınıf eklenirken hata oluştu: {e}")

def sinif_sil(sinif_id):
    try:
        supabase.table("siniflar").delete().eq("id", sinif_id).execute()
    except Exception as e:
        st.error(f"Sınıf silinirken hata oluştu: {e}")

