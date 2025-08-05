from helpers.sinif import siniflari_getir
from helpers.ogretmen import ogretmenleri_getir
from helpers.utils import gun_string_to_list, saat_str_to_time

def saatler_uyusuyor(mu, sinif_bas, sinif_bit, ogretmen_bas, ogretmen_bit):
    if None in (sinif_bas, sinif_bit, ogretmen_bas, ogretmen_bit):
        return False
    return ogretmen_bas <= sinif_bas and ogretmen_bit >= sinif_bit


def gunler_uyusuyor(mu_sinif, mu_ogretmen):
    mu_sinif = mu_sinif.strip().lower()
    mu_ogretmen = [g.strip().lower() for g in mu_ogretmen]
    return mu_sinif in mu_ogretmen

def atama_opsiyon_1(ilce_id):
    siniflar = siniflari_getir(ilce_id)
    ogretmenler = ogretmenleri_getir(ilce_id)
    atamalar = []
    atanan_siniflar = set()

    for sinif in siniflar:
        print(f"🎯 SINIF: {sinif['ad']} | {sinif['gun']} [{sinif['baslangic']} - {sinif['bitis']}]")

        if sinif["id"] in atanan_siniflar:
            print("  ⛔ Zaten atanmış.")
            continue

        en_iyi_skor = -1
        en_iyi_sinif = None
        en_iyi_ogretmen = None

        for ogretmen in ogretmenler:
            print(f"  🔍 Öğretmen: {ogretmen['ad']} | {ogretmen['calisma_gunu']} [{ogretmen['baslangic']} - {ogretmen['bitis']}]")

            ogretmen_gunler = gun_string_to_list(ogretmen["calisma_gunu"])
            ogretmen_bas = saat_str_to_time(ogretmen["baslangic"])
            ogretmen_bit = saat_str_to_time(ogretmen["bitis"])

            if not gunler_uyusuyor(sinif["gun"], ogretmen_gunler):
                print("    ❌ Gün uyuşmuyor!")
                continue
            if not saatler_uyusuyor("kontrol", sinif["baslangic"], sinif["bitis"], ogretmen_bas, ogretmen_bit):
                print("    ❌ Saat uyuşmuyor!")
                continue

            print("    ✅ Eşleşme bulundu. Atama adayı.")

            skor = ogretmen["puan"] * sinif["ogrenci"]
            if skor > en_iyi_skor:
                en_iyi_skor = skor
                en_iyi_sinif = sinif
                en_iyi_ogretmen = ogretmen

        if en_iyi_sinif and en_iyi_ogretmen:
            atamalar.append((en_iyi_ogretmen, en_iyi_sinif))
            atanan_siniflar.add(en_iyi_sinif["id"])

    return atamalar

def atama_opsiyon_2(ilce_id):
    siniflar = siniflari_getir(ilce_id)
    ogretmenler = ogretmenleri_getir(ilce_id)
    atamalar = []
    atanan_siniflar = set()

    for ogretmen in ogretmenler:
        en_iyi_skor = -1
        en_iyi_sinif = None
        ogretmen_gunler = gun_string_to_list(ogretmen["calisma_gunu"])
        ogretmen_bas = saat_str_to_time(ogretmen["baslangic"])
        ogretmen_bit = saat_str_to_time(ogretmen["bitis"])

        for sinif in siniflar:
            if sinif["id"] in atanan_siniflar:
                continue
            if not gunler_uyusuyor(sinif["gun"], ogretmen_gunler):
                continue
            if not saatler_uyusuyor(sinif["baslangic"], sinif["bitis"], ogretmen_bas, ogretmen_bit):
                continue

            if sinif["seviye"] == "2":
                uyum = ogretmen["uyum_2"]
            elif sinif["seviye"] == "3-4":
                uyum = ogretmen["uyum_34"]
            elif sinif["seviye"] == "5-6":
                uyum = ogretmen["uyum_56"]
            else:
                uyum = 0

            skor = (ogretmen["puan"] + uyum) * sinif["ogrenci"]

            if skor > en_iyi_skor:
                en_iyi_skor = skor
                en_iyi_sinif = sinif

        if en_iyi_sinif:
            atamalar.append((ogretmen, en_iyi_sinif))
            atanan_siniflar.add(en_iyi_sinif["id"])

    return atamalar
def atama_opsiyon_3(ilce_id):
    siniflar = siniflari_getir(ilce_id)
    ogretmenler = ogretmenleri_getir(ilce_id)
    atamalar = []
    atanan_siniflar = set()

    for ogretmen in ogretmenler:
        en_iyi_skor = -1
        en_iyi_sinif = None
        ogretmen_gunler = gun_string_to_list(ogretmen["calisma_gunu"])
        ogretmen_bas = saat_str_to_time(ogretmen["baslangic"])
        ogretmen_bit = saat_str_to_time(ogretmen["bitis"])

        for sinif in siniflar:
            if sinif["id"] in atanan_siniflar:
                continue
            if not gunler_uyusuyor(sinif["gun"], ogretmen_gunler):
                continue
            if not saatler_uyusuyor(sinif["baslangic"], sinif["bitis"], ogretmen_bas, ogretmen_bit):
                continue

            if sinif["seviye"] == "2":
                uyum = ogretmen["uyum_2"]
            elif sinif["seviye"] == "3-4":
                uyum = ogretmen["uyum_34"]
            elif sinif["seviye"] == "5-6":
                uyum = ogretmen["uyum_56"]
            else:
                uyum = 0

            skor = uyum * sinif["ogrenci"]

            if skor > en_iyi_skor:
                en_iyi_skor = skor
                en_iyi_sinif = sinif

        if en_iyi_sinif:
            atamalar.append((ogretmen, en_iyi_sinif))
            atanan_siniflar.add(en_iyi_sinif["id"])

    return atamalar


from db import supabase
import streamlit as st

def atamalari_temizle():
    try:
        supabase.table("atamalar").delete().neq("id", 0).execute()
    except Exception as e:
        st.error(f"Atamalar temizlenirken hata oluştu: {e}")

def atama_kaydet(atamalar):
    try:
        for ogretmen, sinif in atamalar:
            supabase.table("atamalar").insert({
                "ogretmen_id": ogretmen["id"],
                "sinif_id": sinif["id"],
                "gun": sinif["gun"],
                "baslangic": sinif["baslangic"],
                "bitis": sinif["bitis"]
            }).execute()
    except Exception as e:
        st.error(f"Atama kaydedilirken hata oluştu: {e}")
