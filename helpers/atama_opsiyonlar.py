from db import supabase
from helpers.utils import gun_string_to_list, saat_str_to_time
import datetime

def veri_yukle():
    siniflar = supabase.table("siniflar").select("*").execute().data
    ogretmenler = supabase.table("ogretmenler").select("*").execute().data
    return siniflar, ogretmenler

def saatler_uyusuyor(sinif, ogretmen):
    try:
        sinif_bas = saat_str_to_time(sinif.get("baslangic"))
        sinif_bit = saat_str_to_time(sinif.get("bitis"))
        ogretmen_bas = saat_str_to_time(ogretmen.get("baslangic"))
        ogretmen_bit = saat_str_to_time(ogretmen.get("bitis"))

        if None in (sinif_bas, sinif_bit, ogretmen_bas, ogretmen_bit):
            return False

        return ogretmen_bas <= sinif_bas and ogretmen_bit >= sinif_bit
    except Exception as e:
        print("Saat karşılaştırma hatası:", e)
        return False


def opsiyon_puani(ogretmen, sinif, opsiyon):
    if opsiyon == 1:
        return ogretmen.get("puan", 0) * sinif.get("ogrenci", 0)
    else:
        seviye = sinif.get("seviye", "")

        if seviye == "3-4":
            uyum_key = "uyum_34"
        elif seviye == "5-6":
            uyum_key = "uyum_56"
        else:
            uyum_key = "uyum_2"

        uyum = ogretmen.get(uyum_key, 0)
        puan = ogretmen.get("puan", 0)
        ogrenci = sinif.get("ogrenci", 0)

        if opsiyon == 2:
            return ((puan + uyum) / 2) * ogrenci
        elif opsiyon == 3:
            return uyum * ogrenci



def atama_yap(opsiyon):
    siniflar, ogretmenler = veri_yukle()
    atamalar = []
    ogretmen_sayac = {o["id"]: 0 for o in ogretmenler}

    for sinif in siniflar:
        uygunlar = []
        for ogretmen in ogretmenler:
            if sinif["ilce_id"] != ogretmen["ilce_id"]:
                continue
            if sinif["gun"] not in gun_string_to_list(ogretmen["calisma_gunu"]):
                continue
            if not saatler_uyusuyor(sinif, ogretmen):
                continue
            if ogretmen_sayac[ogretmen["id"]] >= ogretmen.get("max_sinif", 1):
                continue

            puan = opsiyon_puani(ogretmen, sinif, opsiyon)
            uygunlar.append((puan, ogretmen))

        if uygunlar:
            secilen = max(uygunlar, key=lambda x: x[0])[1]
            ogretmen_sayac[secilen["id"]] += 1
            atamalar.append({
                "sinif_id": sinif["id"],
                "sinif_ad": sinif["ad"],
                "ogretmen_id": secilen["id"],
                "ogretmen_ad": secilen["isim"],
                "gun": sinif["gun"],
                "baslangic": sinif["baslangic"],
                "bitis": sinif["bitis"],
                "ogrenci": sinif["ogrenci"]
            })

    return atamalar

def atama_opsiyon_1():
    return atama_yap(1)

def atama_opsiyon_2():
    return atama_yap(2)

def atama_opsiyon_3():
    return atama_yap(3)
