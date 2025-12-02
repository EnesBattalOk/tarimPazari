import os
import re

dosya_adi = "app.py"
req_dosyasi = "requirements.txt"

# 1. SİLİNECEK DOSYALAR (Vercel ve Yardımcı Scriptler)
silinecekler = [
    "vercel.json",          # Vercel ayar dosyası
    "duzenle.py",
    "fix_json.py",
    "tamir_et.py",
    "son_tamir.py",
    "db_fix.py",
    "tablo_tanit.py",
    "hata_goster.py",
    "db_yolu_duzelt.py",
    "kurtarici.py",
    "super_tamir.py",
    "zorla_ac.py",
    "postgres_gecis.py",
    "veri_yukle.py",
    "temizlik.py"
]

print("🔄 Fabrika ayarlarına dönüş başlıyor...\n")

# --- ADIM 1: Gereksiz Dosyaları Sil ---
for dosya in silinecekler:
    if os.path.exists(dosya):
        try:
            os.remove(dosya)
            print(f"🗑️  Silindi: {dosya}")
        except:
            pass

# --- ADIM 2: requirements.txt Temizliği ---
if os.path.exists(req_dosyasi):
    with open(req_dosyasi, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # psycopg2 (Postgres) kütüphanesini çıkar
    yeni_lines = [line for line in lines if "psycopg2" not in line]
    
    with open(req_dosyasi, "w", encoding="utf-8") as f:
        f.writelines(yeni_lines)
    print("✅ requirements.txt sadeleştirildi.")

# --- ADIM 3: app.py Temizliği (En Önemlisi) ---
if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # A. Vercel için eklenen 'instance_path=/tmp' ayarını kaldır
    if "app = Flask(__name__, instance_path='/tmp')" in icerik:
        icerik = icerik.replace("app = Flask(__name__, instance_path='/tmp')", "app = Flask(__name__)")
        print("✅ Flask tanımlaması düzeltildi.")

    # B. Eklediğimiz blokları Regex ile bulup silelim
    
    # 1. Veritabanı Ayarı Bloğu
    icerik = re.sub(r'# --- VERITABANI AYARI \(POSTGRES \+ SQLITE\) ---.*?# ---------------------------------------------\n', '', icerik, flags=re.DOTALL)
    
    # 2. Hata Ayıklama Modu
    icerik = re.sub(r'# --- HATA AYIKLAMA MODU \(VERCEL\) ---.*?# ---------------------------------------------\n', '', icerik, flags=re.DOTALL)
    
    # 3. Kurtarıcı Fonksiyon (safe_get_categories)
    icerik = re.sub(r'# --- VERCEL ICIN OZEL KURTARICI FONKSIYON ---.*?# -------------------------------------------\n', '', icerik, flags=re.DOTALL)
    
    # 4. Veritabanı Hazırlama Rotası (/hazirla)
    icerik = re.sub(r'# --- VERITABANI DOLDURMA ROTASI \(VERCEL ICIN\) ---.*?# -----------------------------------------------\n', '', icerik, flags=re.DOTALL)

    # 5. Zorla Açma Modu (inject_cart) - Bunu eski haline çevirelim
    # Eski basit haline regex ile zor olduğu için manuel yerine koyuyoruz
    inject_cart_eski = """
@app.context_processor
def inject_cart():
    try:
        return dict(cart_info=get_cart_total(), categories=Category.query.all())
    except:
        return dict(cart_info={'count': 0, 'total': 0}, categories=[])
"""
    # Eğer bizim eklediğimiz karmaşık inject_cart varsa, basitiyle değiştir
    if "def inject_cart():" in icerik and "# --- ZORLA ACMA MODU ---" in icerik:
        # Fonksiyonun başlangıcından bitişine kadar olan kısmı bulup değiştirmemiz lazım
        # Bu karmaşık olduğu için basitçe app.py içinde aratıp replace yapıyoruz
        match = re.search(r'def inject_cart\(\):.*?# -----------------------', icerik, flags=re.DOTALL)
        if match:
            icerik = icerik.replace(match.group(0), "def inject_cart():\n    return dict(cart_info=get_cart_total(), categories=Category.query.all())")
            print("✅ inject_cart fonksiyonu sadeleştirildi.")

    # 6. Yorum satırı ile iptal edilen os.makedirs'ı geri aç
    icerik = icerik.replace("# VERCEL_ICIN_IPTAL: ", "")

    # C. Dosyayı Kaydet
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(icerik)
    print("✅ app.py içindeki Vercel kodları temizlendi.")

else:
    print("❌ app.py bulunamadı!")

print("\n✨ Projeniz eski haline döndü! Artık Netlify için hazırsınız.")
print("Son adım olarak terminalde şu komutu çalıştırıp kendi bilgisayarındaki temizlik.py ve orijinal_don.py dosyalarını silebilirsin.")