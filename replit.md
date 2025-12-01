# TarımPazarı - E-Ticaret Pazar Yeri Platformu

## Genel Bakış
TarımPazarı, çiftçileri (alıcılar) ve tedarikçileri (satıcılar) buluşturan tam kapsamlı bir e-ticaret pazar yeri platformudur.

## Teknoloji Yığını
- **Backend**: Python 3.11, Flask
- **Veritabanı**: SQLite + SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **UI Framework**: Bootstrap 5 (CDN)
- **İkonlar**: FontAwesome (CDN)

## Proje Yapısı
```
├── app.py              # Ana Flask uygulaması, route'lar ve iş mantığı
├── models.py           # SQLAlchemy veritabanı modelleri
├── seed_data.py        # Başlangıç verileri script'i
├── templates/          # Jinja2 HTML şablonları
│   ├── base.html       # Ana şablon
│   ├── index.html      # Ana sayfa
│   ├── products.html   # Ürün listesi
│   ├── product_detail.html
│   ├── cart.html       # Sepet
│   ├── checkout.html   # Ödeme
│   ├── orders.html     # Siparişler
│   ├── login.html      # Giriş
│   ├── register.html   # Kayıt
│   ├── seller/         # Satıcı paneli şablonları
│   └── admin/          # Admin paneli şablonları
├── static/
│   ├── css/style.css   # Özel CSS stilleri
│   └── js/main.js      # JavaScript (AJAX, sepet işlemleri)
└── tarim_pazari.db     # SQLite veritabanı
```

## Hibrit Lojistik Algoritması
Backend, sepetteki ürünlerin toplam "Desi" (hacimsel ağırlık) hesabını yapar:
- **Desi < 30**: Kargo Entegrasyonu (standart kargo)
- **Desi >= 30**: Ambar/Nakliye (büyük yük taşımacılığı)

## Kullanıcı Rolleri
1. **Admin**: Satıcıları onaylar, kategorileri yönetir
2. **Satıcı (Tedarikçi)**: Ürün yükler, desi/stok girer, siparişleri yönetir
3. **Alıcı (Çiftçi)**: Ürünleri gezer, filtreler, sepete ekler, yorum yapar

## Demo Hesapları
- **Admin**: admin@tarimpazari.com / admin123
- **Satıcı**: info@antalyaseramarket.com / seller123
- **Alıcı**: mehmet@ciftci.com / buyer123

## Çalıştırma
```bash
python app.py
```
Sunucu `http://0.0.0.0:5000` adresinde çalışır.

## Tema Renkleri
- **Ana Renk**: Koyu Yeşil (#2E7D32)
- **Aksiyon Rengi**: Turuncu (#F57C00)

## Son Değişiklikler
- Proje oluşturuldu ve tüm temel özellikler eklendi
- Hibrit lojistik algoritması implement edildi
- Trendyol/Hepsiburada tarzı UI tasarlandı
