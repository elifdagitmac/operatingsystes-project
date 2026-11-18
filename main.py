"""
Ana program: 5 algoritma varyantını çalıştırır, karşılaştırma tablosunu yazar,
Gantt şemalarını 'ciktilar' klasörüne PNG olarak kaydeder.

Çalıştırma:  python main.py
"""
import os

from algoritmalar import GOREVLER, hepsini_calistir
from gantt import gantt_metin, gantt_ciz, gantt_hepsi

CIKTI_KLASORU = "ciktilar"


def tablo_yazdir(sonuclar):
    print("\nKARŞILAŞTIRMA TABLOSU (süre: ms)")
    print("-" * 66)
    print(f"{'Algoritma':<34}{'Fren bekleme':>14}{'Ortalama bekleme':>18}")
    print("-" * 66)
    for _, s in sonuclar:
        print(f"{s['isim']:<34}{s['bekleme']['Fren']:>14}{s['ortalama']:>18.2f}")
    print("-" * 66)


def main():
    sonuclar = hepsini_calistir()
    gorev_sirasi = [g["ad"] for g in GOREVLER]

    # 1) Her algoritmanın çizelgesi ve bekleme süreleri
    for _, s in sonuclar:
        gantt_metin(s)
        bekleme_yazisi = ", ".join(f"{ad}: {b}" for ad, b in s["bekleme"].items())
        print(f"  Bekleme -> {bekleme_yazisi} | Ortalama: {s['ortalama']:.2f}\n")

    # 2) Karşılaştırma tablosu
    tablo_yazdir(sonuclar)

    # 3) Gantt resimleri (matplotlib yoksa atlanır)
    try:
        os.makedirs(CIKTI_KLASORU, exist_ok=True)
        for kisa_ad, s in sonuclar:
            gantt_ciz(s, f"{CIKTI_KLASORU}/gantt_{kisa_ad}.png", gorev_sirasi)
        gantt_hepsi([s for _, s in sonuclar], f"{CIKTI_KLASORU}/gantt_hepsi.png", gorev_sirasi)
        print(f"\nGantt şemaları '{CIKTI_KLASORU}' klasörüne kaydedildi.")
    except ImportError:
        print("\nmatplotlib kurulu değil, resimler atlandı. Kurmak için: pip install matplotlib")


if __name__ == "__main__":
    main()
