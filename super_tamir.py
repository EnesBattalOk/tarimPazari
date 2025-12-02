import os

dosya_adi = "app.py"

# 1. Kodun en altına eklenecek "Kurtarıcı Fonksiyon"
kurtarici_fonksiyon = """

# --- VERCEL ICIN OZEL KURTARICI FONKSIYON ---
def safe_get_categories():
    try:
        # Kategorileri çekmeyi dene
        return Category.query.all()
    except Exception:
        # Hata verirse (tablo yoksa), veritabanini olustur
        print("⚠️ Tablo bulunamadi, yeniden olusturuluyor...")
        with app.app_context():
            db.create_all()
            # Bos kalmasin diye ornek kategori ekle
            try:
                if not Category.query.first():
                    db.session.add(Category(name="Genel", slug="genel", icon_class="fa-leaf"))
                    db.session.commit()
            except:
                pass
        # Simdi tekrar dene, olmazsa bos liste don
        try:
            return Category.query.all()
        except:
            return []
# -------------------------------------------
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # 2. Önce kurtarıcı fonksiyonu dosyanın sonuna ekleyelim (eğer yoksa)
    if "def safe_get_categories():" not in icerik:
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(kurtarici_fonksiyon)
        print("✅ Kurtarıcı fonksiyon app.py sonuna eklendi.")
    
    # 3. Şimdi hata veren o meşhur satırı bulup değiştirelim
    # Hata veren satır: categories=Category.query.all()
    eski_kod = "categories=Category.query.all()"
    yeni_kod = "categories=safe_get_categories()"
    
    # Dosyayı tekrar oku (son haliyle)
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik_son = f.read()
        
    if eski_kod in icerik_son:
        icerik_duzeltilmis = icerik_son.replace(eski_kod, yeni_kod)
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(icerik_duzeltilmis)
        print("✅ Hatalı satır başarıyla değiştirildi! (Category.query.all -> safe_get_categories)")
    else:
        print("⚠️ Hatalı satır tam bulunamadı. Daha önce düzeltmiş olabilir misin?")
        print("Kontrol et: 'categories=safe_get_categories()' yazıyor mu?")

else:
    print("❌ app.py dosyası bulunamadı!")