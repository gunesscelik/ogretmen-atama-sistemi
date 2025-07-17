# -*- coding: utf-8 -*-
import streamlit as st
import psycopg2
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, value, LpStatus
from datetime import time
import pandas as pd
from db import get_connection  # Zaten varsa tekrar yazma
@st.cache_data(ttl=300)  # 5 dakika önbellekte tut
def ogretmenleri_getir_ilceye_gore(ilce_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, ad, puan, calisma_gunu, max_sinif,
                       uyum_2, uyum_34, uyum_56, baslangic, bitis
                FROM ogretmenler
                WHERE ilce_id = %s
            """, (ilce_id,))
            return cur.fetchall()

# --- Streamlit Ayarı ---
st.set_page_config(page_title="📚 Öğretmen Atama Sistemi", layout="wide")
st.title("📘 Öğretmen Atama Sistemi")
# --- Sekmeler ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏙️ İl İşlestmleri", 
    "🏘️ İlçe İşlemleri", 
    "🏫 Sınıf İşlemleri", 
    "👩‍🏫 Öğretmen İşlemleri", 
    "📊 Toplu Atama"
])
# --- Veritabanı Bağlantısı ---
def get_connection():
    return psycopg2.connect(
        host="dpg-d1s52hh5pdvs73aenf3g-a.oregon-postgres.render.com",
        database="yeniatama",
        user="yeniatama_user",
        password="l7t6EuA6OD5YuTDhiKLdmfO4eRqUBm6x",
        port=5432
    )

# --- Veritabanı Tabloları Oluştur ---
def tablo_olustur():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS iller (
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100) UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ilceler (
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100),
            il_id INTEGER REFERENCES iller(id)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS siniflar (
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100),
            ogrenci INT,
            ilce_id INTEGER REFERENCES ilceler(id),
            gun VARCHAR(20),
            seviye VARCHAR(10),
            baslangic TIME,
            bitis TIME
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ogretmenler (
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100),
            puan INT,
            ilce_id INTEGER REFERENCES ilceler(id),
            calisma_gunu VARCHAR(20),
            max_sinif INT DEFAULT 1,
            uyum_2 INT DEFAULT 0,
            uyum_34 INT DEFAULT 0,
            uyum_56 INT DEFAULT 0
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
# Tablo oluşturma fonksiyonunu ilk çalıştırmada çağır
tablo_olustur()
# --- İl Yardımcı Fonksiyonlar ---
def iller_getir():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, ad FROM iller")
            return cur.fetchall()
def il_ekle(ad):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO iller (ad)
                VALUES (%s)
                ON CONFLICT (ad) DO NOTHING
            """, (ad,))
            conn.commit()
def il_sil(ad):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM iller WHERE ad=%s", (ad,))
            il_row = cur.fetchone()
            if il_row:
                il_id = il_row[0]
                cur.execute("SELECT id FROM ilceler WHERE il_id=%s", (il_id,))
                ilceler = cur.fetchall()
                for ilce_row in ilceler:
                    ilce_id = ilce_row[0]
                    cur.execute("DELETE FROM siniflar WHERE ilce_id=%s", (ilce_id,))
                    cur.execute("DELETE FROM ogretmenler WHERE ilce_id=%s", (ilce_id,))
                cur.execute("DELETE FROM ilceler WHERE il_id=%s", (il_id,))
                cur.execute("DELETE FROM iller WHERE id=%s", (il_id,))
            conn.commit()
# --- TAB1: İl Ekle / Sil ---
with tab1:
    st.subheader("🏙️ İl Ekle / Sil")
    il_adi = st.text_input("İl adı giriniz")
    if st.button("İl Ekle", key="il_ekle_btn"):
        if il_adi:
            il_ekle(il_adi)
            st.success(f"{il_adi} başarıyla eklendi.")
    iller = iller_getir()
    if iller:
        il_adlari = [ad for (_, ad) in iller]
        secilen_il = st.selectbox("Silinecek il", il_adlari, key="il_sil_sec")
        if st.button("İli Sil", key="il_sil_btn"):
            il_sil(secilen_il)
            st.success(f"{secilen_il} silindi.")
    else:
        st.info("Henüz kayıtlı il yok.")
