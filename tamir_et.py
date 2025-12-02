import os

dosya_adi = "app.py"

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        satirlar = f.readlines()
    
    yeni_satirlar = []
    degisiklik_yapildi = False

    for satir in satirlar:
        # Hata veren 'os.makedirs' komutunu bulursak
        if "os.makedirs" in satir:
            # Başına # koyarak o satırı yoruma çevir (iptal et)
            yeni_satirlar.append(f"# VERCEL_ICIN_IPTAL: {satir}")
            degisiklik_yapildi = True
            print(f"🔧 Şu satır iptal edildi: {satir.strip()}")
        else:
            yeni_satirlar.append(satir)
            
    if degisiklik_yapildi:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.writelines(yeni_satirlar)
        print("✅ app.py başarıyla güncellendi! Artık klasör oluşturmaya çalışmayacak.")
    else:
        print("⚠️ app.py içinde 'os.makedirs' bulunamadı. Belki daha önce silinmiştir?")

else:
    print("❌ app.py dosyası bulunamadı!")