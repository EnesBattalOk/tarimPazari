import os

dosya_adi = "app.py"

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        satirlar = f.readlines()
    
    yeni_satirlar = []
    models_eklendi = False
    
    # 1. Önce "from models import" var mı diye bakalım
    models_var_mi = any("from models import" in s or "import models" in s for s in satirlar)
    
    for satir in satirlar:
        # Eğer db.create_all() komutunu görürsek ve henüz models eklenmediyse
        if "db.create_all()" in satir and not models_eklendi:
            # Hemen öncesine models import satırını ekle (Eğer yoksa)
            if not models_var_mi:
                yeni_satirlar.append("# Modelleri veritabanı olusmadan once tanitiyoruz:\n")
                yeni_satirlar.append("from models import *\n") 
                print("✅ Modeller db.create_all() öncesine eklendi.")
            models_eklendi = True
            yeni_satirlar.append(satir)
        else:
            yeni_satirlar.append(satir)
            
    # Dosyayı kaydet
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.writelines(yeni_satirlar)
    
    if not models_eklendi:
        print("⚠️ Uyarı: 'db.create_all()' komutu app.py içinde bulunamadı. db_fix.py'yi çalıştırdın mı?")
    else:
        print("🚀 app.py güncellendi! Artık tablolar eksiksiz oluşacak.")

else:
    print("❌ app.py bulunamadı!")