import os

dosya_adi = "app.py"

# Hata veren o meşhur satır
eski_kod = "return dict(cart_info=get_cart_total(), categories=Category.query.all())"

# Onun yerine koyacağımız "Zırhlı" kod
yeni_kod = """
    # --- VERCEL KURTARMA MODU ---
    try:
        # Kategorileri çekmeyi dene
        cats = Category.query.all()
    except Exception:
        # Eğer tablo yoksa hata verme, hemen oluştur!
        try:
            with app.app_context():
                db.create_all()
                # Opsiyonel: Boş kalmasın diye varsayılan kategori ekle
                if not Category.query.first():
                    ornek = Category(name="Genel", slug="genel", icon_class="fa-leaf")
                    db.session.add(ornek)
                    db.session.commit()
            cats = Category.query.all()
        except:
            cats = [] # Yine de olmazsa boş liste dön ama ÇÖKME
            
    return dict(cart_info=get_cart_total(), categories=cats)
    # ---------------------------
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    if eski_kod in icerik:
        yeni_icerik = icerik.replace(eski_kod, yeni_kod)
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)
        print("✅ app.py başarıyla zırhlandı! Artık 'Tablo Yok' hatasında çökmeyecek, tabloyu kendi oluşturacak.")
    else:
        # Eğer kod tam eşleşmezse, belki boşluklar farklıdır, manuel uyarısı verelim
        print("⚠️ Hata: Aranan kod satırı tam bulunamadı. Kodunda değişiklik yapmış olabilir misin?")
        print("Lütfen app.py içinde 'inject_cart' fonksiyonunu bul ve içindeki return satırını kontrol et.")

else:
    print("❌ app.py bulunamadı!")