# helpers/ogretmen.py
from db import supabase
import streamlit as st
from helpers.utils import gun_list_to_string

def ogretmenleri_getir(ilce_id=None):
    try:
        query = supabase.table("ogretmenler").select("*")
        if ilce_id:
            query = query.eq("ilce_id", ilce_id)
        response = query.execute()
        if response.data:
            return sorted(response.data, key=lambda x: x["isim"])
        return []
    except Exception as e:
        st.error(f"Öğretmenler alınırken hata oluştu: {e}")
        return []


def ogretmen_ekle(isim, puan, ilce_id, calisma_gunleri, max_sinif, uyum_2, uyum_34, uyum_56, baslangic, bitis):
    try:
        gun_string = gun_list_to_string(calisma_gunleri)
        response = supabase.table("ogretmenler").insert({
            "isim": isim,
            "puan": puan,
            "ilce_id": ilce_id,
            "calisma_gunu": gun_string,
            "max_sinif": max_sinif,
            "uyum_2": uyum_2,
            "uyum_34": uyum_34,
            "uyum_56": uyum_56,
            "baslangic": baslangic,
            "bitis": bitis,
            "saat_araligi": f"{baslangic}-{bitis}"
        }).execute()

        if response.data:
            return True
        else:
            st.warning("Veri eklenemedi, boş cevap döndü.")
            return False

    except Exception as e:
        st.error(f"Öğretmen eklenirken hata oluştu: {e}")
        return False


        
        # ✅ Ekleme cevabının başarılı olduğundan emin ol
        if response.data:
            return True
        else:
            st.warning("Veri eklenemedi, boş cevap döndü.")
            return False

    except Exception as e:
        st.error(f"Öğretmen eklenirken hata oluştu: {e}")
        return False


        

from db import supabase

# helpers/ogretmen.py
from db import supabase

def ogretmen_sil(ogretmen_id):
    try:
        response = supabase.table("ogretmenler").delete().eq("id", ogretmen_id).execute()
        
        print(">>> Silme ID:", ogretmen_id)
        print(">>> Response:", response)

        # ✅ APIResponse nesnesinin 'data' özelliği list olup en az 1 öğe içeriyorsa başarılı
        if hasattr(response, "data") and isinstance(response.data, list) and len(response.data) > 0:
            return True
        else:
            return False

    except Exception as e:
        print(">>> Exception:", e)
        return False







