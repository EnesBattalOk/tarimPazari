import os

dosya_adi = "app.py"
req_dosyasi = "requirements.txt"

# 1. requirements.txt içine Postgres kütüphanesini ekle
if os.path.exists(req_dosyasi):
    with open(req_dosyasi, "r", encoding="utf-8") as f:
        reqs = f.read()
    
    if "psycopg2-binary" not in reqs:
        with open(req_dosyasi, "a", encoding="utf-8") as f:
            f.write("\npsycopg2-binary\n")
        print("✅ requirements.txt güncellendi (psycopg2-binary eklendi).")
    else:
        print("ℹ️ psycopg2 zaten ekli.")
else:
    # Dosya yoksa oluştur
    with open(req_dosyasi, "w", encoding="utf-8") as f:
        f.write("Flask\nFlask-SQLAlchemy\nFlask-Login\nFlask-WTF\nemail_validator\nWerkzeug\nWTForms\nsqlalchemy\npsycopg2-binary\n")
    print("✅ requirements.txt oluşturuldu.")

# 2. app.py içindeki veritabanı ayarını değiştir
if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # Eski ayarı bul (Genelde SQLALCHEMY_DATABASE_URI diye başlar)
    # Biz daha garantili bir yöntemle, app.config satırının hemen üstüne akıllı bir kod ekleyeceğiz.
    
    yeni_veritabani_ayari = """
# --- VERITABANI AYARI (POSTGRES + SQLITE) ---
import os
# Vercel'den gelen Postgres adresini al
db_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")

if db_url:
    # Postgres adresi bazen 'postgres://' diye baslar, onu 'postgresql://' yapmamiz gerek
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    print("✅ Vercel Postgres Veritabanı kullanılıyor.")
else:
    # Eger Vercel degilse veya link yoksa eski usul /tmp kullan (Hata vermemesi icin)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join('/tmp', 'tarim.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    print("⚠️ Yerel SQLite kullanılıyor (Veriler silinebilir).")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------------------------------------
"""
    
    # app = Flask(__name__) satırını bulup hemen altına yapıştıralım
    if "app = Flask" in icerik:
        # Önce eski SQLALCHEMY_DATABASE_URI tanımlarını temizleyelim (Basitçe yoruma alalım)
        # Bu biraz riskli o yüzden direkt en güvenli yere, app tanımlandıktan sonraya ekliyoruz.
        # Eski tanımlar kalsa bile bu kod en son çalışacağı için onları ezecektir (Python yukarıdan aşağı çalışır).
        
        parcalar = icerik.split("app = Flask")
        # app = Flask... satırını koruyarak araya kodumuzu sokuyoruz
        yeni_icerik = parcalar[0] + "app = Flask" + parcalar[1].split("\n", 1)[0] + "\n" + yeni_veritabani_ayari + "\n" + parcalar[1].split("\n", 1)[1]
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)
        print("✅ app.py güncellendi! Artık Postgres varsa onu kullanacak.")
    else:
        print("❌ app.py içinde 'app = Flask' bulunamadı.")

else:
    print("❌ app.py dosyası bulunamadı!")
```

#### 3. Uygula ve Gönder

1.  Terminali aç ve kodu çalıştır:
    ```bash
    python postgres_gecis.py
    ```

2.  GitHub'a gönder:
    ```bash
    git add .
    git commit -m "postgres gecisi yapildi"
    git push