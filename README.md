# İşlemci Zamanlama Algoritmaları: Araba Fren Sistemi Senaryosu

İşletim Sistemleri dersi projesi. Aynı görev listesi üzerinde dört zamanlama
algoritması karşılaştırılır ve fren görevi için en uygun algoritma seçilir.

## Senaryo

Arabanın bilgisayarı tek işlemciyle şu görevleri yönetiyor (süre birimi: ms):

| Görev | Geliş | Süre | Öncelik (1 = en önemli) |
|---|---|---|---|
| Müzik | 0 | 6 | 4 |
| Klima | 1 | 3 | 3 |
| Motor | 2 | 4 | 2 |
| Fren | 3 | 2 | 1 |

## Algoritmalar

1. Geliş sırası (FCFS)
2. En kısa iş önce (SJF)
3. Döngüsel sıralama (Round Robin), kuantum 3 ve kuantum 2
4. Öncelik zamanlaması (kesmeli)

## Ölçütler

- **Fren bekleme süresi:** güvenlik ölçütü (kritik görev geç kalmamalı)
- **Ortalama bekleme süresi:** genel performans
- Bekleme = bitiş − geliş − çalışma süresi

## Çalıştırma

```
pip install -r requirements.txt
python main.py                 # tablo + Gantt şemaları (ciktilar/ klasörü)
python -m unittest -v          # elle hesaplanan sonuçlarla test
```

## Dosyalar

- `algoritmalar.py`: algoritmalar ve görev listesi
- `gantt.py`: zaman çizelgesi (Gantt) çizimi
- `main.py`: ana program, karşılaştırma tablosu
- `test_algoritmalar.py`: elle bulunan sayılarla doğrulama

## Varsayım

Döngüsel sıralamada aynı anda gelen görev ile süresi dolan görev varsa
**yeni gelen görev kuyruğa önce girer**. Farklı kural için
`dongusel_siralama(..., yeni_gelen_once=False)` kullanılır.