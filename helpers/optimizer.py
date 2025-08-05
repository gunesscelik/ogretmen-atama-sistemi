# helpers/optimizer.py
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary

def siniflara_ogretmen_atama(siniflar, ogretmenler, uyum_ile_mi=False, sadece_uyum_mu=False):
    prob = LpProblem("Ogretmen_Atama", LpMaximize)

    # Değişkenleri oluştur
    atama = {
        (o["id"], s["id"]): LpVariable(f"x_{o['id']}_{s['id']}", 0, 1, LpBinary)
        for o in ogretmenler for s in siniflar
    }

    # Amaç fonksiyonu: Uyum + Puan * Öğrenci sayısı
    if sadece_uyum_mu:
        prob += lpSum(
            atama[o["id"], s["id"]] * ogretmen_uyumu(o, s)
            for o in ogretmenler for s in siniflar
        )
    elif uyum_ile_mi:
        prob += lpSum(
            atama[o["id"], s["id"]] * (
                0.5 * ogretmen_uyumu(o, s) +
                0.5 * o["puan"] * s["ogrenci"]
            )
            for o in ogretmenler for s in siniflar
        )
    else:
        prob += lpSum(
            atama[o["id"], s["id"]] * (o["puan"] * s["ogrenci"])
            for o in ogretmenler for s in siniflar
        )

    # Her sınıfa en fazla bir öğretmen
    for s in siniflar:
        prob += lpSum(atama[o["id"], s["id"]] for o in ogretmenler) <= 1

    # Her öğretmene en fazla max_sinif sınıf
    for o in ogretmenler:
        prob += lpSum(atama[o["id"], s["id"]] for s in siniflar) <= o["max_sinif"]

    # Uygun gün ve saat aralığında kontrol
    for o in ogretmenler:
        for s in siniflar:
            if not gun_ve_saat_uygun_mu(o, s):
                prob += atama[o["id"], s["id"]] == 0

    prob.solve()

    atamalar = [
        {"ogretmen_id": o["id"], "sinif_id": s["id"]}
        for o in ogretmenler for s in siniflar
        if atama[o["id"], s["id"]].varValue == 1
    ]
    return atamalar


def ogretmen_uyumu(ogretmen, sinif):
    seviye = sinif["seviye"]
    if seviye == "2":
        return ogretmen["uyum_2"]
    elif seviye in ("3", "4"):
        return ogretmen["uyum_34"]
    elif seviye in ("5", "6"):
        return ogretmen["uyum_56"]
    return 0


def gun_ve_saat_uygun_mu(ogretmen, sinif):
    if ogretmen["calisma_gunu"] != sinif["gun"]:
        return False
    if not ogretmen["baslangic"] or not ogretmen["bitis"]:
        return False
    return ogretmen["baslangic"] <= sinif["baslangic"] and ogretmen["bitis"] >= sinif["bitis"]


