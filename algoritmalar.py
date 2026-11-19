"""
İşlemci zamanlama algoritmaları - simülasyon.

Süre birimi: ms (tam sayı).
Öncelik: küçük sayı = daha önemli (1 en önemli).

Her algoritma bir "zaman çizelgesi" (Gantt için) üretir:
    [("Müzik", 0, 3), ("Klima", 3, 6), ...]  -> (görev, başlangıç, bitiş)
Bekleme süreleri bu çizelgeden TEK bir formülle hesaplanır:
    bekleme = bitiş - geliş - süre
"""
import random
from collections import deque

# Bir görevden diğerine geçişin (bağlam değiştirme) maliyeti, ms.
# Hoca: "boşalt, yükle de bir iştir" -> toplam süreye eklenir.
GECIS_MALIYETI = 1

# Aging ayarları (bizim algoritmamız): bekleyen iş her AGING_ARALIK ms'de
# önceliğini AGING_PUAN puan artırır. Denemeler: 5 ms çok agresif (herkes hızla
# öncelik 1 olup algoritma geliş sırasına dönüşüyor), 20 ms iyi denge.
AGING_ARALIK = 20
AGING_PUAN = 1

# --- Fren senaryosu (D): elle yazılmış 4 görev ---------------------------------
GOREVLER = [
    {"ad": "Müzik", "gelis": 0, "sure": 6, "oncelik": 4},
    {"ad": "Klima", "gelis": 1, "sure": 3, "oncelik": 3},
    {"ad": "Motor", "gelis": 2, "sure": 4, "oncelik": 2},
    {"ad": "Fren",  "gelis": 3, "sure": 2, "oncelik": 1},
]

# --- Rastgele senaryolar (A, B, C) ----------------------------------------------
# sure   : [(ağırlık, (en az, en çok)), ...]  iş süresi aralıkları
# gelis  : (en erken, en geç) geliş zamanı
# oncelik: 1,2,3,4 önceliklerinin ağırlıkları. Gerçekçi: çoğu iş düşük öncelikli,
#          az sayıda iş yüksek öncelikli (hocanın uyarısı: çoğu işe yüksek öncelik verme)
# Geliş penceresi toplam iş miktarına yakın seçildi: sistem yoğun ama kuyruk
# kontrolsüz şişmiyor (50 iş x ortalama süre ~ pencere).
SENARYOLAR = {
    "A) Çok kısa iş": {"adet": 50, "sure": [(1, (1, 3))],
                       "gelis": (0, 110), "oncelik": [10, 20, 30, 40]},
    "B) Çok uzun iş": {"adet": 50, "sure": [(1, (8, 15))],
                       "gelis": (0, 600), "oncelik": [10, 20, 30, 40]},
    "C) Karışık":     {"adet": 50, "sure": [(70, (1, 4)), (30, (5, 15))],
                       "gelis": (0, 260), "oncelik": [10, 20, 30, 40]},
}


def gorev_uret(senaryo, tohum):
    """
    Senaryoya göre rastgele iş listesi üretir.
    Aynı tohum (seed) = aynı liste, yani sonuçlar tekrarlanabilir.
    """
    rastgele = random.Random(tohum)
    gorevler = []
    for no in range(1, senaryo["adet"] + 1):
        agirliklar = [a for a, _ in senaryo["sure"]]
        _, aralik = rastgele.choices(senaryo["sure"], weights=agirliklar)[0]
        gorevler.append({
            "ad": f"G{no:02d}",
            "gelis": rastgele.randint(*senaryo["gelis"]),
            "sure": rastgele.randint(*aralik),
            "oncelik": rastgele.choices([1, 2, 3, 4], weights=senaryo["oncelik"])[0],
        })
    return gorevler


def sonuc_olustur(isim, gorevler, cizelge, gecis_maliyeti=GECIS_MALIYETI):
    """Çizelgeden tüm ölçütleri hesaplar."""
    # Çizelge zaman sırasında olduğu için son yazılan değer görevin bitiş zamanıdır
    bitis = {}
    for ad, bas, son in cizelge:
        bitis[ad] = son

    bekleme = {g["ad"]: bitis[g["ad"]] - g["gelis"] - g["sure"] for g in gorevler}
    ortalama = sum(bekleme.values()) / len(bekleme)

    # Kritik görevler (öncelik 1) için ortalama bekleme. Fren senaryosunda = Fren.
    kritikler = [bekleme[g["ad"]] for g in gorevler if g["oncelik"] == 1]
    kritik_bekleme = sum(kritikler) / len(kritikler) if kritikler else None

    # Bağlam değiştirme: işlemci bir görevden BAŞKA bir göreve geçtiğinde sayılır
    gecis = sum(1 for onceki, simdiki in zip(cizelge, cizelge[1:]) if onceki[0] != simdiki[0])
    toplam_sure = max(bitis.values()) + gecis * gecis_maliyeti

    # Verimlilik: süre / (süre + bekleme). 1'e yakın = az bekledi.
    verimlilik = sum(g["sure"] / (g["sure"] + bekleme[g["ad"]]) for g in gorevler) / len(gorevler)

    # Tepki süresi: göreve ilk kez sıra gelene kadar geçen süre (ilk çalışma - geliş)
    ilk_calisma = {}
    for ad, bas, son in cizelge:
        ilk_calisma.setdefault(ad, bas)
    tepki = sum(ilk_calisma[g["ad"]] - g["gelis"] for g in gorevler) / len(gorevler)

    return {
        "isim": isim, "cizelge": cizelge, "bekleme": bekleme,
        "ortalama": ortalama,
        "tepki": tepki,
        "kritik_bekleme": kritik_bekleme,
        "en_uzun_bekleme": max(bekleme.values()),    # açlığı gösterir
        "gecis_sayisi": gecis,
        "toplam_sure": toplam_sure,
        "verimlilik": verimlilik,
    }


