import os

dosya_adi = "app.py"
req_dosyasi = "requirements.txt"

# 1. PostgreSQL kütüphanesini (psycopg2) ekle
if os.path.exists(req_dosyasi):
    with open(req_dosyasi, "r", encoding="utf-8") as f:
        reqs = f.read()
    
    if "psycopg2-binary" not in reqs:
        with open(req_dosyasi, "a", encoding="utf-8") as f:
            f.write("\npsycopg2-binary\n")
        print("✅ requirements.txt güncellendi (psycopg2 eklendi).")
    else:
        print("ℹ️ psycopg2 zaten ekli.")

# 2. app.py dosyasını güncelle (Veritabanı Ayarı)
if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # Eğer zaten ayarlıysa elleme, yoksa ekle
    if "os.environ.get('DATABASE_URL')" in icerik:
        print("⚠️ app.py zaten veritabanı ayarına sahip görünüyor.")
    else:
        if "app = Flask" in icerik:
            # Yeni veritabanı ayar kodu
            db_ayar_kodu = """
# --- VERITABANI AYARI (RENDER POSTGRES) ---
import os
# Render'dan gelen veritabanı adresini al
db_url = os.environ.get("DATABASE_URL")

if db_url:
    # Postgres adresi bazen 'postgres://' diye baslar, onu 'postgresql://' yapmamiz gerek
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    print("✅ Render Postgres Veritabanı kullanılıyor.")
else:
    # Lokal bilgisayarda yine SQLite kullan
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'tarim.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    print("⚠️ Yerel SQLite kullanılıyor.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------------------------------------
"""
            parcalar = icerik.split("app = Flask")
            # app = Flask... satırını koruyarak araya kodumuzu sokuyoruz
            # parcalar[1]'in ilk satırı (app tanımlaması) bittikten sonraya ekleyelim
            kalan_kisim = parcalar[1]
            ilk_satir_sonu = kalan_kisim.find("\n")
            
            yeni_icerik = parcalar[0] + "app = Flask" + kalan_kisim[:ilk_satir_sonu+1] + db_ayar_kodu + kalan_kisim[ilk_satir_sonu+1:]
            
            # Eski SQLALCHEMY tanımlarını temizleyelim (Çakışma olmasın)
            # Basitçe eski 'app.config['SQLALCHEMY_DATABASE_URI'] =' satırlarını yoruma alalım
            # (Yeni eklediğimiz kod hariç)
            
            # Bu biraz riskli regex yerine basitçe dosyanın en üstüne (app'den sonraya) ekledik,
            # Python aşağı doğru okuduğu için eğer aşağıda başka tanım varsa bizimki ezilebilir.
            # O yüzden eski tanımları bulup silmek daha garanti.
            
            if "app.config['SQLALCHEMY_DATABASE_URI'] =" in kalan_kisim:
                 print("ℹ️ Eski veritabanı ayarları algılandı, temizleniyor...")
                 # Eski ayarı etkisiz hale getirmek için basit bir replace yapıyoruz
                 # Not: Bu tam çözüm olmayabilir ama genelde işe yarar.
                 yeni_icerik = yeni_icerik.replace("app.config['SQLALCHEMY_DATABASE_URI'] =", "# ESKI AYAR: app.config['SQLALCHEMY_DATABASE_URI'] =")
                 # Kendi eklediğimiz kodda da bu satır var, onu geri düzeltelim :)
                 yeni_icerik = yeni_icerik.replace("# ESKI AYAR: app.config['SQLALCHEMY_DATABASE_URI'] = db_url", "app.config['SQLALCHEMY_DATABASE_URI'] = db_url")
                 yeni_icerik = yeni_icerik.replace("# ESKI AYAR: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path", "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path")

            with open(dosya_adi, "w", encoding="utf-8") as f:
                f.write(yeni_icerik)
            print("✅ app.py veritabanı ayarı güncellendi! Artık Render veritabanını tanıyacak.")
        else:
            print("❌ app.py içinde 'app = Flask' bulunamadı.")

    # 3. VERİ YÜKLEME ROTASINI EKLE (/hazirla)
    # Veritabanı boş olduğu için bu rotaya ihtiyacımız var.
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik_son = f.read()

    if "/hazirla" not in icerik_son:
        veri_hazirlama_kodu = """

# --- RENDER VERI YUKLEME (URUNLER DAHIL) ---
@app.route('/hazirla')
def veritabani_hazirla():
    try:
        from models import Category, Product
        
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
            for k in kategoriler_data:
                if not Category.query.filter_by(name=k['name']).first():
                    yeni_kat = Category(name=k['name'], icon_class=k['icon_class'])
                    db.session.add(yeni_kat)
                    eklenen_kat += 1
            db.session.commit()
            
            # 3. Urunleri Ekle
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
                kat = Category.query.filter_by(name=kat_adi).first()
                if kat:
                    if not Product.query.filter_by(name=urun_adi).first():
                        try:
                            yeni_urun = Product(
                                name=urun_adi,
                                price=fiyat,
                                description=aciklama,
                                category_id=kat.id,
                                image=resim
                            )
                            db.session.add(yeni_urun)
                            eklenen_urun += 1
                        except:
                            pass
            db.session.commit()
        
        return f'''
        <div style="font-family: sans-serif; padding: 50px; text-align: center; background: #d4edda; color: #155724;">
            <h1>✅ Veritabanı Hazır!</h1>
            <p>Postgres veritabanına bağlanıldı ve dolduruldu.</p>
            <ul>
                <li>{eklenen_kat} Kategori</li>
                <li>{eklenen_urun} Ürün</li>
            </ul>
            <br>
            <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none;">Siteye Git</a>
        </div>
        '''
    except Exception as e:
        import traceback
        return f"<h1>Hata:</h1><pre>{traceback.format_exc()}</pre>"
# -----------------------------------------------
"""
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(veri_hazirlama_kodu)
        print("✅ /hazirla rotası eklendi. Site açılınca bu adrese girip verileri doldurmalısın.")
    else:
        print("ℹ️ /hazirla rotası zaten var.")

else:
    print("❌ app.py dosyası bulunamadı!")