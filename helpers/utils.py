# helpers/utils.py
import datetime

def saat_str_to_time(saat_str):
    try:
        if not saat_str or saat_str.strip() == "":
            return None
        saat_str = saat_str.strip()
        if len(saat_str.split(":")) == 3:
            return datetime.datetime.strptime(saat_str, "%H:%M:%S").time()
        else:
            return datetime.datetime.strptime(saat_str, "%H:%M").time()
    except Exception as e:
        print("❗Saat dönüşüm hatası:", e)
        return None




def gun_string_to_list(gun_str):
    """
    Virgülle ayrılmış string'i listeye çevirir.
    Örnek: "Pazartesi,Salı" -> ["Pazartesi", "Salı"]
    """
    if not gun_str:
        return []
    return [g.strip() for g in gun_str.split(",")]

def gun_list_to_string(gun_list):
    """Listeyi tekrar virgülle ayrılmış string'e çevirir."""
    return ",".join(gun_list)

def time_to_str(t):
    """datetime.time nesnesini 'HH:MM' formatına çevirir."""
    if not t:
        return ""
    return t.strftime("%H:%M")

