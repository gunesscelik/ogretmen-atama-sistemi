# helpers/ilce.py
from db import supabase
import streamlit as st

@st.cache_data(ttl=0)
def ilceleri_getir(il_id):
    try:
        response = supabase.table("ilceler").select("*").eq("il_id", il_id).execute()
        if response.data:
            return sorted(response.data, key=lambda x: x["ad"])
        return []
    except Exception as e:
        st.error(f"İlçeler alınırken hata oluştu: {e}")
        return []

def ilce_ekle(ilce_adi, il_id):
    try:
        supabase.table("ilceler").insert({"ad": ilce_adi, "il_id": il_id}).execute()
    except Exception as e:
        st.error(f"İlçe eklenirken hata oluştu: {e}")

def ilce_sil(ilce_id):
    try:
        supabase.table("ilceler").delete().eq("id", ilce_id).execute()
    except Exception as e:
        st.error(f"İlçe silinirken hata oluştu: {e}")

def ilce_id_bul(ilce_adi, ilceler):
    for ilce in ilceler:
        if ilce["ad"] == ilce_adi:
            return ilce["id"]
    return None

