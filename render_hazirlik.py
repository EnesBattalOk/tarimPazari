import os

dosya_adi = "app.py"

# Sitenin adres çubuğuna /hazirla yazınca çalışacak kod
veri_hazirlama_kodu = """

# --- RENDER ICIN VERITABANI DOLDURMA ---
@app.route('/hazirla')
def veritabani_hazirla():
    try:
        from models import Category, Product
        # 1. Tablolari olustur
        with app.app_context():
            db.create_all()
        
        # 2. Kategorileri Ekle (Slug alani kaldirildi cunku modelde yok)
        kategoriler = [
            {"name": "Meyve", "icon_class": "fa-apple-alt"},
            {"name": "Sebze", "icon_class": "fa-carrot"},
            {"name": "Tahıl & Bakliyat", "icon_class": "fa-wheat"},
            {"name": "Süt & Kahvaltılık", "icon_class": "fa-cheese"},
            {"name": "Organik Ürünler", "icon_class": "fa-leaf"}
        ]
        
        eklenen_kat = 0
        with app.app_context():
            for k in kategoriler:
                # Isme gore kontrol et, varsa ekleme
                if not Category.query.filter_by(name=k['name']).first():
                    yeni = Category(name=k['name'], icon_class=k['icon_class'])
                    db.session.add(yeni)
                    eklenen_kat += 1
            db.session.commit()
        
        return f'''
        <div style="font-family: sans-serif; padding: 50px; text-align: center; background: #d4edda; color: #155724;">
            <h1>✅ Dükkan Doldu!</h1>
            <p>Veritabanı başarıyla oluşturuldu.</p>
            <p><strong>{eklenen_kat}</strong> adet kategori eklendi.</p>
            <br>
            <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Alışverişe Başla</a>
        </div>
        '''
    except Exception as e:
        return f"<h1>Hata Oluştu:</h1><pre>{e}</pre>"
# -----------------------------------------------
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    # Eski kod varsa onu bulup temizleyelim ve yenisini ekleyelim
    if "@app.route('/hazirla')" in icerik:
        print("⚠️ Eski kod bulundu, temizleniyor...")
        
        # Eski kodun başladığı yeri bul
        baslangic_index = icerik.find("@app.route('/hazirla')")
        
        # Dosyanın sadece o kısımdan öncesini al (Eski kodu kesip atıyoruz)
        temiz_icerik = icerik[:baslangic_index]
        
        # Yeni kodu ekle
        son_icerik = temiz_icerik + veri_hazirlama_kodu
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(son_icerik)
            
        print("✅ app.py temizlendi ve güncellendi! Hatalı 'slug' kodları silindi.")
        
    else:
        # Kod hiç yoksa direkt ekle
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(veri_hazirlama_kodu)
        print("✅ app.py güncellendi! Artık site adresinin sonuna '/hazirla' yazarak verileri yükleyebilirsin.")

else:
    print("❌ app.py dosyası bulunamadı!")