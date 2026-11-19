# İşlemci Zamanlama Algoritmaları: Simülasyon ve Karşılaştırma

İşletim Sistemleri dersi projesi. Süreç yönetimi (CPU zamanlama) alanında bilinen
algoritmalar ile kendi tasarladığımız algoritma, aynı koşullarda farklı
senaryolarla karşılaştırılır.

Bu bir **simülasyon**: işler gerçekten çalıştırılmaz, "şu kadar ms geçti, iş
tamamlandı" kabul edilir. Süre birimi ms (tam sayı).

## Algoritmalar

1. Geliş sırası (FCFS)
2. En kısa iş önce (SJF)
3. Döngüsel sıralama (Round Robin), kuantum 3 ve kuantum 2
4. Öncelik zamanlaması (kesmeli)
5. **Aging'li öncelik (bizim algoritmamız):** öncelik zamanlamasına, bekleyen işin
   önceliğini zamanla artıran bir kural ekler. Böylece önemsiz işler sonsuza dek
   aç kalmaz.

## Senaryolar

| Senaryo | İş sayısı | Süre | Not |
|---|---|---|---|
| A) Çok kısa iş | 50 | 1-3 ms | rastgele |
| B) Çok uzun iş | 50 | 8-15 ms | rastgele |
| C) Karışık | 50 | %70 1-4 ms, %30 5-15 ms | rastgele |
| D) Fren senaryosu | 4 | elle yazılmış | araba bilgisayarı: müzik, klima, motor, fren |

- İşlerin geliş zamanı, süresi ve önceliği rastgele üretilir (`gorev_uret`).
- Öncelik dağılımı gerçekçi: çoğu iş düşük öncelikli (%10/%20/%30/%40, öncelik 1-4).
- Aynı tohum (seed) aynı listeyi verir, yani sonuçlar tekrarlanabilir.
- A, B, C senaryoları 20 farklı rastgele listeyle denenir, **ortalama** alınır.

## Ölçütler

- **Ortalama bekleme:** bekleme = bitiş − geliş − çalışma süresi
- **Kritik bekleme:** öncelik 1 olan işlerin ortalama beklemesi (fren senaryosunda Fren)
- **En uzun bekleme:** açlık (starvation) göstergesi
- **Tepki süresi:** işe ilk kez sıra gelene kadar geçen süre
- **Geçiş sayısı ve toplam süre:** bağlam değiştirme maliyeti dahil
  (toplam = bitiş + geçiş sayısı × 1 ms)
- **Verimlilik:** süre / (süre + bekleme), 1'e yakın = az bekledi

## Çalıştırma

```
pip install -r requirements.txt
python main.py                 # tablolar + grafikler (ciktilar/ klasörü)
python -m unittest -v          # testler
```

## Dosyalar

- `algoritmalar.py`: algoritmalar, rastgele iş üretici, ölçütler
- `gantt.py`: zaman çizelgesi (Gantt) ve karşılaştırma grafikleri
- `main.py`: ana program
- `test_algoritmalar.py`: testler (fren senaryosu elle hesaplanan sayılarla doğrulanır)

## Varsayımlar ve sınırlar

- Döngüsel sıralamada aynı anda gelen görev ile süresi dolan görev varsa **yeni gelen
  önce** kuyruğa girer. Farklı kural için `dongusel_siralama(..., yeni_gelen_once=False)`.
- Bağlam değiştirme maliyeti basitleştirilmiştir: toplam süreye `geçiş sayısı × 1 ms`
  eklenir, işler tek tek geciktirilmez (bekleme süreleri bundan etkilenmez).
- Aging ayarları (`AGING_ARALIK = 20`, `AGING_PUAN = 1`) deneyle seçildi (main.py'de
  "Aging ayar denemesi"): 5 ms çok agresif olup algoritmayı geliş sırasına
  yaklaştırıyor.
- IO bekleme durumu (waiting) ve süreç durumları (new, ready, running, terminated)
  henüz modellenmedi.
