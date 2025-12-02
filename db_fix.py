import os

dosya_adi = "app.py"

eklenecek_kod = """

# --- VERCEL ICIN TABLO OLUSTURMA ---
# Uygulama her calistiginda tablolarin varligini kontrol et ve yoksa olustur
with app.app_context():
    try:
        db.create_all()
        print("✅ Tablolar basariyla olusturuldu (Vercel /tmp).")
    except Exception as e:
        print(f"⚠️ Tablo olusturma hatasi: {e}")
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()

    # Eğer bu kodu daha önce eklediysek tekrar eklemeyelim
    if "VERCEL ICIN TABLO OLUSTURMA" in icerik:
        print("⚠️ Bu kod zaten eklenmiş, tekrar eklenmedi.")
    else:
        # Kodu dosyanın en sonuna ekle
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(eklenecek_kod)
        print("✅ app.py güncellendi! Artık site açılınca tablolar otomatik oluşacak.")

else:
    print("❌ app.py dosyası bulunamadı!")