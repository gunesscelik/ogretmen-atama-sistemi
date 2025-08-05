import streamlit as st
from helpers.il import illeri_getir, il_ekle, il_sil
from helpers.ilce import ilceleri_getir, ilce_ekle, ilce_sil
from helpers.sinif import siniflari_getir, sinif_ekle, sinif_sil
from helpers.ogretmen import ogretmenleri_getir, ogretmen_ekle, ogretmen_sil
from helpers.utils import saat_str_to_time, time_to_str, gun_string_to_list
from helpers.atama import atama_kaydet, atamalari_temizle
from helpers.atama_opsiyonlar import atama_opsiyon_1, atama_opsiyon_2, atama_opsiyon_3
import pandas as pd

st.set_page_config(page_title="Öğretmen Atama Sistemi", layout="wide")
st.title("👩‍🏫 Öğretmen Atama Sistemi")

sekme = st.sidebar.selectbox("İşlem Seçiniz", ["İller", "İlçeler", "Sınıflar", "Öğretmenler", "Atama"])

if sekme == "İller":
    st.header("📍 İller")

    # Mevcut illeri getir
    iller = illeri_getir()
    for il in iller:
        st.write(f"- {il['ad']} (ID: {il['id']})")

    # Yeni il ekleme
    yeni_il = st.text_input("Yeni İl Adı")
    if st.button("İl Ekle") and yeni_il:
        try:
            il_ekle(yeni_il)
            st.cache_data.clear()  # önce cache'i temizle
            st.success("İl başarıyla eklendi.")  # sonra başarı mesajı ver
            st.rerun()
  # sayfayı yeniden başlat
        except Exception as e:
            st.error(f"İl eklenirken hata oluştu: {e}")

    # ✅ İl silme - doğru girintili hali
    if iller:
        il_id_sil = st.selectbox("Silinecek İl", options=[(il["id"], il["ad"]) for il in iller], format_func=lambda x: x[1])
        if st.button("İl Sil"):
            try:
                il_sil(il_id_sil[0])
                st.cache_data.clear()
                st.success("İl silindi.")
                st.rerun()

            except Exception as e:
                st.error(f"İl silinirken hata oluştu: {e}")
    else:
        st.info("Henüz eklenmiş bir il yok.")






elif sekme == "İlçeler":
    st.header("🌇️ İlçeler")
    iller = illeri_getir()
    il_sec = st.selectbox("İl Seçiniz", options=iller, format_func=lambda x: x["ad"])
    ilceler = ilceleri_getir(il_sec["id"])
    for ilce in ilceler:
        st.write(f"- {ilce['ad']} (ID: {ilce['id']})")
    yeni_ilce = st.text_input("Yeni İlçe Adı")
    if st.button("İlçe Ekle") and yeni_ilce:
        ilce_ekle(yeni_ilce, il_sec["id"])
        st.success("İlçe eklendi.")
        st.rerun()


    ilce_id_sil = st.selectbox("Silinecek İlçe", options=[(ilce["id"], ilce["ad"]) for ilce in ilceler], format_func=lambda x: x[1])
    if st.button("İlçe Sil"):
        ilce_sil(ilce_id_sil[0])
        st.success("İlçe silindi.")
        st.rerun()

elif sekme == "Sınıflar":
    st.header("🏫 Sınıflar")
    iller = illeri_getir()
    il_sec = st.selectbox("İl Seçiniz", iller, format_func=lambda x: x["ad"])
    ilceler = ilceleri_getir(il_sec["id"])
    ilce_sec = st.selectbox("İlçe Seçiniz", ilceler, format_func=lambda x: x["ad"])
    siniflar = siniflari_getir(ilce_sec["id"])
    for sinif in siniflar:
        st.write(f"- {sinif['ad']} ({sinif['ogrenci']} öğrenci) | {sinif['gun']} {sinif['seviye']} [{sinif['baslangic']}-{sinif['bitis']}]")

    with st.form("Sınıf Ekleme"):
        ad = st.text_input("Sınıf Adı")
        ogrenci = st.number_input("Öğrenci Sayısı", 1)
        gun = st.selectbox("Gün", ["Cumartesi", "Pazar"])

        seviye = st.selectbox("Seviye", ["2", "3-4", "5-6"])
        bas = st.time_input("Başlangıç Saati")
        bit = st.time_input("Bitiş Saati")
        ekle = st.form_submit_button("Sınıfı Ekle")
        if ekle:
            sinif_ekle(ad, ogrenci, ilce_sec["id"], gun, seviye, bas.strftime("%H:%M"), bit.strftime("%H:%M"))
            st.success("Sınıf eklendi.")
            st.rerun()


    silinecek_sinif = st.selectbox("Sınıf Sil", [(s["id"], s["ad"]) for s in siniflar], format_func=lambda x: x[1])
    if st.button("Sınıf Sil"):
        sinif_sil(silinecek_sinif[0])
        st.success("Sınıf silindi.")
        st.rerun()


