"""
Gantt (zaman çizelgesi) çizimi.
- gantt_metin(): terminalde yazı olarak gösterir (kütüphane gerekmez)
- gantt_ciz():   matplotlib ile PNG resmi üretir (slayta koymak için)
"""

RENKLER = {
    "Müzik": "#9aa5b1",   # gri: önemsiz
    "Klima": "#4cc3d9",
    "Motor": "#f2a33a",
    "Fren":  "#e5484d",   # kırmızı: kritik
}


def gantt_metin(sonuc):
    """Her çalışma aralığını bir satırda gösterir. Her blok 1 ms."""
    print(sonuc["isim"])
    for ad, bas, son in sonuc["cizelge"]:
        print(f"  {ad:<6} {bas:>2} → {son:<2} {'█' * (son - bas)}")


def _ciz(ax, sonuc, gorev_sirasi):
    for ad, bas, son in sonuc["cizelge"]:
        y = gorev_sirasi.index(ad)
        ax.barh(y, son - bas, left=bas, height=0.6,
                color=RENKLER.get(ad, "#888"), edgecolor="white")
        ax.text((bas + son) / 2, y, f"{bas}-{son}", ha="center", va="center", fontsize=8)
    bitis = max(son for _, _, son in sonuc["cizelge"])
    ax.set_yticks(range(len(gorev_sirasi)))
    ax.set_yticklabels(gorev_sirasi)
    ax.set_xticks(range(0, bitis + 1))
    ax.set_xlim(0, bitis)
    ax.invert_yaxis()
    ax.set_xlabel("Zaman (ms)")
    ax.set_title(sonuc["isim"], fontsize=10, loc="left")
    ax.grid(axis="x", alpha=0.3)


def gantt_ciz(sonuc, dosya, gorev_sirasi):
    """Tek bir algoritmanın şemasını PNG olarak kaydeder."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 3))
    _ciz(ax, sonuc, gorev_sirasi)
    fig.tight_layout()
    fig.savefig(dosya, dpi=150)
    plt.close(fig)


def gantt_hepsi(sonuclar, dosya, gorev_sirasi):
    """Tüm algoritmaları alt alta tek resimde gösterir (karşılaştırma slaydı için)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, eksenler = plt.subplots(len(sonuclar), 1, figsize=(9, 2.6 * len(sonuclar)),
                                 sharex=True)
    for ax, sonuc in zip(eksenler, sonuclar):
        _ciz(ax, sonuc, gorev_sirasi)
        ax.set_xlabel("")
    eksenler[-1].set_xlabel("Zaman (ms)")
    fig.tight_layout()
    fig.savefig(dosya, dpi=150)
    plt.close(fig)


ALGO_RENKLERI = {
    "fcfs": "#9aa5b1", "sjf": "#4cc3d9", "rr_k3": "#f2a33a",
    "rr_k2": "#f7c873", "oncelik": "#e5484d", "oncelik_aging": "#7b61ff",
}


def karsilastirma_grafigi(senaryo_sonuclari, metrik, baslik, dosya, kisa_isim):
    """
    Senaryoları yan yana, algoritmaları çubuk olarak gösterir (küçük = iyi).
    senaryo_sonuclari: {"A) ...": {"fcfs": {...metrikler...}, ...}, ...}
    ★ = o senaryoda en iyi (en düşük) algoritma.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, eksenler = plt.subplots(1, len(senaryo_sonuclari), figsize=(4.2 * len(senaryo_sonuclari), 4),
                                 sharey=False)
    for ax, (senaryo_ad, sonuclar) in zip(eksenler, senaryo_sonuclari.items()):
        anahtarlar = list(sonuclar.keys())
        degerler = [sonuclar[k][metrik] for k in anahtarlar]
        en_iyi = min(degerler)
        cubuklar = ax.bar(range(len(anahtarlar)), degerler,
                          color=[ALGO_RENKLERI.get(k, "#888") for k in anahtarlar])
        for cubuk, d in zip(cubuklar, degerler):
            etiket = f"{d:.1f}" + (" ★" if d == en_iyi else "")
            ax.text(cubuk.get_x() + cubuk.get_width() / 2, d, etiket,
                    ha="center", va="bottom", fontsize=8)
        ax.set_xticks(range(len(anahtarlar)))
        ax.set_xticklabels([kisa_isim[k] for k in anahtarlar], rotation=35, ha="right", fontsize=8)
        ax.set_title(senaryo_ad, fontsize=10)
        ax.margins(y=0.15)
        ax.grid(axis="y", alpha=0.3)
    eksenler[0].set_ylabel("ms")
    fig.suptitle(baslik, fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=150)
    plt.close(fig)