# --- İlçe Yardımcı Fonksiyonlar ---
def ilceler_getir(il_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, ad FROM ilceler WHERE il_id=%s", (il_id,))
            return cur.fetchall()
def ilce_ekle(ad, il_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ilceler (ad, il_id) VALUES (%s, %s)", (ad, il_id))
            conn.commit()
def ilce_sil(ad, il_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ilceler WHERE ad=%s AND il_id=%s", (ad, il_id))
            ilce_row = cur.fetchone()
            if ilce_row:
                ilce_id = ilce_row[0]
                cur.execute("DELETE FROM siniflar WHERE ilce_id=%s", (ilce_id,))
                cur.execute("DELETE FROM ogretmenler WHERE ilce_id=%s", (ilce_id,))
                cur.execute("DELETE FROM ilceler WHERE id=%s", (ilce_id,))
            conn.commit()
# --- TAB2: İlçe Ekle / Sil ---
with tab2:
    st.subheader("🏘️ İlçe Ekle / Sil")
    iller = iller_getir()
    if iller:
        il_id_dict = {ad: id for (id, ad) in iller}
        secilen_il = st.selectbox("İl seç", list(il_id_dict.keys()), key="ilce_il_sec")
        ilce_adi = st.text_input("İlçe adı giriniz")
        if st.button("İlçe Ekle", key="ilce_ekle_btn"):
            if ilce_adi:
                ilce_ekle(ilce_adi, il_id_dict[secilen_il])
                st.success(f"{ilce_adi} başarıyla eklendi.")
        secili_il_id = il_id_dict[secilen_il]
        ilceler = ilceler_getir(secili_il_id)
        if ilceler:
            ilce_adlari = [ad for (_, ad) in ilceler]
            silinecek_ilce = st.selectbox("Silinecek ilçe", ilce_adlari, key="ilce_sil_sec")
            if st.button("İlçeyi Sil", key="ilce_sil_btn"):
                ilce_sil(silinecek_ilce, secili_il_id)
                st.success(f"{silinecek_ilce} silindi.")
        else:
            st.info("Bu ilde henüz ilçe yok.")
    else:
        st.warning("Önce il eklemelisiniz.")
# --- Sınıf Yardımcı Fonksiyonları ---
def siniflari_getir(ilce_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, ad, ogrenci, gun, seviye, baslangic, bitis
                FROM siniflar
                WHERE ilce_id=%s
            """, (ilce_id,))
            return cur.fetchall()
def ogretmenleri_getir_ilceye_gore(ilce_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, ad, puan, calisma_gunu, max_sinif,
                       uyum_2, uyum_34, uyum_56, baslangic, bitis
                FROM ogretmenler
                WHERE ilce_id=%s
            """, (ilce_id,))
            return cur.fetchall()
def ogretmen_ekle(ad, puan, ilce_id, calisma_gunu, max_sinif, uyum_dict, bas, bit):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ogretmenler 
                (ad, puan, ilce_id, calisma_gunu, max_sinif, uyum_2, uyum_34, uyum_56, baslangic, bitis)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ad, puan, ilce_id, calisma_gunu, max_sinif,
                uyum_dict["2"], uyum_dict["3-4"], uyum_dict["5-6"],
                bas, bit
            ))
            conn.commit()
def ogretmen_guncelle(ogretmen_id, ad, puan, gun, max_sinif, uyum_dict, bas, bit):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE ogretmenler
                SET ad=%s, puan=%s, calisma_gunu=%s, max_sinif=%s,
                    uyum_2=%s, uyum_34=%s, uyum_56=%s,
                    baslangic=%s, bitis=%s
                WHERE id=%s
            """, (
                ad, puan, gun, max_sinif,
                uyum_dict["2"], uyum_dict["3-4"], uyum_dict["5-6"],
                bas, bit, ogretmen_id
            ))
            conn.commit()


def sinif_ekle(ad, ogrenci, ilce_id, gun, seviye, baslangic, bitis):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO siniflar (ad, ogrenci, ilce_id, gun, seviye, baslangic, bitis)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ad, ogrenci, ilce_id, gun, seviye, baslangic, bitis))
            conn.commit()
def sinif_sil(ad, ilce_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM siniflar WHERE ad=%s AND ilce_id=%s", (ad, ilce_id))
            conn.commit()
def sinif_guncelle(sinif_id, ad, ogrenci, gun, seviye, baslangic, bitis):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE siniflar
                SET ad=%s, ogrenci=%s, gun=%s, seviye=%s, baslangic=%s, bitis=%s
                WHERE id=%s
            """, (ad, ogrenci, gun, seviye, baslangic, bitis, sinif_id))
            conn.commit()