# 1) Geliş sırası (FCFS / FIFO): ilk gelen ilk çalışır, kimse kesilmez
def geldigi_sirayla(gorevler):
    cizelge = []
    t = 0
    for g in sorted(gorevler, key=lambda x: x["gelis"]):
        t = max(t, g["gelis"])              # görev henüz gelmediyse bekle
        cizelge.append((g["ad"], t, t + g["sure"]))
        t += g["sure"]
    return sonuc_olustur("Geliş sırası (FCFS)", gorevler, cizelge)


# 2) En kısa iş önce (SJF): işlemci boşalınca en kısa süreli görev seçilir, kesilmez
def en_kisa_is_once(gorevler):
    bekleyenler = list(gorevler)
    cizelge = []
    t = 0
    while bekleyenler:
        hazir = [g for g in bekleyenler if g["gelis"] <= t]   # şu an gelmiş olanlar
        if not hazir:
            t = min(g["gelis"] for g in bekleyenler)          # kimse yok, ilk gelene atla
            continue
        secilen = min(hazir, key=lambda g: (g["sure"], g["gelis"]))
        cizelge.append((secilen["ad"], t, t + secilen["sure"]))
        t += secilen["sure"]
        bekleyenler.remove(secilen)
    return sonuc_olustur("En kısa iş önce (SJF)", gorevler, cizelge)


# 3) Döngüsel sıralama (Round Robin): herkes sırayla en fazla `kuantum` ms çalışır
def dongusel_siralama(gorevler, kuantum, yeni_gelen_once=True):
    """
    yeni_gelen_once=True : aynı anda gelen görev ile süresi dolan görev varsa
                           yeni gelen kuyruğa ÖNCE girer (en yaygın kural).
    False yaparsan süresi dolan görev önce girer (hocanın kuralı farklıysa).
    """
    gelecekler = sorted(gorevler, key=lambda x: x["gelis"])
    kalan = {g["ad"]: g["sure"] for g in gorevler}
    kuyruk = deque()
    cizelge = []
    t = 0
    i = 0            # gelecekler listesinde sıradaki görev
    bitenler = 0

    while bitenler < len(gorevler):
        # Gelmiş olan görevleri kuyruğa al
        while i < len(gelecekler) and gelecekler[i]["gelis"] <= t:
            kuyruk.append(gelecekler[i]["ad"])
            i += 1
        if not kuyruk:                       # kuyruk boş, bir sonraki geliş anına atla
            t = gelecekler[i]["gelis"]
            continue

        ad = kuyruk.popleft()
        calisma = min(kuantum, kalan[ad])    # kuantumdan kısa işse işi bitince çıkar
        cizelge.append((ad, t, t + calisma))
        t += calisma
        kalan[ad] -= calisma

        # Çalışırken gelenleri kuyruğa al
        sinir = t if yeni_gelen_once else t - 1
        while i < len(gelecekler) and gelecekler[i]["gelis"] <= sinir:
            kuyruk.append(gelecekler[i]["ad"])
            i += 1

        if kalan[ad] > 0:
            kuyruk.append(ad)                # işi bitmediyse kuyruğun sonuna
        else:
            bitenler += 1

    return sonuc_olustur(f"Döngüsel sıralama (kuantum {kuantum})", gorevler, cizelge)