elif sekme == "Öğretmenler":
    st.header("🧑‍🏫 Öğretmenler")
    iller = illeri_getir()
    il_sec = st.selectbox("İl Seç", iller, format_func=lambda x: x["ad"])
    ilceler = ilceleri_getir(il_sec["id"])
    ilce_sec = st.selectbox("İlçe Seç", ilceler, format_func=lambda x: x["ad"])
    ogretmenler = ogretmenleri_getir(ilce_sec["id"])
    for ogretmen in ogretmenler:
        st.write(f"- {ogretmen['isim']} | Puan: {ogretmen['puan']} | Max Sınıf: {ogretmen['max_sinif']} | Uyum: 2: {ogretmen['uyum_2']}, 3-4: {ogretmen['uyum_34']}, 5-6: {ogretmen['uyum_56']} | Günler: {ogretmen['calisma_gunu']} | Saat: {ogretmen['baslangic']}-{ogretmen['bitis']}")
    with st.form("Öğretmen Ekleme"):
        isim= st.text_input("Ad Soyad")
        puan = st.number_input("Puan", 0, 100)
        calisma_gunleri = st.multiselect(
            "Çalışma Günleri",
            ["Cumartesi", "Pazar"],
            help="Sadece hafta sonu günleri seçilebilir."
        )

        max_sinif = st.number_input("Maksimum Sınıf Sayısı", 1, 5, 1)
        uyum_2 = st.slider("2. Sınıf Uyum", 0, 100, 50)
        uyum_34 = st.slider("3-4. Sınıf Uyum", 0, 100, 50)
        uyum_56 = st.slider("5-6. Sınıf Uyum", 0, 100, 50)
        bas = st.time_input("Başlangıç Saati")
        bit = st.time_input("Bitiş Saati")
        ekle = st.form_submit_button("Öğretmeni Ekle")
        if ekle:
            basarili = ogretmen_ekle(isim, puan, ilce_sec["id"], calisma_gunleri, max_sinif, uyum_2, uyum_34, uyum_56, bas.strftime("%H:%M"), bit.strftime("%H:%M"))
            if basarili:
                st.success("Öğretmen eklendi.")
                st.rerun()

            else:
                st.error("Öğretmen eklenemedi.")



    if ogretmenler:
        silinecek_ogretmen = st.selectbox(
            "Öğretmen Sil", 
            [(o["id"], o["isim"]) for o in ogretmenler], 
            format_func=lambda x: x[1]
        )

        if st.button("Öğretmeni Sil"):
            secilen_id = silinecek_ogretmen[0]
            print("Seçilen öğretmen ID:", secilen_id)
            basarili = ogretmen_sil(secilen_id)
            if basarili:
                st.success("Öğretmen silindi.")
                st.rerun()
            else:
                st.error("Silme işlemi yapılamadı veya kayıt bulunamadı.")
    else:
        st.info("Silinecek öğretmen bulunamadı.")




elif sekme == "Atama":
    st.header("🔄 Öğretmen Atama")

    # 🔽 İl ve İlçe seçimini kullanıcıdan alıyoruz
    iller = illeri_getir()
    il_sec = st.selectbox("İl Seçin", options=iller, format_func=lambda x: x["ad"])

    ilceler = ilceleri_getir(il_sec["id"])
    ilce_sec = st.selectbox("İlçe Seçin", options=ilceler, format_func=lambda x: x["ad"])

    ilce_id = ilce_sec["id"]  # ✅ artık ilce_id tanımlı

    # Atama opsiyonunu seç
    opsiyon = st.selectbox(
        "Atama Yöntemini Seçin",
        (
            "Puan × Öğrenci (Opsiyon 1)", 
            "Puan + Uyum × Öğrenci (Opsiyon 2)",
            "Sadece Uyum × Öğrenci (Opsiyon 3)"
        )
    )


    if st.button("📌 Atamayı Başlat"):
        if opsiyon == "Puan × Öğrenci (Opsiyon 1)":
            atamalar = atama_opsiyon_1()
        elif opsiyon == "Puan + Uyum × Öğrenci (Opsiyon 2)":
            atamalar = atama_opsiyon_2()
        else:
            atamalar = atama_opsiyon_3()

        atamalari_temizle()
        st.success(f"{len(atamalar)} atama kaydedildi!")

        st.subheader("📋 Atama Sonuçları")

        if not atamalar:
            st.info("Herhangi bir atama yapılamadı.")
        else:
            # 📋 Atama sonuçlarını tablo olarak göster
            df_atamalar = pd.DataFrame([
                {
                    "Sınıf": a["sinif_ad"],
                    "Öğretmen": a["ogretmen_ad"],
                    "Gün": a["gun"],
                    "Saat": f"{a['baslangic']} - {a['bitis']}",
                    "Öğrenci Sayısı": a["ogrenci"]
                }
                for a in atamalar
            ])
            st.dataframe(df_atamalar, use_container_width=True)

            # ❌ Atanamayan sınıfları göster
            siniflar = siniflari_getir(ilce_id)
            atanan_sinif_idler = [a["sinif_id"] for a in atamalar]
            atanamayan_siniflar = [s for s in siniflar if s["id"] not in atanan_sinif_idler]

            st.subheader("📌 Atanamayan Sınıflar")
            if not atanamayan_siniflar:
                st.success("Tüm sınıflar atandı!")
            else:
                for s in atanamayan_siniflar:
                    st.markdown(f"- **{s['ad']}** | {s['gun']} [{s['baslangic']} - {s['bitis']}]")

            # ❌ Atanamayan öğretmenleri göster
            ogretmenler = ogretmenleri_getir(ilce_id)
            atanan_ogretmen_idler = [a["ogretmen_id"] for a in atamalar]
            atanamayan_ogretmenler = [o for o in ogretmenler if o["id"] not in atanan_ogretmen_idler]

            st.subheader("📌 Atanamayan Öğretmenler")
            if not atanamayan_ogretmenler:
                st.success("Tüm öğretmenler atandı!")
            else:
                for o in atanamayan_ogretmenler:
                    st.markdown(f"- **{o['ad']}** | Günler: {o['calisma_gunu']} | Saat: {o['baslangic']} - {o['bitis']}")


