# helpers/il.py
from db import supabase
import streamlit as st

@st.cache_data(ttl=300)
def illeri_getir():
    try:
        response = supabase.table("iller").select("*").execute()
        if response.data:
            return sorted(response.data, key=lambda x: x["ad"])
        return []
    except Exception as e:
        st.error(f"İller alınırken hata oluştu: {e}")
        return []

def il_ekle(il_adi):
    try:
        supabase.table("iller").insert({"ad": il_adi}).execute()
    except Exception as e:
        st.error(f"İl eklenirken hata oluştu: {e}")

def il_sil(il_id):
    try:
        supabase.table("iller").delete().eq("id", il_id).execute()
    except Exception as e:
        st.error(f"İl silinirken hata oluştu: {e}")

def il_id_bul(il_adi, iller):
    for il in iller:
        if il["ad"] == il_adi:
            return il["id"]
    return None