# --- TAB3: Sınıf Ekle / Sil / Güncelle ---
with tab3:
    st.subheader("🏫 Sınıf İşlemleri")
    iller = iller_getir()
    ilce_listesi = []
    for il_id, il_ad in iller:
        ilceler = ilceler_getir(il_id)
        for ilce_id, ilce_ad in ilceler:
            ilce_listesi.append((ilce_id, f"{il_ad} / {ilce_ad}"))
    if ilce_listesi:
        ilce_adlari = [ad for (_, ad) in ilce_listesi]
        ilce_dict = {ad: id for (id, ad) in ilce_listesi}
        secilen_ilce = st.selectbox("İlçe seç", ilce_adlari, key="sinif_ilce_sec")
        sinif_adi = st.text_input("Sınıf adı")
        ogrenci_sayisi = st.number_input("Öğrenci sayısı", min_value=1, step=1)
        GUN_SECENEKLERI = ["Cumartesi", "Pazar", "Her İkisi"]
        sinif_gunu = st.selectbox("Ders günü", GUN_SECENEKLERI)
        SEVIYE_SECENEKLERI = ["2", "3-4", "5-6"]
        sinif_seviye = st.selectbox("Sınıf seviyesi", SEVIYE_SECENEKLERI)
        baslangic = st.time_input("Ders başlangıç saati", value=time(9, 0))
        bitis = st.time_input("Ders bitiş saati", value=time(10, 0))
        if st.button("Sınıfı Ekle", key="sinif_kaydet_btn"):
            if baslangic >= bitis:
                st.error("Başlangıç saati, bitiş saatinden önce olmalıdır.")
            else:
                sinif_ekle(sinif_adi, ogrenci_sayisi, ilce_dict[secilen_ilce],
                           sinif_gunu, sinif_seviye, baslangic, bitis)
                st.success(f"{sinif_adi} başarıyla eklendi.")
        ilce_id = ilce_dict[secilen_ilce]
        siniflar = siniflari_getir(ilce_id)
        if siniflar:
            st.markdown("### 📋 Mevcut Sınıflar")
            for _, ad, ogr, gun, seviye, bas, bit in siniflar:
                st.write(f"- {ad} | Seviye: {seviye} | Gün: {gun} | Saat: {bas.strftime('%H:%M')} - {bit.strftime('%H:%M')} | Öğrenci: {ogr}")
            # Silme
            silinecek_sinif = st.selectbox("Silinecek sınıf", [ad for (_, ad, *_rest) in siniflar], key="sinif_sil")
            if st.button("Sınıfı Sil", key="sinif_sil_btn"):
                sinif_sil(silinecek_sinif, ilce_id)
                st.success(f"{silinecek_sinif} silindi.")
            # Güncelleme
            st.markdown("### ✏️ Sınıf Bilgisi Güncelle")
            guncellenecek_sinif = st.selectbox("Düzenlenecek sınıf", siniflar, format_func=lambda x: x[1], key="sinif_duzenle")
            if guncellenecek_sinif:
                sid, sad, sogr, sgun, ssev, sbas, sbit = guncellenecek_sinif
                ad = st.text_input("Sınıf adı", value=sad, key="guncel_ad_sinif")
                ogr = st.number_input("Öğrenci sayısı", value=sogr, key="guncel_ogr_sinif")
                gun = st.selectbox("Gün", GUN_SECENEKLERI, index=GUN_SECENEKLERI.index(sgun), key="guncel_gun_sinif")
                try:
                    index = SEVIYE_SECENEKLERI.index(ssev)
                except ValueError:
                    index = 0
                sev = st.selectbox("Seviye", SEVIYE_SECENEKLERI, index=index, key="guncel_sev_sinif")
                bas = st.time_input("Başlangıç", value=sbas, key="guncel_bas_sinif")
                bit = st.time_input("Bitiş", value=sbit, key="guncel_bit_sinif")
                if st.button("Sınıfı Güncelle"):
                    if bas >= bit:
                        st.error("Başlangıç saati, bitiş saatinden önce olmalı.")
                    else:
                        sinif_guncelle(sid, ad, ogr, gun, sev, bas, bit)
                        st.success(f"{sad} sınıfı güncellendi.")
        else:
            st.info("Bu ilçede henüz sınıf yok.")
    else:
        st.warning("Önce ilçe ekleyiniz.")
