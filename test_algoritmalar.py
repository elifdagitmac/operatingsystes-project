"""
Testler: kodun sonuçları ELLE hesaplanan sayılarla aynı mı?
Çalıştırma:  python -m unittest -v
"""
import unittest

from algoritmalar import (GOREVLER, geldigi_sirayla, en_kisa_is_once,
                          dongusel_siralama, oncelik_zamanlamasi)


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


if __name__ == "__main__":
    unittest.main()
