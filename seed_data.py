import random
from datetime import datetime, timedelta
from models import db, User, Category, Product, Order, OrderItem, Review, Wishlist
from werkzeug.security import generate_password_hash

def seed_database(drop_all=False):
    """
    Veritabanını kapsamlı demo verileriyle doldurur.
    drop_all=True ise tüm tabloları siler ve yeniden oluşturur.
    """
    
    if drop_all:
        db.drop_all()
        db.create_all()
        print("✅ Tüm tablolar silindi ve yeniden oluşturuldu.")
    
    # ============================================================================
    # 1. TANIMLI KULLANICILAR (Kolay giriş için)
    # ============================================================================
    
    admin = User(
        username='admin',
        email='admin@tarimpazari.com',
        password_hash=generate_password_hash('Admin123!'),
        role='admin',
        is_seller_approved=True
    )
    db.session.add(admin)
    
    seller_approved = User(
        username='antalyasera',
        email='satici@tarimpazari.com',
        password_hash=generate_password_hash('Satici123!'),
        role='seller',
        is_seller_approved=True,
        company_name='Antalya Sera Market',
        tax_number='1234567890',
        tax_office='Antalya Vergi Dairesi'
    )
    db.session.add(seller_approved)
    
    seller_pending = User(
        username='yeniciftci',
        email='yeni@tarimpazari.com',
        password_hash=generate_password_hash('Satici123!'),
        role='seller',
        is_seller_approved=False,
        company_name='Yeni Çiftçi Ltd',
        tax_number='9876543210',
        tax_office='İstanbul Vergi Dairesi'
    )
    db.session.add(seller_pending)
    
    buyer = User(
        username='alici',
        email='alici@tarimpazari.com',
        password_hash=generate_password_hash('Alici123!'),
        role='buyer',
        is_seller_approved=False
    )
    db.session.add(buyer)
    
    db.session.flush()
    
    # ============================================================================
    # 2. RASTGELE KULLANICILAR (20 Alıcı & 20 Satıcı hedefi için)
    # ============================================================================
    
    seller_companies = [
        ("Konya Gübre", "konyagubre"),
        ("Ege Tohum", "egetohum"),
        ("Akdeniz Sera", "akdenizsera"),
        ("Karadeniz Fidan", "karadenizfidan"),
        ("Trakya Tarım", "trakyatarim"),
        ("Marmara Sulama", "marmarasulama"),
        ("İç Anadolu Makine", "icanadolumakine"),
        ("Güneydoğu Zirai", "guneydoguzirai"),
        ("Bursa Organik", "bursaorganik"),
        ("İzmir Sera Sistemleri", "izmirsera"),
        ("Adana Tarım Market", "adanatarim"),
        ("Mersin Tohum Evi", "mersintohum"),
        ("Denizli Gübre Deposu", "denizligubre"),
        ("Eskişehir Fidancılık", "eskisehirfidan"),
        ("Samsun Tarım AŞ", "samsuntarim"),
        ("Gaziantep Sera", "gaziantepsera"),
        ("Kayseri Sulama", "kayserisulama"),
        ("Balıkesir Organik", "balikesirorganik")
    ]
    
    approved_sellers = [seller_approved]
    
    for i, (company, username) in enumerate(seller_companies):
        is_approved = random.choice([True, True, True, False])
        seller = User(
            username=username,
            email=f'{username}@firma.com',
            password_hash=generate_password_hash('Satici123!'),
            role='seller',
            is_seller_approved=is_approved,
            company_name=company,
            tax_number=f'{random.randint(1000000000, 9999999999)}',
            tax_office=f'{company.split()[0]} Vergi Dairesi'
        )
        db.session.add(seller)
        if is_approved:
            approved_sellers.append(seller)
    
    db.session.flush()
    
    buyer_names = [
        ("Ahmet", "Yılmaz"),
        ("Ayşe", "Demir"),
        ("Mehmet", "Kaya"),
        ("Fatma", "Çelik"),
        ("Ali", "Şahin"),
        ("Zeynep", "Yıldız"),
        ("Mustafa", "Öztürk"),
        ("Emine", "Aydın"),
        ("Hasan", "Arslan"),
        ("Hatice", "Doğan"),
        ("Hüseyin", "Kılıç"),
        ("Elif", "Aslan"),
        ("İbrahim", "Çetin"),
        ("Merve", "Koç"),
        ("Osman", "Kurt"),
        ("Selin", "Özdemir"),
        ("Burak", "Erdoğan"),
        ("Gamze", "Polat"),
        ("Emre", "Özkan")
    ]
    
    all_buyers = [buyer]
    
    for first_name, last_name in buyer_names:
        username = f'{first_name.lower()}{last_name.lower()}'
        buyer_user = User(
            username=username,
            email=f'{username}@email.com',
            password_hash=generate_password_hash('Alici123!'),
            role='buyer',
            is_seller_approved=False
        )
        db.session.add(buyer_user)
        all_buyers.append(buyer_user)
    
    db.session.flush()
    
    # ============================================================================
    # 3. KATEGORİLER
    # ============================================================================
    
    categories = [
        Category(name='Sera Malzemeleri', icon_class='fa-warehouse'),
        Category(name='Gübre', icon_class='fa-seedling'),
        Category(name='Tohum', icon_class='fa-leaf'),
        Category(name='Sulama', icon_class='fa-tint'),
        Category(name='Zirai İlaç', icon_class='fa-spray-can'),
        Category(name='Tarım Makineleri', icon_class='fa-tractor'),
    ]
    
    for cat in categories:
        db.session.add(cat)
    
    db.session.flush()
    
    # ============================================================================
    # 4. ÜRÜNLER (60+ Ürün - %50 Ağır, %50 Hafif)
    # ============================================================================
    
    heavy_products = [
        ("Galvanizli Sera Profili 6m", "Sera Malzemeleri", 850.00, 45.0, "Yüksek kaliteli galvanizli çelik profil. 6 metre uzunluk, korozyona dayanıklı.", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"),
        ("Demir Sera Direği Set", "Sera Malzemeleri", 1200.00, 55.0, "10 adet 3m demir direk seti. Montaj aksesuarları dahil.", "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400"),
        ("Sera Naylonu Rulo 100m", "Sera Malzemeleri", 2800.00, 40.0, "UV filtreli, 8m genişlik, 100m uzunluk sera örtüsü.", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"),
        ("Alüminyum Sera Çatı Sistemi", "Sera Malzemeleri", 4500.00, 65.0, "Komple çatı sistemi, 50m² alan için yeterli.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400"),
        ("Polikarbon Sera Paneli 10'lu", "Sera Malzemeleri", 3200.00, 48.0, "4mm kalınlık, UV korumalı, 10 adet panel.", "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"),
        ("Sera Havalandırma Motoru", "Sera Malzemeleri", 1800.00, 35.0, "Otomatik açılır kapanır pencere sistemi.", "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400"),
        ("Çelik Sera İskeleti Komple", "Sera Malzemeleri", 8500.00, 120.0, "100m² sera için komple iskelet sistemi.", "https://images.unsplash.com/photo-1592502712628-162b0f3c1c4d?w=400"),
        ("Tonluk Organik Gübre", "Gübre", 2500.00, 100.0, "1000kg organik kompost gübre. Tüm bitkiler için.", "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400"),
        ("Hayvan Gübresi 500kg", "Gübre", 1200.00, 60.0, "Fermente edilmiş büyükbaş gübresi.", "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400"),
        ("Solucan Gübresi 250kg", "Gübre", 1800.00, 35.0, "Premium kalite solucan humusu.", "https://images.unsplash.com/photo-1584479898061-15742e14f50d?w=400"),
        ("Kimyasal Gübre Paket 200kg", "Gübre", 950.00, 32.0, "NPK 15-15-15 granül gübre.", "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=400"),
        ("Organik Kompost 300kg", "Gübre", 680.00, 38.0, "Bitkisel atıklardan üretilmiş kompost.", "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=400"),
        ("Tavuk Gübresi 400kg", "Gübre", 520.00, 50.0, "Kurutulmuş ve işlenmiş tavuk gübresi.", "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=400"),
        ("Deniz Yosunu Gübresi 100kg", "Gübre", 1400.00, 33.0, "Doğal deniz yosunu özütü, sıvı konsantre.", "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400"),
        ("Endüstriyel Sulama Pompası", "Sulama", 3500.00, 45.0, "5.5 HP dizel motor, yüksek basınç.", "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400"),
        ("Sulama Borusu 1000m", "Sulama", 2200.00, 80.0, "32mm PE boru, 1000 metre rulo.", "https://images.unsplash.com/photo-1558904541-efa843a96f01?w=400"),
        ("Büyük Sulama Tankı 5000L", "Sulama", 4800.00, 150.0, "Polyester su deposu, UV dayanımlı.", "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=400"),
        ("Merkezi Sulama Sistemi", "Sulama", 6500.00, 95.0, "Otomatik programlanabilir sistem, 1 hektar.", "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=400"),
        ("Yağmurlama Sistemi Pro", "Sulama", 2800.00, 42.0, "360° döner başlıklar, 50 adet set.", "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400"),
        ("Derin Kuyu Pompası", "Sulama", 4200.00, 55.0, "Paslanmaz çelik, 100m derinlik kapasitesi.", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"),
        ("Filtre Sistemi Endüstriyel", "Sulama", 1900.00, 38.0, "Disk filtre, otomatik yıkamalı.", "https://images.unsplash.com/photo-1473973266408-ed4e27abdd47?w=400"),
        ("Damlama Sistemi 5 Hektar", "Sulama", 8500.00, 110.0, "Komple damlama sulama paketi.", "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400"),
        ("Tohum Serpme Makinesi", "Tohum", 2400.00, 65.0, "Traktör arkası, ayarlanabilir serpme.", "https://images.unsplash.com/photo-1592982537447-6f2a6a0c7c10?w=400"),
        ("Endüstriyel Tohum Kurutma", "Sera Malzemeleri", 5500.00, 85.0, "Elektrikli tohum kurutma makinesi.", "https://images.unsplash.com/photo-1595841696677-6489ff3f8cd1?w=400"),
        ("Sera Isıtma Kazanı", "Sera Malzemeleri", 7200.00, 130.0, "Kömür/odun yakıtlı, 500m² ısıtma.", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=400"),
        ("Otomatik Sulama Kontrol Ünitesi", "Sulama", 3100.00, 40.0, "IoT destekli akıllı sulama sistemi.", "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=400"),
        ("Gübre Karıştırma Tankı", "Gübre", 2600.00, 75.0, "1000L kapasiteli, motorlu karıştırıcı.", "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400"),
        ("Sera Gölgeleme Sistemi", "Sera Malzemeleri", 1950.00, 52.0, "%50 gölgeleme, 500m² alan için.", "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400"),
        ("Profesyonel Sera Fanı", "Sera Malzemeleri", 1100.00, 32.0, "Yüksek debili havalandırma fanı.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400"),
        ("Toprak İşleme Seti Pro", "Sera Malzemeleri", 890.00, 35.0, "Profesyonel bahçe aletleri seti.", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"),
    ]
    
    light_products = [
        ("Domates Tohumu Premium", "Tohum", 45.00, 0.5, "Organik sertifikalı, 100 adet tohum.", "https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400"),
        ("Biber Tohumu Karışık", "Tohum", 38.00, 0.3, "5 farklı çeşit biber tohumu, 50'şer adet.", "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400"),
        ("Salatalık Tohumu", "Tohum", 32.00, 0.4, "Kornişon salatalık, 80 adet tohum.", "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400"),
        ("Patlıcan Tohumu", "Tohum", 42.00, 0.3, "Kemer patlıcan, 60 adet tohum.", "https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=400"),
        ("Marul Tohumu Mix", "Tohum", 28.00, 0.2, "4 çeşit marul, toplam 200 tohum.", "https://images.unsplash.com/photo-1556801712-76c8eb07bbc9?w=400"),
        ("Fasulye Tohumu", "Tohum", 55.00, 1.0, "Ayşe kadın fasulye, 500g paket.", "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400"),
        ("Kabak Tohumu", "Tohum", 35.00, 0.5, "Sakız kabağı, 30 adet tohum.", "https://images.unsplash.com/photo-1570586437263-ab629fccc818?w=400"),
        ("Havuç Tohumu", "Tohum", 25.00, 0.2, "Nantes havuç, 500 adet tohum.", "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400"),
        ("Soğan Tohumu", "Tohum", 40.00, 0.3, "Kırmızı soğan, 300 adet tohum.", "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400"),
        ("Ispanak Tohumu", "Tohum", 22.00, 0.2, "Bölgeye uygun çeşit, 400 tohum.", "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400"),
        ("Bahçe Makası Pro", "Sera Malzemeleri", 85.00, 0.8, "Paslanmaz çelik, ergonomik sap.", "https://images.unsplash.com/photo-1617576683096-00fc8eecb3af?w=400"),
        ("Budama Makası", "Sera Malzemeleri", 120.00, 0.6, "Profesyonel dal kesme makası.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400"),
        ("El Çapası", "Sera Malzemeleri", 45.00, 1.2, "Çelik başlık, ahşap sap.", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"),
        ("Bahçe Eldiveni 5'li", "Sera Malzemeleri", 65.00, 0.5, "Su geçirmez, dikenli iş için.", "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=400"),
        ("Toprak pH Ölçer", "Sera Malzemeleri", 180.00, 0.3, "Dijital ekran, anlık ölçüm.", "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400"),
        ("Nem Ölçer Dijital", "Sera Malzemeleri", 95.00, 0.2, "Toprak nem sensörü.", "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=400"),
        ("Bitki Etiketi 100'lü", "Sera Malzemeleri", 35.00, 0.4, "Plastik, yazılabilir etiket.", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=400"),
        ("Fide Tepsisi 50 Gözlü", "Sera Malzemeleri", 28.00, 0.8, "Sert plastik, tekrar kullanılabilir.", "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=400"),
        ("Saksı 5L 10'lu Paket", "Sera Malzemeleri", 55.00, 2.0, "Drenaj delikli plastik saksı.", "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"),
        ("Sera İpi 500m", "Sera Malzemeleri", 45.00, 1.5, "Dayanıklı PP ip, yeşil renk.", "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"),
        ("Sıvı Gübre 5L", "Gübre", 120.00, 6.0, "Yaprak gübresi, tüm bitkiler için.", "https://images.unsplash.com/photo-1584479898061-15742e14f50d?w=400"),
        ("Organik Sıvı Gübre 2L", "Gübre", 85.00, 2.5, "Deniz yosunu özlü, organik.", "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400"),
        ("Mikro Besin Seti", "Gübre", 145.00, 1.0, "Demir, çinko, mangan karışımı.", "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=400"),
        ("Kök Güçlendirici", "Gübre", 95.00, 0.8, "Köklendirme hormonu, 250ml.", "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400"),
        ("Yaprak Parlatıcı", "Gübre", 55.00, 0.5, "Doğal yaprak bakım spreyi.", "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=400"),
        ("Mini Damlama Seti", "Sulama", 185.00, 3.0, "Balkon/teras için, 20 saksı kapasiteli.", "https://images.unsplash.com/photo-1558904541-efa843a96f01?w=400"),
        ("Bahçe Hortumu 25m", "Sulama", 220.00, 5.0, "Örgülü, bükülmez hortum.", "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400"),
        ("Sulama Tabancası Pro", "Sulama", 75.00, 0.4, "7 fonksiyonlu, metal gövde.", "https://images.unsplash.com/photo-1473973266408-ed4e27abdd47?w=400"),
        ("Sprinkler Başlığı 5'li", "Sulama", 65.00, 0.6, "Ayarlanabilir açı, plastik.", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"),
        ("Damla Sulama Aparatı 50'li", "Sulama", 95.00, 1.0, "Ayarlanabilir damlatıcı.", "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400"),
        ("Mantar İlacı 1L", "Zirai İlaç", 85.00, 1.5, "Külleme ve mildiyö için etkili.", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"),
        ("Yaprak Biti İlacı 500ml", "Zirai İlaç", 65.00, 0.8, "Organik sertifikalı, tüm bitkiler için.", "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=400"),
        ("Kırmızı Örümcek İlacı", "Zirai İlaç", 95.00, 1.0, "Sera ve açık alan için etkili.", "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"),
        ("Genel Böcek İlacı 2L", "Zirai İlaç", 120.00, 2.5, "Geniş spektrumlu böcek ilacı.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400"),
        ("Yabani Ot İlacı 5L", "Zirai İlaç", 180.00, 6.0, "Seçici herbisit, tahıllar için.", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"),
        ("Toprak Dezenfektanı 10L", "Zirai İlaç", 250.00, 12.0, "Toprak kaynaklı hastalıklar için.", "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400"),
        ("Biyolojik Mücadele Seti", "Zirai İlaç", 320.00, 2.0, "Faydalı böcekler ile doğal mücadele.", "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400"),
        ("Bakır Sülfat 5kg", "Zirai İlaç", 145.00, 6.0, "Bordo bulamacı için, fungisit.", "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=400"),
        ("Kükürt Tozu 10kg", "Zirai İlaç", 95.00, 11.0, "Organik tarımda kullanılabilir.", "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400"),
        ("Neem Yağı Konsantre 1L", "Zirai İlaç", 175.00, 1.2, "Doğal böcek kovucu ve fungisit.", "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=400"),
    ]
    
    machinery_products = [
        ("Benzinli Çim Biçme Makinesi", "Tarım Makineleri", 4500.00, 45.0, "4 zamanlı motor, 46cm kesim genişliği.", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"),
        ("Akülü Budama Makası Pro", "Tarım Makineleri", 1800.00, 3.0, "32mm kesim kapasitesi, 2 adet akü.", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"),
        ("Motorlu Tırpan", "Tarım Makineleri", 2200.00, 8.0, "52cc motor, çift başlık sistemi.", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"),
        ("Mini Çapa Makinesi", "Tarım Makineleri", 3800.00, 55.0, "6.5 HP benzinli motor, 80cm çalışma.", "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400"),
        ("Elektrikli İlaçlama Pompası", "Tarım Makineleri", 850.00, 8.0, "16L tank, şarjlı, sırt tipi.", "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=400"),
        ("Motorlu Pülverizatör 100L", "Tarım Makineleri", 5500.00, 65.0, "El arabası tipi, benzinli motor.", "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400"),
        ("Zeytin Hasat Makinesi", "Tarım Makineleri", 2800.00, 5.0, "Titreşimli başlık, uzun sap.", "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"),
        ("Toprak Burgusu Makinesi", "Tarım Makineleri", 1950.00, 15.0, "52cc motor, 150mm ve 200mm uçlar.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400"),
        ("Çim Havalandırma Makinesi", "Tarım Makineleri", 3200.00, 40.0, "Benzinli, 40cm çalışma genişliği.", "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400"),
        ("Yaprak Toplama Makinesi", "Tarım Makineleri", 1600.00, 6.0, "Benzinli üfleme/emme fonksiyonu.", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=400"),
        ("Motorlu Testere 45cm", "Tarım Makineleri", 2400.00, 7.0, "52cc motor, profesyonel kullanım.", "https://images.unsplash.com/photo-1592502712628-162b0f3c1c4d?w=400"),
        ("Dal Öğütme Makinesi", "Tarım Makineleri", 8500.00, 120.0, "15 HP motor, 10cm dal kapasitesi.", "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=400"),
        ("Çit Kesme Makinesi Akülü", "Tarım Makineleri", 1400.00, 4.0, "60cm bıçak, çift taraflı kesim.", "https://images.unsplash.com/photo-1595841696677-6489ff3f8cd1?w=400"),
        ("Kompresör 50L Taşınabilir", "Tarım Makineleri", 2100.00, 35.0, "2.5 HP motor, ilaçlama için.", "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400"),
        ("Jeneratör 3000W", "Tarım Makineleri", 4800.00, 45.0, "Benzinli, sera aydınlatma için.", "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=400"),
    ]
    
    all_products = []
    category_map = {cat.name: cat.id for cat in categories}
    
    for name, cat_name, price, desi, desc, image_url in heavy_products:
        seller = random.choice(approved_sellers)
        stock = random.choice([0, 5, 10, 25, 50, 100, 500])
        product = Product(
            seller_id=seller.id,
            category_id=category_map[cat_name],
            name=name,
            description=desc,
            price=price,
            stock=stock,
            desi=desi,
            image_url=image_url,
            rating=round(random.uniform(3.5, 5.0), 1)
        )
        db.session.add(product)
        all_products.append(product)
    
    for name, cat_name, price, desi, desc, image_url in light_products:
        seller = random.choice(approved_sellers)
        stock = random.choice([0, 10, 50, 100, 200, 500, 1000])
        product = Product(
            seller_id=seller.id,
            category_id=category_map[cat_name],
            name=name,
            description=desc,
            price=price,
            stock=stock,
            desi=desi,
            image_url=image_url,
            rating=round(random.uniform(3.5, 5.0), 1)
        )
        db.session.add(product)
        all_products.append(product)
    
    for name, cat_name, price, desi, desc, image_url in machinery_products:
        seller = random.choice(approved_sellers)
        stock = random.choice([0, 3, 5, 10, 15, 20])
        product = Product(
            seller_id=seller.id,
            category_id=category_map[cat_name],
            name=name,
            description=desc,
            price=price,
            stock=stock,
            desi=desi,
            image_url=image_url,
            rating=round(random.uniform(3.5, 5.0), 1)
        )
        db.session.add(product)
        all_products.append(product)
    
    db.session.flush()
    
    # ============================================================================
    # 5. SİPARİŞLER (Ana alıcı için geçmiş siparişler)
    # ============================================================================
    
    order_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'delivered', 'delivered']
    shipping_methods = ['Kargo Entegrasyonu', 'Ambar/Nakliye']
    
    addresses = [
        "Atatürk Mah. Çiftlik Sok. No:15, Antalya",
        "Cumhuriyet Cad. No:42/A, İzmir",
        "Tarım Köyü, Sera Yolu No:8, Mersin",
        "Organize Sanayi Bölgesi 5. Cadde, Konya"
    ]
    
    for i in range(8):
        order_products = random.sample(all_products, random.randint(1, 5))
        total_price = 0
        total_desi = 0
        
        order = Order(
            buyer_id=buyer.id,
            total_price=0,
            total_desi=0,
            status=random.choice(order_statuses),
            shipping_method='',
            shipping_address=random.choice(addresses),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.session.add(order)
        db.session.flush()
        
        for prod in order_products:
            qty = random.randint(1, 3)
            item_desi = prod.desi * qty
            item_price = prod.price * qty
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                quantity=qty,
                price=item_price,
                desi=item_desi
            )
            db.session.add(order_item)
            
            total_price += item_price
            total_desi += item_desi
        
        order.total_price = total_price
        order.total_desi = total_desi
        order.shipping_method = 'Ambar/Nakliye' if total_desi >= 30 else 'Kargo Entegrasyonu'
    
    db.session.flush()
    
    # ============================================================================
    # 6. YORUMLAR (Farklı ürünlere 1-5 yıldız)
    # ============================================================================
    
    review_comments_positive = [
        "Hızlı kargo, teşekkürler.",
        "Ürün beklediğimden kaliteli çıktı.",
        "Paketleme çok özenliydi.",
        "Fiyat performans ürünü, tavsiye ederim.",
        "Satıcı çok ilgili, sorularıma hemen cevap verdi.",
        "İkinci siparişim, yine memnun kaldım.",
        "Sera için tam ihtiyacım olan ürün.",
        "Kaliteli malzeme, sağlam paketleme.",
    ]
    
    review_comments_neutral = [
        "Fiyatına göre idare eder.",
        "Ortalama bir ürün.",
        "Beklentilerimi karşıladı.",
        "Normal, fena değil.",
    ]
    
    review_comments_negative = [
        "Kargo biraz gecikti.",
        "Ürün fotoğraftakinden farklı.",
        "Daha iyi olabilirdi.",
    ]
    
    reviewed_products = random.sample(all_products, min(40, len(all_products)))
    
    for product in reviewed_products:
        num_reviews = random.randint(1, 5)
        reviewers = random.sample(all_buyers, min(num_reviews, len(all_buyers)))
        
        for reviewer in reviewers:
            stars = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 10, 35, 45])[0]
            
            if stars >= 4:
                comment = random.choice(review_comments_positive)
            elif stars == 3:
                comment = random.choice(review_comments_neutral)
            else:
                comment = random.choice(review_comments_negative)
            
            review = Review(
                product_id=product.id,
                user_id=reviewer.id,
                comment=comment,
                stars=stars,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.session.add(review)
        
        product.update_rating()
    
    db.session.commit()
    
    # ============================================================================
    # ÖZET
    # ============================================================================
    
    total_users = User.query.count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_buyers = User.query.filter_by(role='buyer').count()
    approved_seller_count = User.query.filter_by(role='seller', is_seller_approved=True).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_reviews = Review.query.count()
    heavy_count = Product.query.filter(Product.desi >= 30).count()
    light_count = Product.query.filter(Product.desi < 30).count()
    
    print("\n" + "="*60)
    print("✅ DEMO ORTAMI BAŞARIYLA OLUŞTURULDU!")
    print("="*60)
    print("\n📋 TANIMLI HESAPLAR:")
    print("-"*40)
    print("  🔑 Yönetici:")
    print("     Email: admin@tarimpazari.com")
    print("     Şifre: Admin123!")
    print()
    print("  🏪 Onaylı Satıcı (Büyük Envanter):")
    print("     Email: satici@tarimpazari.com")
    print("     Şifre: Satici123!")
    print("     Firma: Antalya Sera Market")
    print()
    print("  ⏳ Onaysız Satıcı (Yeni):")
    print("     Email: yeni@tarimpazari.com")
    print("     Şifre: Satici123!")
    print("     Firma: Yeni Çiftçi Ltd")
    print()
    print("  🛒 Alıcı (Sık Alışveriş Yapan):")
    print("     Email: alici@tarimpazari.com")
    print("     Şifre: Alici123!")
    print()
    print("-"*40)
    print(f"\n📊 İSTATİSTİKLER:")
    print(f"  👥 Toplam Kullanıcı: {total_users}")
    print(f"     - Satıcılar: {total_sellers} ({approved_seller_count} onaylı)")
    print(f"     - Alıcılar: {total_buyers}")
    print(f"  📦 Toplam Ürün: {total_products}")
    print(f"     - Ağır (≥30 Desi): {heavy_count} (Ambar/Nakliye)")
    print(f"     - Hafif (<30 Desi): {light_count} (Kargo)")
    print(f"  📋 Toplam Sipariş: {total_orders}")
    print(f"  ⭐ Toplam Yorum: {total_reviews}")
    print("="*60 + "\n")


if __name__ == '__main__':
    from app import app, db
    
    with app.app_context():
        seed_database(drop_all=True)
