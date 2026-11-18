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
