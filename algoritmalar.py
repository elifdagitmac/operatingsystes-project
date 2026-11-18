"""
İşlemci zamanlama algoritmaları - Araba fren sistemi senaryosu.

Süre birimi: ms (tam sayı).
Öncelik: küçük sayı = daha önemli (1 en önemli).

Her algoritma bir "zaman çizelgesi" (Gantt için) üretir:
    [("Müzik", 0, 3), ("Klima", 3, 6), ...]  -> (görev, başlangıç, bitiş)
Bekleme süreleri bu çizelgeden TEK bir formülle hesaplanır:
    bekleme = bitiş - geliş - süre
"""
from collections import deque

# Ortak görev listesi (geliş zamanı, çalışma süresi, öncelik)
GOREVLER = [
    {"ad": "Müzik", "gelis": 0, "sure": 6, "oncelik": 4},
    {"ad": "Klima", "gelis": 1, "sure": 3, "oncelik": 3},
    {"ad": "Motor", "gelis": 2, "sure": 4, "oncelik": 2},
    {"ad": "Fren",  "gelis": 3, "sure": 2, "oncelik": 1},
]


def sonuc_olustur(isim, gorevler, cizelge):
    """Çizelgeden bekleme sürelerini ve ortalamayı hesaplar."""
    bekleme = {}
    for g in gorevler:
        # Görevin en son çalıştığı an = bitiş zamanı
        bitis = max(son for ad, bas, son in cizelge if ad == g["ad"])
        bekleme[g["ad"]] = bitis - g["gelis"] - g["sure"]
    ortalama = sum(bekleme.values()) / len(bekleme)
    return {"isim": isim, "cizelge": cizelge, "bekleme": bekleme, "ortalama": ortalama}


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

    while bitenler