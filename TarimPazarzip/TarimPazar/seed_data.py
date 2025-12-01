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
    ]
    
    for cat in categories:
        db.session.add(cat)
    
    db.session.flush()
    
    # ============================================================================
    # 4. ÜRÜNLER (60+ Ürün - %50 Ağır, %50 Hafif)
    # ============================================================================
    
    heavy_products = [
        ("Galvanizli Sera Profili 6m", "Sera Malzemeleri", 850.00, 45.0, "Yüksek kaliteli galvanizli çelik profil. 6 metre uzunluk, korozyona dayanıklı."),
        ("Demir Sera Direği Set", "Sera Malzemeleri", 1200.00, 55.0, "10 adet 3m demir direk seti. Montaj aksesuarları dahil."),
        ("Sera Naylonu Rulo 100m", "Sera Malzemeleri", 2800.00, 40.0, "UV filtreli, 8m genişlik, 100m uzunluk sera örtüsü."),
        ("Alüminyum Sera Çatı Sistemi", "Sera Malzemeleri", 4500.00, 65.0, "Komple çatı sistemi, 50m² alan için yeterli."),
        ("Polikarbon Sera Paneli 10'lu", "Sera Malzemeleri", 3200.00, 48.0, "4mm kalınlık, UV korumalı, 10 adet panel."),
        ("Sera Havalandırma Motoru", "Sera Malzemeleri", 1800.00, 35.0, "Otomatik açılır kapanır pencere sistemi."),
        ("Çelik Sera İskeleti Komple", "Sera Malzemeleri", 8500.00, 120.0, "100m² sera için komple iskelet sistemi."),
        ("Tonluk Organik Gübre", "Gübre", 2500.00, 100.0, "1000kg organik kompost gübre. Tüm bitkiler için."),
        ("Hayvan Gübresi 500kg", "Gübre", 1200.00, 60.0, "Fermente edilmiş büyükbaş gübresi."),
        ("Solucan Gübresi 250kg", "Gübre", 1800.00, 35.0, "Premium kalite solucan humusu."),
        ("Kimyasal Gübre Paket 200kg", "Gübre", 950.00, 32.0, "NPK 15-15-15 granül gübre."),
        ("Organik Kompost 300kg", "Gübre", 680.00, 38.0, "Bitkisel atıklardan üretilmiş kompost."),
        ("Tavuk Gübresi 400kg", "Gübre", 520.00, 50.0, "Kurutulmuş ve işlenmiş tavuk gübresi."),
        ("Deniz Yosunu Gübresi 100kg", "Gübre", 1400.00, 33.0, "Doğal deniz yosunu özütü, sıvı konsantre."),
        ("Endüstriyel Sulama Pompası", "Sulama", 3500.00, 45.0, "5.5 HP dizel motor, yüksek basınç."),
        ("Sulama Borusu 1000m", "Sulama", 2200.00, 80.0, "32mm PE boru, 1000 metre rulo."),
        ("Büyük Sulama Tankı 5000L", "Sulama", 4800.00, 150.0, "Polyester su deposu, UV dayanımlı."),
        ("Merkezi Sulama Sistemi", "Sulama", 6500.00, 95.0, "Otomatik programlanabilir sistem, 1 hektar."),
        ("Yağmurlama Sistemi Pro", "Sulama", 2800.00, 42.0, "360° döner başlıklar, 50 adet set."),
        ("Derin Kuyu Pompası", "Sulama", 4200.00, 55.0, "Paslanmaz çelik, 100m derinlik kapasitesi."),
        ("Filtre Sistemi Endüstriyel", "Sulama", 1900.00, 38.0, "Disk filtre, otomatik yıkamalı."),
        ("Damlama Sistemi 5 Hektar", "Sulama", 8500.00, 110.0, "Komple damlama sulama paketi."),
        ("Tohum Serpme Makinesi", "Tohum", 2400.00, 65.0, "Traktör arkası, ayarlanabilir serpme."),
        ("Endüstriyel Tohum Kurutma", "Sera Malzemeleri", 5500.00, 85.0, "Elektrikli tohum kurutma makinesi."),
        ("Sera Isıtma Kazanı", "Sera Malzemeleri", 7200.00, 130.0, "Kömür/odun yakıtlı, 500m² ısıtma."),
        ("Otomatik Sulama Kontrol Ünitesi", "Sulama", 3100.00, 40.0, "IoT destekli akıllı sulama sistemi."),
        ("Gübre Karıştırma Tankı", "Gübre", 2600.00, 75.0, "1000L kapasiteli, motorlu karıştırıcı."),
        ("Sera Gölgeleme Sistemi", "Sera Malzemeleri", 1950.00, 52.0, "%50 gölgeleme, 500m² alan için."),
        ("Profesyonel Sera Fanı", "Sera Malzemeleri", 1100.00, 32.0, "Yüksek debili havalandırma fanı."),
        ("Toprak İşleme Seti Pro", "Sera Malzemeleri", 890.00, 35.0, "Profesyonel bahçe aletleri seti."),
    ]
    
    light_products = [
        ("Domates Tohumu Premium", "Tohum", 45.00, 0.5, "Organik sertifikalı, 100 adet tohum."),
        ("Biber Tohumu Karışık", "Tohum", 38.00, 0.3, "5 farklı çeşit biber tohumu, 50'şer adet."),
        ("Salatalık Tohumu", "Tohum", 32.00, 0.4, "Kornişon salatalık, 80 adet tohum."),
        ("Patlıcan Tohumu", "Tohum", 42.00, 0.3, "Kemer patlıcan, 60 adet tohum."),
        ("Marul Tohumu Mix", "Tohum", 28.00, 0.2, "4 çeşit marul, toplam 200 tohum."),
        ("Fasulye Tohumu", "Tohum", 55.00, 1.0, "Ayşe kadın fasulye, 500g paket."),
        ("Kabak Tohumu", "Tohum", 35.00, 0.5, "Sakız kabağı, 30 adet tohum."),
        ("Havuç Tohumu", "Tohum", 25.00, 0.2, "Nantes havuç, 500 adet tohum."),
        ("Soğan Tohumu", "Tohum", 40.00, 0.3, "Kırmızı soğan, 300 adet tohum."),
        ("Ispanak Tohumu", "Tohum", 22.00, 0.2, "Bölgeye uygun çeşit, 400 tohum."),
        ("Bahçe Makası Pro", "Sera Malzemeleri", 85.00, 0.8, "Paslanmaz çelik, ergonomik sap."),
        ("Budama Makası", "Sera Malzemeleri", 120.00, 0.6, "Profesyonel dal kesme makası."),
        ("El Çapası", "Sera Malzemeleri", 45.00, 1.2, "Çelik başlık, ahşap sap."),
        ("Bahçe Eldiveni 5'li", "Sera Malzemeleri", 65.00, 0.5, "Su geçirmez, dikenli iş için."),
        ("Toprak pH Ölçer", "Sera Malzemeleri", 180.00, 0.3, "Dijital ekran, anlık ölçüm."),
        ("Nem Ölçer Dijital", "Sera Malzemeleri", 95.00, 0.2, "Toprak nem sensörü."),
        ("Bitki Etiketi 100'lü", "Sera Malzemeleri", 35.00, 0.4, "Plastik, yazılabilir etiket."),
        ("Fide Tepsisi 50 Gözlü", "Sera Malzemeleri", 28.00, 0.8, "Sert plastik, tekrar kullanılabilir."),
        ("Saksı 5L 10'lu Paket", "Sera Malzemeleri", 55.00, 2.0, "Drenaj delikli plastik saksı."),
        ("Sera İpi 500m", "Sera Malzemeleri", 45.00, 1.5, "Dayanıklı PP ip, yeşil renk."),
        ("Sıvı Gübre 5L", "Gübre", 120.00, 6.0, "Yaprak gübresi, tüm bitkiler için."),
        ("Organik Sıvı Gübre 2L", "Gübre", 85.00, 2.5, "Deniz yosunu özlü, organik."),
        ("Mikro Besin Seti", "Gübre", 145.00, 1.0, "Demir, çinko, mangan karışımı."),
        ("Kök Güçlendirici", "Gübre", 95.00, 0.8, "Köklendirme hormonu, 250ml."),
        ("Yaprak Parlatıcı", "Gübre", 55.00, 0.5, "Doğal yaprak bakım spreyi."),
        ("Mini Damlama Seti", "Sulama", 185.00, 3.0, "Balkon/teras için, 20 saksı kapasiteli."),
        ("Bahçe Hortumu 25m", "Sulama", 220.00, 5.0, "Örgülü, bükülmez hortum."),
        ("Sulama Tabancası Pro", "Sulama", 75.00, 0.4, "7 fonksiyonlu, metal gövde."),
        ("Sprinkler Başlığı 5'li", "Sulama", 65.00, 0.6, "Ayarlanabilir açı, plastik."),
        ("Damla Sulama Aparatı 50'li", "Sulama", 95.00, 1.0, "Ayarlanabilir damlatıcı."),
    ]
    
    all_products = []
    category_map = {cat.name: cat.id for cat in categories}
    
    for name, cat_name, price, desi, desc in heavy_products:
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
            image_url=f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=400',
            rating=round(random.uniform(3.5, 5.0), 1)
        )
        db.session.add(product)
        all_products.append(product)
    
    for name, cat_name, price, desi, desc in light_products:
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
            image_url=f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=400',
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
