import os

dosya_adi = "app.py"
kod_parcasi = "app.config['SQLALCHEMY_DATABASE_URI']"

# Vercel için çalışan güvenli veritabanı ayarı
yeni_ayar = """
# --- VERCEL DATABASE AYARI ---
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
# Veritabanını geçici klasöre (/tmp) koyuyoruz ki hata vermesin
db_path = os.path.join('/tmp', 'tarim.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
# -----------------------------
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    # Eğer dosyada eski veritabanı ayarı varsa onu bulup değiştireceğiz
    if kod_parcasi in icerik:
        # Basit bir değiştirme yapıyoruz, eski satırı yoruma alıp yenisini ekliyoruz
        yeni_icerik = icerik.replace(kod_parcasi, "# ESKI AYAR IPTAL: " + kod_parcasi + "\n" + yeni_ayar)
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)
        print("✅ Veritabanı yolu /tmp olarak güncellendi!")
    else:
        print("⚠️ 'SQLALCHEMY_DATABASE_URI' satırı bulunamadı. Kodda farklı bir isimle mi yazılı?")
        # Bulamazsa en başa eklemeyi deneyelim (app tanımlandıktan sonraya)
        print("Lütfen app.py dosyasını kontrol et, veritabanı ayarını elle '/tmp/tarim.db' yap.")

else:
    print("❌ app.py dosyası bulunamadı!")