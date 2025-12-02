import os

dosya_adi = "app.py"

# Bu kod, ne hata olursa olsun ekrana detaylıca yazdırır
debug_kodu = """

# --- HATA AYIKLAMA MODU (VERCEL) ---
import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    # Hatayi gizlemek yerine ekrana basar
    return f'''
    <div style="font-family: monospace; background: #f8d7da; padding: 20px; border: 1px solid #f5c6cb; color: #721c24;">
        <h1>⚠️ UYGULAMA HATASI</h1>
        <p>Aşağıdaki hatayı kopyalayıp geliştiriciye (yapay zekaya) iletin:</p>
        <hr>
        <pre>{traceback.format_exc()}</pre>
    </div>
    ''', 500
"""

if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    if "handle_exception" in icerik:
        print("⚠️ Hata gösterici kod zaten ekli.")
    else:
        with open(dosya_adi, "a", encoding="utf-8") as f:
            f.write(debug_kodu)
        print("✅ app.py güncellendi! Artık hatayı ekranda göreceğiz.")
else:
    print("❌ app.py dosyası bulunamadı!")