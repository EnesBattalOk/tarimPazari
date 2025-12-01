import random
from models import User, Category, Product, Review
from werkzeug.security import generate_password_hash

def seed_database(db):
    """
    Veritabanını başlangıç verileriyle doldurur.
    """
    
    if User.query.first():
        print("Veritabanı zaten dolu, seed işlemi atlanıyor.")
        return
    
    # Create 3 test users with specific emails
    admin = User(
        username='admin',
        email='admin@tarimpazari.com',
        password_hash=generate_password_hash('Admin123!'),
        role='admin',
        is_seller_approved=True
    )
    db.session.add(admin)
    
    seller_approved = User(
        username='satici',
        email='satici@tarimpazari.com',
        password_hash=generate_password_hash('Satici123!'),
        role='seller',
        is_seller_approved=True,
        company_name='Antalya Sera Market'
    )
    db.session.add(seller_approved)
    
    seller_pending = User(
        username='yenisatici',
        email='yeni@tarimpazari.com',
        password_hash=generate_password_hash('Satici123!'),
        role='seller',
        is_seller_approved=False,
        company_name='Yeni Çiftlik Ltd'
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
    
    # Create categories
    categories = [
        Category(name='Sera Malzemeleri', icon_class='fa-warehouse'),
        Category(name='Gübre', icon_class='fa-seedling'),
        Category(name='Sulama', icon_class='fa-tint'),
        Category(name='Tohum', icon_class='fa-leaf'),
        Category(name='Zirai İlaç', icon_class='fa-spray-can'),
        Category(name='Tarım Makineleri', icon_class='fa-tractor'),
    ]
    
    for cat in categories:
        db.session.add(cat)
    
    db.session.flush()
    
    # Create products from approved seller only
    products = [
        Product(
            seller_id=seller_approved.id,
            category_id=1,
            name='Sera Naylonu (Ağır)',
            description='Yüksek kaliteli UV dayanımlı sera naylonu. 8 metre genişlik, 50 metre uzunluk.',
            price=2500.00,
            stock=50,
            desi=50.0,
            image_url='https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400',
            rating=4.5
        ),
        Product(
            seller_id=seller_approved.id,
            category_id=4,
            name='Domates Tohumu',
            description='Organik sertifikalı domates tohumu. 100 adet tohum içerir.',
            price=45.00,
            stock=200,
            desi=1.0,
            image_url='https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400',
            rating=4.8
        ),
        Product(
            seller_id=seller_approved.id,
            category_id=2,
            name='Organik Solucan Gübresi 25kg',
            description='%100 doğal solucan gübresi. Tüm bitkiler için uygundur.',
            price=180.00,
            stock=100,
            desi=28.0,
            image_url='https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400',
            rating=4.6
        ),
        Product(
            seller_id=seller_approved.id,
            category_id=3,
            name='Damlama Sulama Seti',
            description='Profesyonel damlama sulama sistemi. 1000 m² alan için yeterli.',
            price=850.00,
            stock=30,
            desi=15.0,
            image_url='https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=400',
            rating=4.3
        ),
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.flush()
    
    # Add reviews from buyer
    review_comments = [
        "Hızlı kargo, teşekkürler.",
        "Ürün beklediğimden kaliteli çıktı.",
        "Paketleme çok özenliydi.",
        "Fiyat performans ürünü.",
        "Tavsiye ederim, kaliteli ürün.",
    ]
    
    review_count = 0
    for product in products:
        stars = random.choice([4, 5, 5])
        comment = random.choice(review_comments)
        
        review = Review(
            product_id=product.id,
            user_id=buyer.id,
            comment=comment,
            stars=stars
        )
        db.session.add(review)
        review_count += 1
    
    db.session.commit()
    
    print("\n✅ Başlangıç verileri başarıyla eklendi:")
    print("  📋 Test Kullanıcıları:")
    print("     - admin@tarimpazari.com / Admin123!")
    print("     - satici@tarimpazari.com / Satici123! (Onaylı Satıcı)")
    print("     - yeni@tarimpazari.com / Satici123! (Onaysız Satıcı)")
    print("     - alici@tarimpazari.com / Alici123! (Alıcı)")
    print(f"  📁 {len(categories)} Kategori")
    print(f"  📦 {len(products)} Ürün")
    print(f"  ⭐ {review_count} Yorum")
    print("\n✨ Giriş Yap:\n")
