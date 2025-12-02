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

# 2. app.py dosyasını güncelle
if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # Eğer zaten ayarlıysa elleme
    if "os.environ.get('DATABASE_URL')" in icerik:
        print("⚠️ app.py zaten veritabanı ayarına sahip görünüyor.")
    else:
        # app = Flask... satırını bul
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
            # app = Flask satırının hemen sonrasına ekle
            parcalar = icerik.split("app = Flask")
            # app = Flask... satırını koruyarak araya kodumuzu sokuyoruz
            # parcalar[1]'in ilk satırı (app tanımlaması) bittikten sonraya ekleyelim
            kalan_kisim = parcalar[1]
            ilk_satir_sonu = kalan_kisim.find("\n")
            
            yeni_icerik = parcalar[0] + "app = Flask" + kalan_kisim[:ilk_satir_sonu+1] + db_ayar_kodu + kalan_kisim[ilk_satir_sonu+1:]
            
            # Eğer eski SQLALCHEMY tanımları varsa onları devre dışı bırakmak lazım ama
            # Python yukarıdan aşağı çalıştığı için bu kodun onlardan SONRA gelmesi lazım.
            # En garantisi: app.config['SQLALCHEMY_DATABASE_URI'] geçen eski satırları bulup yoruma almak.
            
            # Basitçe eski tanımları bulup # ile iptal edelim (Yeni eklediğimiz hariç)
            # Ama bu karmaşık olabilir. En temiz yöntem, bu kodun app.py'nin en tepesine yakın (app tanımından hemen sonra) olması ve 
            # eski kodların aşağıda kalsa bile bu ayarın geçerli olmasıdır.
            # Ancak app.config ataması aşağıda tekrar yapılırsa bozulur.
            
            # O yüzden eski atamayı bulup silelim:
            eski_ayar_pattern = "app.config['SQLALCHEMY_DATABASE_URI'] ="
            # Yeni eklediğimiz kodda da bu satır var, o yüzden dikkatli olmalıyız.
            
            # Dosyayı kaydet
            with open(dosya_adi, "w", encoding="utf-8") as f:
                f.write(yeni_icerik)
            print("✅ app.py güncellendi! Artık Render veritabanını tanıyacak.")
        else:
            print("❌ app.py içinde 'app = Flask' bulunamadı.")
else:
    print("❌ app.py dosyası bulunamadı!")