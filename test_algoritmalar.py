"""
Testler: kodun sonuçları ELLE hesaplanan sayılarla aynı mı?
Çalıştırma:  python -m unittest -v
"""
import unittest

from algoritmalar import (GOREVLER, SENARYOLAR, geldigi_sirayla, en_kisa_is_once,
                          dongusel_siralama, oncelik_zamanlamasi, gorev_uret,
                          senaryo_karsilastir)


class ElleHesapTestleri(unittest.TestCase):

    def kontrol(self, sonuc, bekleme, ortalama):
        self.assertEqual(sonuc["bekleme"], bekleme)
        self.assertAlmostEqual(sonuc["ortalama"], ortalama)

    def test_geldigi_sirayla(self):
        s = geldigi_sirayla(GOREVLER)
        self.assertEqual(s["cizelge"], [("Müzik", 0, 6), ("Klima", 6, 9),
                                        ("Motor", 9, 13), ("Fren", 13, 15)])
        self.kontrol(s, {"Müzik": 0, "Klima": 5, "Motor": 7, "Fren": 10}, 5.5)

    def test_en_kisa_is_once(self):
        s = en_kisa_is_once(GOREVLER)
        self.assertEqual(s["cizelge"], [("Müzik", 0, 6), ("Fren", 6, 8),
                                        ("Klima", 8, 11), ("Motor", 11, 15)])
        self.kontrol(s, {"Müzik": 0, "Klima": 7, "Motor": 9, "Fren": 3}, 4.75)

    def test_dongusel_kuantum_3(self):
        s = dongusel_siralama(GOREVLER, kuantum=3)
        self.assertEqual(s["cizelge"], [("Müzik", 0, 3), ("Klima", 3, 6), ("Motor", 6, 9),
                                        ("Fren", 9, 11), ("Müzik", 11, 14), ("Motor", 14, 15)])
        self.kontrol(s, {"Müzik": 8, "Klima": 2, "Motor": 9, "Fren": 6}, 6.25)

    def test_dongusel_kuantum_2(self):
        s = dongusel_siralama(GOREVLER, kuantum=2)
        self.assertEqual(s["cizelge"], [("Müzik", 0, 2), ("Klima", 2, 4), ("Motor", 4, 6),
                                        ("Müzik", 6, 8), ("Fren", 8, 10), ("Klima", 10, 11),
                                        ("Motor", 11, 13), ("Müzik", 13, 15)])
        self.kontrol(s, {"Müzik": 9, "Klima": 7, "Motor": 7, "Fren": 5}, 7.0)

    def test_oncelik(self):
        s = oncelik_zamanlamasi(GOREVLER)
        self.assertEqual(s["cizelge"], [("Müzik", 0, 1), ("Klima", 1, 2), ("Motor", 2, 3),
                                        ("Fren", 3, 5), ("Motor", 5, 8), ("Klima", 8, 10),
                                        ("Müzik", 10, 15)])
        self.kontrol(s, {"Müzik": 9, "Klima": 6, "Motor": 2, "Fren": 0}, 4.25)

    # --- Yeni ölçütler (fren senaryosu, elle kontrol edilebilir) ---
    def test_gecis_ve_toplam_sure(self):
        # Geçiş sayısı = işlemcinin başka göreve geçtiği sayı, toplam = bitiş + geçiş x 1 ms
        self.assertEqual(geldigi_sirayla(GOREVLER)["gecis_sayisi"], 3)
        self.assertEqual(geldigi_sirayla(GOREVLER)["toplam_sure"], 18)
        self.assertEqual(dongusel_siralama(GOREVLER, 3)["gecis_sayisi"], 5)
        self.assertEqual(oncelik_zamanlamasi(GOREVLER)["gecis_sayisi"], 6)
        self.assertEqual(oncelik_zamanlamasi(GOREVLER)["toplam_sure"], 21)

    def test_kritik_bekleme_ve_tepki(self):
        # Fren senaryosunda tek kritik (öncelik 1) görev Fren'dir
        for s in (geldigi_sirayla(GOREVLER), en_kisa_is_once(GOREVLER),
                  oncelik_zamanlamasi(GOREVLER)):
            self.assertEqual(s["kritik_bekleme"], s["bekleme"]["Fren"])
        # Öncelikli algoritmada herkes gelir gelmez çalışır -> tepki 0
        self.assertEqual(oncelik_zamanlamasi(GOREVLER)["tepki"], 0)
        # Kesilmeyen algoritmada tepki = bekleme
        self.assertAlmostEqual(geldigi_sirayla(GOREVLER)["tepki"], 5.5)

    # --- Rastgele iş üretici ---
    def test_uretici_tekrarlanabilir(self):
        a = gorev_uret(SENARYOLAR["C) Karışık"], tohum=7)
        b = gorev_uret(SENARYOLAR["C) Karışık"], tohum=7)
        c = gorev_uret(SENARYOLAR["C) Karışık"], tohum=8)
        self.assertEqual(a, b)          # aynı tohum = aynı liste
        self.assertNotEqual(a, c)       # farklı tohum = farklı liste

    def test_uretici_sinirlar(self):
        for ad, sen in SENARYOLAR.items():
            isler = gorev_uret(sen, tohum=1)
            self.assertEqual(len(isler), 50)
            self.assertEqual(len({g["ad"] for g in isler}), 50)      # adlar benzersiz
            for g in isler:
                self.assertIn(g["oncelik"], (1, 2, 3, 4))
                self.assertGreaterEqual(g["gelis"], sen["gelis"][0])
                self.assertLessEqual(g["gelis"], sen["gelis"][1])

    # --- Aging (kendi algoritmamız) ---
    def test_aging_cok_buyuk_aralikta_normal_oncelige_esit(self):
        isler = gorev_uret(SENARYOLAR["C) Karışık"], tohum=3)
        normal = oncelik_zamanlamasi(isler)
        aging = oncelik_zamanlamasi(isler, aging=True, aralik=10 ** 9)
        self.assertEqual(normal["cizelge"], aging["cizelge"])

    def test_aging_acligi_azaltir_ama_kritik_isi_fcfs_den_iyi_korur(self):
        s = senaryo_karsilastir(SENARYOLAR["C) Karışık"], tekrar=10)
        self.assertLess(s["oncelik_aging"]["en_uzun_bekleme"], s["oncelik"]["en_uzun_bekleme"])
        self.assertLess(s["oncelik_aging"]["kritik_bekleme"], s["fcfs"]["kritik_bekleme"])


if __name__ == "__main__":
    unittest.main()