def _efektif_oncelik(g, t, kalan, aging, aralik, puan):
    """
    Aging: görev bekledikçe önceliği artar (öncelik SAYISI azalır, en az 1).
    Her `aralik` ms beklemede `puan` puan. Böylece önemsiz işler sonsuza dek aç kalmaz.
    """
    if not aging:
        return g["oncelik"]
    bekleme_simdi = t - g["gelis"] - (g["sure"] - kalan[g["ad"]])
    return max(1, g["oncelik"] - puan * (bekleme_simdi // aralik))


# 4) Öncelik zamanlaması (kesmeli): her an kuyruktaki EN ÖNEMLİ görev çalışır
#    aging=True  -> bizim algoritmamız: aging'li öncelik
def oncelik_zamanlamasi(gorevler, aging=False, aralik=AGING_ARALIK, puan=AGING_PUAN):
    kalan = {g["ad"]: g["sure"] for g in gorevler}
    cizelge = []
    t = 0
    while any(k > 0 for k in kalan.values()):
        hazir = [g for g in gorevler if g["gelis"] <= t and kalan[g["ad"]] > 0]
        if not hazir:
            t += 1
            continue
        # Küçük öncelik sayısı = daha önemli. Eşitse önce gelen.
        secilen = min(hazir, key=lambda g: (_efektif_oncelik(g, t, kalan, aging, aralik, puan),
                                            g["gelis"]))
        ad = secilen["ad"]
        # Her ms'de kontrol ediyoruz: daha önemli biri gelirse çalışan otomatik kesilir
        if cizelge and cizelge[-1][0] == ad and cizelge[-1][2] == t:
            cizelge[-1] = (ad, cizelge[-1][1], t + 1)   # aynı görev devam ediyor
        else:
            cizelge.append((ad, t, t + 1))
        kalan[ad] -= 1
        t += 1
    if aging:
        isim = f"Aging'li öncelik (her {aralik} ms'de -{puan})"
    else:
        isim = "Öncelik zamanlaması (kesmeli)"
    return sonuc_olustur(isim, gorevler, cizelge)


def hepsini_calistir(gorevler=GOREVLER):
    """Altı varyantı çalıştırır, (kısa_ad, sonuç) listesi döndürür."""
    return [
        ("fcfs",          geldigi_sirayla(gorevler)),
        ("sjf",           en_kisa_is_once(gorevler)),
        ("rr_k3",         dongusel_siralama(gorevler, kuantum=3)),
        ("rr_k2",         dongusel_siralama(gorevler, kuantum=2)),
        ("oncelik",       oncelik_zamanlamasi(gorevler)),
        ("oncelik_aging", oncelik_zamanlamasi(gorevler, aging=True)),
    ]


KISA_ISIM = {
    "fcfs": "Geliş sırası", "sjf": "En kısa iş önce",
    "rr_k3": "Döngüsel (k=3)", "rr_k2": "Döngüsel (k=2)",
    "oncelik": "Öncelik", "oncelik_aging": "Aging'li öncelik",
}

METRIKLER = ["ortalama", "kritik_bekleme", "en_uzun_bekleme", "tepki",
             "gecis_sayisi", "toplam_sure", "verimlilik"]


def senaryo_karsilastir(senaryo, tekrar=20):
    """
    Senaryodan `tekrar` kez rastgele iş listesi üretir, her algoritmayı çalıştırır
    ve ölçütlerin ORTALAMASINI döndürür (tek şanslı/şanssız listeye bağlı kalmasın diye).
    """
    kayitlar = {}
    for tohum in range(tekrar):
        for kisa, s in hepsini_calistir(gorev_uret(senaryo, tohum)):
            kayit = kayitlar.setdefault(kisa, {"isim": s["isim"],
                                               "degerler": {m: [] for m in METRIKLER}})
            for m in METRIKLER:
                if s[m] is not None:
                    kayit["degerler"][m].append(s[m])

    sonuc = {}
    for kisa, kayit in kayitlar.items():
        sonuc[kisa] = {"isim": kayit["isim"]}
        for m in METRIKLER:
            v = kayit["degerler"][m]
            sonuc[kisa][m] = sum(v) / len(v)
    return sonuc


def aging_denemesi(senaryo, araliklar=(5, 10, 20, 40), tekrar=20):
    """
    Aging aralığını değiştirip sonuçlara bakar.
    Küçük aralık = adil ama kritik işi korumaz, büyük aralık = kritik iş korunur
    ama önemsiz işler daha uzun bekler. Hoca: "denedim, böyle çıktı" demek yeterli.
    """
    sonuc = []
    for aralik in araliklar:
        kritik, en_uzun, ortalama = [], [], []
        for tohum in range(tekrar):
            s = oncelik_zamanlamasi(gorev_uret(senaryo, tohum), aging=True, aralik=aralik)
            ortalama.append(s["ortalama"])
            en_uzun.append(s["en_uzun_bekleme"])
            if s["kritik_bekleme"] is not None:
                kritik.append(s["kritik_bekleme"])
        sonuc.append({"aralik": aralik,
                      "ortalama": sum(ortalama) / len(ortalama),
                      "kritik_bekleme": sum(kritik) / len(kritik),
                      "en_uzun_bekleme": sum(en_uzun) / len(en_uzun)})
    return sonuc