# --- TAB4: Öğretmen Ekle / Sil ---
with tab4:
    st.subheader("👩‍🏫 Öğretmen Ekle / Sil")
    iller = iller_getir()
    ilce_listesi = []
    for il_id, il_ad in iller:
        ilceler = ilceler_getir(il_id)
        for ilce_id, ilce_ad in ilceler:
            ilce_listesi.append((ilce_id, f"{il_ad} / {ilce_ad}"))
    if ilce_listesi:
        ilce_adlari = [ad for (_, ad) in ilce_listesi]
        ilce_dict = {ad: id for (id, ad) in ilce_listesi}
        secilen_ilce = st.selectbox("İlçe seç", ilce_adlari, key="ogrt_ilce")
        ogretmen_adi = st.text_input("Adı")
        ogretmen_puani = st.number_input("Başarı puanı", min_value=0)
        GUN_SECENEKLERI = ["Cumartesi", "Pazar", "Her İkisi"]
        ogretmen_gunu = st.selectbox("Çalışabileceği gün", GUN_SECENEKLERI)
        ogretmen_maxsinif = st.number_input("En fazla kaç sınıfa atanabilir?", min_value=1, max_value=10, value=1)
        ogretmen_bas = st.time_input("Başlangıç saati", value=time(10, 0))
        ogretmen_bit = st.time_input("Bitiş saati", value=time(15, 0))

        st.markdown("#### Sınıf Seviyesi Uyum Puanları (0–100)")
        uyum_dict = {}
        for seviye in ["2", "3-4", "5-6"]:
            uyum_dict[seviye] = st.number_input(f"{seviye} sınıf uyumu", min_value=0, max_value=100, key=f"uyum_{seviye}")
        if st.button("Kaydet", key="ogrt_kaydet_btn"):
            if ogretmen_adi:
                ogretmen_ekle(ogretmen_adi, ogretmen_puani, ilce_dict[secilen_ilce],
                              ogretmen_gunu, ogretmen_maxsinif, uyum_dict,ogretmen_bas, ogretmen_bit)
                st.success(f"{ogretmen_adi} başarıyla eklendi.")
        ilce_id = ilce_dict[secilen_ilce]
        ogretmenler = ogretmenleri_getir_ilceye_gore(ilce_id)
        if ogretmenler:
            st.markdown("### 📋 Mevcut Öğretmenler")
            for _, ad, puan, gun, maxs, u2, u34, u56, bas, bit in ogretmenler:
                st.write(f"- {ad} | Puan: {puan} | Gün: {gun} | max_sinif: {maxs} | Uyumlar: [2: {u2}, 3-4: {u34}, 5-6: {u56}]")






            # Güncelleme
            # Güncelleme
    st.markdown("### ✏️ Bilgileri Güncelle")
    guncellenecek = st.selectbox("Düzenlenecek", ogretmenler, format_func=lambda x: x[1], key="ogrt_duzenle")
    if guncellenecek:
        oid, oad, opuan, ogun, omax, u2, u34, u56, obas, obit = guncellenecek  # 10 değer
        ad = st.text_input("Ad", value=oad, key="guncel_ad_ogrt")
        puan = st.number_input("Puan", value=opuan, key="guncel_puan_ogrt")
        gun = st.selectbox("Gün", GUN_SECENEKLERI, index=GUN_SECENEKLERI.index(ogun), key="guncel_gun_ogrt")
        maxs = st.number_input("Max sınıf", value=omax, key="guncel_max_ogrt")
        bas = st.time_input("Başlangıç", value=obas, key="guncel_bas_ogrt")
        bit = st.time_input("Bitiş", value=obit, key="guncel_bit_ogrt")
        uyum_dict = {
            "2": st.number_input("Uyum 2", value=u2, key="guncel_u2"),
            "3-4": st.number_input("Uyum 3-4", value=u34, key="guncel_u34"),
            "5-6": st.number_input("Uyum 5-6", value=u56, key="guncel_u56"),
        }
        if st.button("Güncelle"):
            ogretmen_guncelle(oid, ad, puan, gun, maxs, uyum_dict, bas, bit)
            st.success(f"{oad} başarıyla güncellendi.")
        else:
            st.info("Bu ilçede henüz öğretmen yok.")
    else:
        st.warning("Önce ilçe ekleyin.")
# --- Yardımcı Fonksiyonlar ---
def gun_uyusuyor_mu(ogretmen, sinif):
    return (
        ogretmen[3] == sinif[3]
        or ogretmen[3] == "Her İkisi"
        or sinif[3] == "Her İkisi"
    )
def saatler_cakismiyor_mu(s1, s2):
    if s1[3] != s2[3]:
        return True  # farklı gün
    bas1, bit1 = s1[5], s1[6]
    bas2, bit2 = s2[5], s2[6]
    return bit1 <= bas2 or bit2 <= bas1
