# helpers/ui.py
import streamlit as st

def sayfa_basligi_yaz(title: str):
    st.markdown(f"## {title}")
    st.markdown("---")

def bilgi_mesaji(mesaj: str):
    st.info(mesaj)

def basari_mesaji(mesaj: str):
    st.success(mesaj)

def hata_mesaji(mesaj: str):
    st.error(mesaj)

def onay_sorusu(mesaj: str) -> bool:
    return st.confirm(mesaj)

def dikey_bosluk(kac_satir: int = 1):
    for _ in range(kac_satir):
        st.markdown("<br>", unsafe_allow_html=True)
