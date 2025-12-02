import os

dosya_adi = "app.py"

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    # Eski tanımlamayı bul ve yenisiyle değiştir
    eski_kod = "app = Flask(__name__)"
    yeni_kod = "app = Flask(__name__, instance_path='/tmp')"
    
    if eski_kod in icerik:
        yeni_icerik = icerik.replace(eski_kod, yeni_kod)
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)
        print("✅ app.py düzeltildi! Flask artık /tmp klasörünü kullanacak.")
    else:
        print("⚠️ Kodda 'app = Flask(__name__)' tam olarak bulunamadı. Belki parantez içinde başka şeyler vardır?")
        # Alternatif: Eğer app = Flask(__name__, template_folder='...') gibi yazılmışsa diye kontrol
        print("Lütfen app.py dosyasını açıp 'app = Flask' ile başlayan satırı kontrol et.")

else:
    print("❌ app.py dosyası bulunamadı!")