def saat_uyumlu_mu(ogretmen, sinif):
    """
    Öğretmenin çalışabileceği saatler, sınıfın ders saatini kapsıyor mu kontrol eder.
    """
    if not gun_uyusuyor_mu(ogretmen, sinif):
        return False
    ogretmen_baslangic = ogretmen[8]  # ogretmen tablosunda baslangic TIME
    ogretmen_bitis = ogretmen[9]      # ogretmen tablosunda bitis TIME
    sinif_baslangic = sinif[5]
    sinif_bitis = sinif[6]
    return ogretmen_baslangic <= sinif_baslangic and ogretmen_bitis >= sinif_bitis
# --- Atama Modeli ---
def atama_modeli(tum_ogretmenler, tum_siniflar, katsayi_fonksiyonu, baslik, zorunlu_atama=False):
    atama_komb = [
        (o[1], s[0])
        for o in tum_ogretmenler for s in tum_siniflar
        if saat_uyumlu_mu(o, s)
    ]
    model = LpProblem("OgretmenAtama", LpMaximize)
    atamalar = LpVariable.dicts("Atama", atama_komb, 0, 1, LpBinary)
    # Amaç fonksiyonu
    model += lpSum([
        katsayi_fonksiyonu(o, s) * atamalar[(o[1], s[0])]
        for o in tum_ogretmenler for s in tum_siniflar
        if saat_uyumlu_mu(o, s)
    ])
    # Her sınıfa en fazla 1 öğretmen atanabilir
    for s in tum_siniflar:
        model += lpSum([
            atamalar[(o[1], s[0])]
            for o in tum_ogretmenler
            if saat_uyumlu_mu(o, s)
        ]) <= 1
    # Her öğretmenin max_sinif kadar atanma hakkı
    for o in tum_ogretmenler:
        model += lpSum([
            atamalar[(o[1], s[0])]
            for s in tum_siniflar
            if saat_uyumlu_mu(o, s)
        ]) <= o[4]
    # Saat çakışmalarını engelle
    for o in tum_ogretmenler:
        uygun_siniflar = [s for s in tum_siniflar if saat_uyumlu_mu(o, s)]
        for i in range(len(uygun_siniflar)):
            for j in range(i + 1, len(uygun_siniflar)):
                s1 = uygun_siniflar[i]
                s2 = uygun_siniflar[j]
                if not saatler_cakismiyor_mu(s1, s2):
                    model += atamalar[(o[1], s1[0])] + atamalar[(o[1], s2[0])] <= 1
    # Her öğretmen en az 1 sınıfa atanmalı (isteğe bağlı)
    if zorunlu_atama:
        for o in tum_ogretmenler:
            model += lpSum([
                atamalar[(o[1], s[0])]
                for s in tum_siniflar if saat_uyumlu_mu(o, s)
            ]) >= 1
    # Modeli çöz
    model.solve()
    if LpStatus[model.status] != "Optimal":
        st.error("🚫 Çözüm bulunamadı. Kapasite veya saat çakışmaları nedeniyle.")
        return
    st.success(f"✅ {baslik} başarıyla tamamlandı.")
    # Atama sonuçlarını göster
    atama_listesi = []
    for (o_ad, s_id) in atama_komb:
        if atamalar[(o_ad, s_id)].varValue == 1:
            sinif = next((s for s in tum_siniflar if s[0] == s_id), None)
            if sinif:
                atama_listesi.append({
                    "Öğretmen": o_ad,
                    "Sınıf": sinif[1],
                    "Gün": sinif[3],
                    "Saat": f"{sinif[5].strftime('%H:%M')} – {sinif[6].strftime('%H:%M')}",
                    "Öğrenci": sinif[2]
                })
    if atama_listesi:
        st.markdown("### 📋 Atama Tablosu")
        st.table(pd.DataFrame(atama_listesi))
        st.info(f"🎯 Toplam Skor: {value(model.objective)}")
    else:
        st.warning("⚠️ Hiçbir atama yapılmadı.")
    # 🔍 Atanmayan sınıfları bul
    # 🔍 Atanmayan sınıfları bul
    atanan_sinif_idleri = set()
    for (o_ad, s_id) in atama_komb:
        if atamalar[(o_ad, s_id)].varValue == 1:
            atanan_sinif_idleri.add(s_id)
    atanmayan_siniflar = [s for s in tum_siniflar if s[0] not in atanan_sinif_idleri]
    if atanmayan_siniflar:
        st.markdown("### 🚫 Atanmayan Sınıflar")
        st.table(pd.DataFrame([{
            "Sınıf": s[1],
            "Gün": s[3],
            "Saat": f"{s[5].strftime('%H:%M')} – {s[6].strftime('%H:%M')}",
            "Öğrenci": s[2]
        } for s in atanmayan_siniflar]))
    # 🔍 Atanmayan öğretmenleri bul
    atanan_ogretmen_adlari = set()
    for (o_ad, s_id) in atama_komb:
        if atamalar[(o_ad, s_id)].varValue == 1:
            atanan_ogretmen_adlari.add(o_ad)
    atanmayan_ogretmenler = [o for o in tum_ogretmenler if o[1] not in atanan_ogretmen_adlari]
    if atanmayan_ogretmenler:
        st.markdown("### 🚫 Atanmayan Öğretmenler")
        st.table(pd.DataFrame([{
            "Ad": o[1],
            "Puan": o[2],
            "Gün": o[3],
            "Saat Aralığı": f"{o[8].strftime('%H:%M')} – {o[9].strftime('%H:%M')}",
            "Max Sınıf": o[4]
        } for o in atanmayan_ogretmenler]))

