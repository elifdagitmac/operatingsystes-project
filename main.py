"""
Ana program:
  1) Fren senaryosu (D): 4 görev, tüm algoritmalar, Gantt şemaları
  2) Rastgele senaryolar (A, B, C): 50 iş x 20 deneme, ölçütlerin ortalaması
  3) Aging ayar denemesi
  4) Grafikleri 'ciktilar' klasörüne PNG olarak kaydeder

Çalıştırma:  python main.py
"""
import os

from algoritmalar import (GOREVLER, SENARYOLAR, KISA_ISIM, hepsini_calistir,
                          senaryo_karsilastir, aging_denemesi)
from gantt import gantt_metin, gantt_ciz, gantt_hepsi, karsilastirma_grafigi

CIKTI_KLASORU = "ciktilar"
TEKRAR = 20          # her senaryo kaç rastgele iş listesiyle denenecek


def fren_senaryosu(gorev_sirasi):
    print("=" * 70)
    print("D) FREN SENARYOSU (4 görev)")
    print("=" * 70)
    sonuclar = hepsini_calistir()
    for _, s in sonuclar:
        gantt_metin(s)
        bekleme_yazisi = ", ".join(f"{ad}: {b}" for ad, b in s["bekleme"].items())
        print(f"  Bekleme -> {bekleme_yazisi} | Ortalama: {s['ortalama']:.2f}\n")

    print("KARŞILAŞTIRMA TABLOSU (süre: ms)")
    print("-" * 78)
    print(f"{'Algoritma':<36}{'Fren bekl.':>11}{'Ort. bekl.':>11}{'Geçiş':>7}{'Toplam':>8}")
    print("-" * 78)
    for _, s in sonuclar:
        print(f"{s['isim']:<36}{s['bekleme']['Fren']:>11}{s['ortalama']:>11.2f}"
              f"{s['gecis_sayisi']:>7}{s['toplam_sure']:>8}")
    print("-" * 78)
    return sonuclar


def senaryo_tablosu(baslik, sonuclar):
    print(f"\n{baslik} ({TEKRAR} rastgele denemenin ortalaması, süre: ms)")
    print("-" * 100)
    print(f"{'Algoritma':<36}{'Ort.bekl.':>10}{'Kritik':>8}{'En uzun':>9}"
          f"{'Tepki':>7}{'Geçiş':>7}{'Toplam':>8}{'Verim.':>8}")
    print("-" * 100)
    for s in sonuclar.values():
        print(f"{s['isim']:<36}{s['ortalama']:>10.2f}{s['kritik_bekleme']:>8.2f}"
              f"{s['en_uzun_bekleme']:>9.1f}{s['tepki']:>7.2f}{s['gecis_sayisi']:>7.1f}"
              f"{s['toplam_sure']:>8.1f}{s['verimlilik']:>8.3f}")
    print("-" * 100)
    # Her ölçütte kazanan (verimlilikte büyük iyi, diğerlerinde küçük iyi)
    etiketler = [("ortalama", "ort. bekleme"), ("kritik_bekleme", "kritik bekleme"),
                 ("en_uzun_bekleme", "en uzun bekleme"), ("tepki", "tepki"),
                 ("toplam_sure", "toplam süre")]
    parcalar = []
    for anahtar, etiket in etiketler:
        kazanan = min(sonuclar, key=lambda k: sonuclar[k][anahtar])
        parcalar.append(f"{etiket}: {KISA_ISIM[kazanan]}")
    kazanan = max(sonuclar, key=lambda k: sonuclar[k]["verimlilik"])
    parcalar.append(f"verimlilik: {KISA_ISIM[kazanan]}")
    print("EN İYİ -> " + " | ".join(parcalar))


def main():
    gorev_sirasi = [g["ad"] for g in GOREVLER]

    # 1) Fren senaryosu
    fren_sonuclari = fren_senaryosu(gorev_sirasi)

    # 2) Rastgele senaryolar
    senaryo_sonuclari = {}
    print("\n" + "=" * 70)
    print("RASTGELE SENARYOLAR (A, B, C)")
    print("=" * 70)
    for ad, senaryo in SENARYOLAR.items():
        senaryo_sonuclari[ad] = senaryo_karsilastir(senaryo, tekrar=TEKRAR)
        senaryo_tablosu(ad, senaryo_sonuclari[ad])

    # 3) Aging ayar denemesi (karışık senaryoda)
    print("\n" + "=" * 70)
    print("AGING AYAR DENEMESİ (C senaryosu): aralık küçüldükçe ne olur?")
    print("=" * 70)
    print(f"{'Aging aralığı':<16}{'Ort. bekleme':>14}{'Kritik bekleme':>16}{'En uzun bekleme':>17}")
    for d in aging_denemesi(SENARYOLAR["C) Karışık"], tekrar=TEKRAR):
        print(f"{str(d['aralik']) + ' ms':<16}{d['ortalama']:>14.2f}"
              f"{d['kritik_bekleme']:>16.2f}{d['en_uzun_bekleme']:>17.1f}")

    # 4) Grafikler (matplotlib yoksa atlanır)
    try:
        os.makedirs(CIKTI_KLASORU, exist_ok=True)
        for kisa_ad, s in fren_sonuclari:
            gantt_ciz(s, f"{CIKTI_KLASORU}/gantt_{kisa_ad}.png", gorev_sirasi)
        gantt_hepsi([s for _, s in fren_sonuclari], f"{CIKTI_KLASORU}/gantt_hepsi.png", gorev_sirasi)

        grafikler = [("ortalama", "Ortalama bekleme süresi (küçük = iyi)", "karsilastirma_ortalama_bekleme"),
                     ("kritik_bekleme", "Kritik (öncelik 1) işlerin bekleme süresi (küçük = iyi)", "karsilastirma_kritik_bekleme"),
                     ("en_uzun_bekleme", "En uzun bekleyen iş (açlık göstergesi, küçük = iyi)", "karsilastirma_en_uzun_bekleme"),
                     ("tepki", "Tepki süresi: ilk çalışmaya kadar (küçük = iyi)", "karsilastirma_tepki")]
        for metrik, baslik, dosya in grafikler:
            karsilastirma_grafigi(senaryo_sonuclari, metrik, baslik,
                                  f"{CIKTI_KLASORU}/{dosya}.png", KISA_ISIM)
        print(f"\nGrafikler '{CIKTI_KLASORU}' klasörüne kaydedildi.")
    except ImportError:
        print("\nmatplotlib kurulu değil, resimler atlandı. Kurmak için: pip install matplotlib")


if __name__ == "__main__":
    main()
