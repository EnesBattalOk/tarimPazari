import os

dosya_adi = "app.py"

# Sitenin adres çubuğuna /hazirla yazınca çalışacak kod
veri_hazirlama_kodu = """

# --- VERITABANI DOLDURMA ROTASI (VERCEL ICIN) ---
@app.route('/hazirla')
def veritabani_hazirla():
    try:
        from models import Category, Product
        from werkzeug.security import generate_password_hash
        
        # 1. Tablolari Garantile
        db.create_all()
        
        # 2. Kategorileri Ekle
        kategoriler = [
            {"name": "Meyve", "slug": "meyve", "icon_class": "fa-apple-alt"},
            {"name": "Sebze", "slug": "sebze", "icon_class": "fa-carrot"},
            {"name": "Tahıl & Bakliyat", "slug": "tahil", "icon_class": "fa-wheat"},
            {"name": "Süt & Kahvaltılık", "slug": "sut", "icon_class": "fa-cheese"},
            {"name": "Organik Ürünler", "slug": "organik", "icon_class": "fa-leaf"}
        ]
        
        eklenen_kat = 0
        for k in kategoriler:
            # Varsa ekleme, yoksa ekle
            if not Category.query.filter_by(slug=k['slug']).first():
                yeni = Category(name=k['name'], slug=k['slug'], icon_class=k['icon_class'])
                db.session.add(yeni)
                eklenen_kat += 1
        
        db.session.commit()
        
        return f'''
        <div style="font-family: sans-serif; padding: 50px; text-align: center; background: #d4edda; color: #155724;">
            <h1>✅ İşlem Tamam!</h1>
            <p>Veritabanı başarıyla oluşturuldu.</p>
            <p><strong>{eklenen_kat}</strong> adet kategori eklendi.</p>
            <br>
            <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Siteye Git</a>
        </div>
        '''
    except Exception as e:
        return f"<h1>Hata Oluştu:</h1><pre>{e}</pre>"
# -----------------------------------------------
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    # Daha önce eklemediysek ekleyelim
    if "/hazirla" not in icerik:
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(veri_hazirlama_kodu)
        print("✅ app.py güncellendi! Artık site adresinin sonuna '/hazirla' yazarak verileri yükleyebilirsin.")
    else:
        print("⚠️ Bu kod zaten ekli.")

else:
    print("❌ app.py dosyası bulunamadı!")