# --- TAB5: Toplu Atama ---
with tab5:
    st.subheader("📊 Toplu Atama (3 Farklı Opsiyon + Zorunlu Atama Seçeneği)")
    iller = iller_getir()
    if iller:
        il_id_dict = {ad: id for (id, ad) in iller}
        secilen_il = st.selectbox("İl seç", list(il_id_dict.keys()), key="atama_il")
        ilceler = ilceler_getir(il_id_dict[secilen_il])
        if ilceler:
            ilce_id_dict = {ad: id for (id, ad) in ilceler}
            secilen_ilce = st.selectbox("İlçe seç", list(ilce_id_dict.keys()), key="atama_ilce")
            ilce_id = ilce_id_dict[secilen_ilce]
            tum_siniflar = siniflari_getir(ilce_id)
            tum_ogretmenler = ogretmenleri_getir_ilceye_gore(ilce_id)
            if not tum_siniflar:
                st.warning("📌 Bu ilçede sınıf yok.")
            elif not tum_ogretmenler:
                st.warning("📌 Bu ilçede öğretmen yok.")
            else:
                zorunlu_mi = st.checkbox("Her öğretmen en az bir sınıfa atanmalı", value=False)
                if st.button("Opsiyon 1: Puan × Öğrenci"):
                    def katsayi1(o, s):
                        return o[2] * s[2]
                    atama_modeli(tum_ogretmenler, tum_siniflar, katsayi1,
                                 "Puan × Öğrenci", zorunlu_atama=zorunlu_mi)
                if st.button("Opsiyon 2: (Puan + Uyum)/2 × Öğrenci Sayısı"):
                    def katsayi2(o, s):
                        seviye = str(s[4])  # Burada seviye string yapılmalı
                        if seviye in ["3", "4"]:
                            seviye = "3-4"
                        elif seviye in ["5", "6"]:
                            seviye = "5-6"
                        uyum_map = {"2": 5, "3-4": 6, "5-6": 7}
                        uyum_index = uyum_map.get(seviye)
                        uyum = o[uyum_index]
                        return ((o[2] * 0.5 + uyum * 0.5) * s[2])
                    atama_modeli(tum_ogretmenler, tum_siniflar, katsayi2,
                                "Ortalama (Puan + Uyum) × Öğrenci", zorunlu_atama=zorunlu_mi)


                if st.button("Opsiyon 3: Sadece Uyum × Öğrenci"):
                    def katsayi3(o, s):
                        seviye = str(s[4])
                        if seviye in ["3", "4"]:
                            seviye = "3-4"
                        elif seviye in ["5", "6"]:
                            seviye = "5-6"
                        uyum_map = {"2": 5, "3-4": 6, "5-6": 7}
                        uyum_index = uyum_map.get(seviye)
                        if uyum_index is not None and uyum_index < len(o):
                            uyum = o[uyum_index]
                        else:
                            uyum = 0  # veya hata mesajı/logging
                        return uyum * s[2]
                    atama_modeli(tum_ogretmenler, tum_siniflar, katsayi3,
                                "Sadece Uyum × Öğrenci", zorunlu_atama=zorunlu_mi)
        else:
            st.warning("Bu ilde henüz ilçe yok.")
    else:
        st.warning("Henüz hiç il eklenmemiş.")