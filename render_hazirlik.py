import os

dosya_adi = "app.py"

# Sitenin adres çubuğuna /hazirla yazınca çalışacak kod
veri_hazirlama_kodu = """

# --- RENDER ICIN VERITABANI DOLDURMA (URUNLER DAHIL) ---
@app.route('/hazirla')
def veritabani_hazirla():
    try:
        from models import Category, Product
        import random
        
        # 1. Tablolari olustur
        with app.app_context():
            db.create_all()
        
        # 2. Kategorileri Ekle
        kategoriler_data = [
            {"name": "Meyve", "icon_class": "fa-apple-alt"},
            {"name": "Sebze", "icon_class": "fa-carrot"},
            {"name": "Tahıl & Bakliyat", "icon_class": "fa-wheat"},
            {"name": "Süt & Kahvaltılık", "icon_class": "fa-cheese"},
            {"name": "Organik Ürünler", "icon_class": "fa-leaf"}
        ]
        
        eklenen_kat = 0
        eklenen_urun = 0
        
        with app.app_context():
            # Kategorileri Ekle
            for k in kategoriler_data:
                if not Category.query.filter_by(name=k['name']).first():
                    yeni_kat = Category(name=k['name'], icon_class=k['icon_class'])
                    db.session.add(yeni_kat)
                    eklenen_kat += 1
            db.session.commit()
            
            # 3. Urunleri Ekle (Kategoriler olustuktan sonra)
            # Ornek urun listesi
            urunler_data = [
                ("Elma", 15.0, "Meyve", "Taze Amasya elması", "fa-apple-alt"),
                ("Domates", 20.0, "Sebze", "Bahçe domatesi", "fa-carrot"),
                ("Mercimek", 45.0, "Tahıl & Bakliyat", "Kırmızı mercimek 1kg", "fa-wheat"),
                ("Ezine Peyniri", 120.0, "Süt & Kahvaltılık", "Tam yağlı inek peyniri", "fa-cheese"),
                ("Köy Yumurtası", 3.5, "Organik Ürünler", "Gezen tavuk yumurtası", "fa-egg"),
                ("Salatalık", 12.0, "Sebze", "Çengelköy salatalığı", "fa-leaf"),
                ("Muz", 35.0, "Meyve", "Yerli anamur muzu", "fa-lemon"),
                ("Nohut", 50.0, "Tahıl & Bakliyat", "Koçbaşı nohut", "fa-seedling")
            ]

            for urun_adi, fiyat, kat_adi, aciklama, resim in urunler_data:
                # Urunun kategorisini bul
                kat = Category.query.filter_by(name=kat_adi).first()
                if kat:
                    # Urun daha once eklenmemisse ekle
                    if not Product.query.filter_by(name=urun_adi).first():
                        # Model yapisina uygun olusturmaya calis (slug olmadan)
                        try:
                            # Standart alanlar: name, price, description, category_id, image
                            yeni_urun = Product(
                                name=urun_adi,
                                price=fiyat,
                                description=aciklama,
                                category_id=kat.id,
                                image=resim # Gecici olarak ikon ismini resim diye kaydediyoruz
                            )
                            db.session.add(yeni_urun)
                            eklenen_urun += 1
                        except Exception as e:
                            print(f"Urun eklenirken hata: {e}")

            db.session.commit()
        
        # Başarı mesajı (Tek tırnak kullanarak çakışmayı önledik)
        return f'''
        <div style="font-family: sans-serif; padding: 50px; text-align: center; background: #d4edda; color: #155724; border: 2px solid #c3e6cb; border-radius: 10px; max-width: 600px; margin: 50px auto;">
            <h1 style="margin-top:0;">✅ Dükkan ve Depo Doldu!</h1>
            <p>Veritabanı başarıyla oluşturuldu.</p>
            <ul style="text-align:left; display:inline-block;">
                <li><strong>{eklenen_kat}</strong> adet kategori eklendi.</li>
                <li><strong>{eklenen_urun}</strong> adet ürün eklendi.</li>
            </ul>
            <br><br>
            <p style="font-size: 0.9em; color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;">
                ⚠️ <strong>ÖNEMLİ:</strong> Render ücretsiz sürümde, site kullanılmazsa bir süre sonra kapanır ve bu veriler silinebilir. 
                Veriler silinirse tekrar <strong>/hazirla</strong> adresine girerek bunları yükleyebilirsiniz.
            </p>
            <br>
            <a href="/" style="background: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 1.1em;">🛍️ Alışverişe Başla</a>
        </div>
        '''
    except Exception as e:
        import traceback
        # Hata mesajı (Tek tırnak kullanarak çakışmayı önledik)
        return f'''
        <div style="font-family: monospace; background: #f8d7da; padding: 20px; color: #721c24;">
            <h1>❌ Hata Oluştu</h1>
            <p>Veriler yüklenirken bir sorun çıktı:</p>
            <pre>{str(e)}</pre>
            <hr>
            <pre>{traceback.format_exc()}</pre>
        </div>
        '''
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
            
        print("✅ app.py temizlendi ve güncellendi! Artık hem KATEGORİ hem ÜRÜN ekleyen kod aktif.")
        
    else:
        # Kod hiç yoksa direkt ekle
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(veri_hazirlama_kodu)
        print("✅ app.py güncellendi! Artık site adresinin sonuna '/hazirla' yazarak verileri yükleyebilirsin.")

else:
    print("❌ app.py dosyası bulunamadı!")