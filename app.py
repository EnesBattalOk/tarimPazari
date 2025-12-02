import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Category, Product, Order, OrderItem, Review, CartItem, ProductQuestion, Wishlist
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__, instance_path='/tmp')
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'tarim-pazari-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarim_pazari.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Upload Folder for Document Verification
UPLOAD_FOLDER = 'TarimPazar/static/uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# VERCEL_ICIN_IPTAL: os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

# ============================================================================
# HİBRİT LOJİSTİK ALGORİTMASI
# ============================================================================
# Bu fonksiyon sepetteki ürünlerin toplam Desi değerini hesaplar ve
# buna göre kargo yöntemini belirler.
# 
# KURAL 1: Toplam Desi < 30 ise -> "Kargo Entegrasyonu" (standart kargo)
# KURAL 2: Toplam Desi >= 30 ise -> "Ambar/Nakliye" (büyük yük taşımacılığı)
# ============================================================================

def calculate_shipping_method(total_desi):
    """
    Hibrit Lojistik Algoritması
    
    Desi (hacimsel ağırlık) değerine göre gönderim yöntemini belirler.
    
    Args:
        total_desi (float): Sepetteki tüm ürünlerin toplam desi değeri
    
    Returns:
        str: Gönderim yöntemi - "Kargo Entegrasyonu" veya "Ambar/Nakliye"
    """
    DESI_THRESHOLD = 30  # Eşik değeri
    
    if total_desi < DESI_THRESHOLD:
        return "Kargo Entegrasyonu"
    else:
        return "Ambar/Nakliye"


def get_shipping_info(total_desi):
    """
    Gönderim bilgilerini detaylı olarak döndürür.
    
    Args:
        total_desi (float): Toplam desi değeri
    
    Returns:
        dict: Gönderim yöntemi, ikon ve açıklama bilgileri
    """
    method = calculate_shipping_method(total_desi)
    
    if method == "Kargo Entegrasyonu":
        return {
            'method': method,
            'icon': 'fa-truck',
            'description': 'Standart kargo ile gönderilecektir.',
            'color': 'success'
        }
    else:
        return {
            'method': method,
            'icon': 'fa-warehouse',
            'description': 'Ambar/Nakliye ile gönderilecektir.',
            'color': 'warning'
        }


# ============================================================================
# YARDIMCI FONKSİYONLAR VE DEKORATÖRLERİ
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'seller':
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_cart_count():
    if 'user_id' in session:
        return CartItem.query.filter_by(user_id=session['user_id']).count()
    return 0


def get_cart_total():
    if 'user_id' in session:
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
        total_desi = sum(item.product.desi * item.quantity for item in cart_items)
        return {'total': total, 'total_desi': total_desi, 'count': len(cart_items)}
    return {'total': 0, 'total_desi': 0, 'count': 0}


@app.context_processor
def inject_cart():
    
    # --- VERCEL KURTARMA MODU ---
    try:
        # Kategorileri çekmeyi dene
        cats = Category.query.all()
    except Exception:
        # Eğer tablo yoksa hata verme, hemen oluştur!
        try:
            with app.app_context():
                db.create_all()
                # Opsiyonel: Boş kalmasın diye varsayılan kategori ekle
                if not Category.query.first():
                    ornek = Category(name="Genel", slug="genel", icon_class="fa-leaf")
                    db.session.add(ornek)
                    db.session.commit()
            cats = Category.query.all()
        except:
            cats = [] # Yine de olmazsa boş liste dön ama ÇÖKME
            
    return dict(cart_info=get_cart_total(), categories=cats)
    # ---------------------------



# ============================================================================
# ANA SAYFA VE ÜRÜN ROUTE'LARI
# ============================================================================

@app.route('/')
def index():
    categories = Category.query.all()
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    user = User.query.get(session.get('user_id')) if session.get('user_id') else None
    wishlist_product_ids = [w.product_id for w in user.wishlist_items] if user else []
    return render_template('index.html', categories=categories, products=featured_products, user=user, wishlist_product_ids=wishlist_product_ids)


@app.route('/products')
def products():
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.all()
    categories = Category.query.all()
    user = User.query.get(session.get('user_id')) if session.get('user_id') else None
    wishlist_product_ids = [w.product_id for w in user.wishlist_items] if user else []
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         user=user,
                         wishlist_product_ids=wishlist_product_ids,
                         selected_category=category_id,
                         min_price=min_price,
                         max_price=max_price,
                         search=search,
                         sort=sort)


@app.route('/wishlist')
@login_required
def wishlist():
    user = User.query.get(session['user_id'])
    wishlist_items = Wishlist.query.filter_by(user_id=session['user_id']).all()
    products = [item.product for item in wishlist_items]
    return render_template('wishlist.html', products=products, user=user)


@app.route('/wishlist/add/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_to_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session['user_id']
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'action': 'removed'})
        flash('Favorilerden çıkarıldı.', 'warning')
    else:
        wishlist = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(wishlist)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'action': 'added'})
        flash('Favorilere eklendi.', 'success')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    shipping_info = get_shipping_info(product.desi)
    
    return render_template('product_detail.html', 
                         product=product, 
                         related_products=related_products,
                         shipping_info=shipping_info)


# ============================================================================
# KİMLİK DOĞRULAMA ROUTE'LARI
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Hoş geldiniz, {user.username}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'seller':
                return redirect(url_for('seller_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('E-posta veya şifre hatalı.', 'danger')
    
    admins = User.query.filter_by(role='admin').all()
    approved_sellers = User.query.filter_by(role='seller', is_seller_approved=True).all()
    pending_sellers = User.query.filter_by(role='seller', is_seller_approved=False).all()
    buyers = User.query.filter_by(role='buyer').all()
    
    return render_template('login.html', 
                          admins=admins,
                          approved_sellers=approved_sellers,
                          pending_sellers=pending_sellers,
                          buyers=buyers)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'buyer')
        company_name = request.form.get('company_name', '')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kayıtlı.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            role=role,
            company_name=company_name if role == 'seller' else None,
            is_seller_approved=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        if role == 'seller':
            flash('Kayıt başarılı! Satıcı hesabınız admin onayı bekliyor.', 'info')
        else:
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('index'))


# ============================================================================
# SEPET ROUTE'LARI
# ============================================================================

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_desi = sum(item.product.desi * item.quantity for item in cart_items)
    
    shipping_info = get_shipping_info(total_desi)
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total_price=total_price,
                         total_desi=total_desi,
                         shipping_info=shipping_info)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity > product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Yeterli stok yok.'})
        flash('Yeterli stok yok.', 'danger')
        return redirect(url_for('product_detail', id=product_id))
    
    cart_item = CartItem.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_info = get_cart_total()
        return jsonify({
            'success': True, 
            'message': 'Ürün sepete eklendi.',
            'cart_count': cart_info['count']
        })
    
    flash('Ürün sepete eklendi.', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Yetkisiz işlem.'})
    
    quantity = request.form.get('quantity', type=int)
    
    if quantity <= 0:
        db.session.delete(cart_item)
    elif quantity > cart_item.product.stock:
        return jsonify({'success': False, 'message': 'Yeterli stok yok.'})
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    
    cart_info = get_cart_total()
    shipping_info = get_shipping_info(cart_info['total_desi'])
    
    return jsonify({
        'success': True,
        'total': cart_info['total'],
        'total_desi': cart_info['total_desi'],
        'cart_count': cart_info['count'],
        'shipping_method': shipping_info['method'],
        'shipping_icon': shipping_info['icon'],
        'shipping_color': shipping_info['color']
    })


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Yetkisiz işlem.'})
    
    db.session.delete(cart_item)
    db.session.commit()
    
    cart_info = get_cart_total()
    shipping_info = get_shipping_info(cart_info['total_desi'])
    
    return jsonify({
        'success': True,
        'message': 'Ürün sepetten kaldırıldı.',
        'total': cart_info['total'],
        'total_desi': cart_info['total_desi'],
        'cart_count': cart_info['count'],
        'shipping_method': shipping_info['method'],
        'shipping_icon': shipping_info['icon'],
        'shipping_color': shipping_info['color']
    })


@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(buyer_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = Order.query.get_or_404(id)
    if order.buyer_id != session['user_id'] and session.get('role') != 'admin':
        flash('Bu siparişi görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('orders'))
    return render_template('order_detail.html', order=order)


# ============================================================================
# YORUM ROUTE'LARI
# ============================================================================

@app.route('/product/<int:product_id>/question', methods=['POST'])
@login_required
def ask_question(product_id):
    product = Product.query.get_or_404(product_id)
    question_text = request.form.get('question_text')
    
    question = ProductQuestion(
        product_id=product_id,
        user_id=session['user_id'],
        question_text=question_text
    )
    db.session.add(question)
    db.session.commit()
    
    flash('Sorunuz satıcıya gönderildi.', 'success')
    return redirect(url_for('product_detail', id=product_id))


@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    
    existing_review = Review.query.filter_by(
        product_id=product_id,
        user_id=session['user_id']
    ).first()
    
    if existing_review:
        flash('Bu ürüne zaten yorum yaptınız.', 'warning')
        return redirect(url_for('product_detail', id=product_id))
    
    comment = request.form.get('comment')
    stars = request.form.get('stars', 5, type=int)
    
    review = Review(
        product_id=product_id,
        user_id=session['user_id'],
        comment=comment,
        stars=stars
    )
    db.session.add(review)
    
    product.update_rating()
    db.session.commit()
    
    flash('Yorumunuz eklendi.', 'success')
    return redirect(url_for('product_detail', id=product_id))


# ============================================================================
# SATICI DOĞRULAMA VE EVRAKLARİ (VERIFICATION SYSTEM)
# ============================================================================

@app.route('/seller/verify', methods=['GET', 'POST'])
@login_required
def seller_verify():
    user = User.query.get(session['user_id'])
    if user.role != 'seller':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user.tax_number = request.form.get('tax_number')
        user.tax_office = request.form.get('tax_office')
        
        # File Upload Logic
        file_fields = [
            ('document_tax_plate', 'tax_plate'), 
            ('document_signature', 'signature'),
            ('document_registry', 'registry'),
            ('document_agriculture', 'agriculture')
        ]
        
        for field_name, suffix in file_fields:
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename != '':
                    filename = secure_filename(f"seller_{user.id}_{suffix}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    setattr(user, field_name, f'/static/uploads/documents/{filename}')
        
        db.session.commit()
        flash('Evraklarınız başarıyla yüklendi. Yönetici onayı bekleniyor.', 'success')
        return redirect(url_for('seller_dashboard'))
    
    pending_questions_count = 0
    return render_template('seller/verify.html', user=user, pending_questions_count=pending_questions_count)


@app.route('/admin/pending-sellers')
@admin_required
def pending_sellers():
    sellers = User.query.filter_by(role='seller', is_seller_approved=False).all()
    return render_template('admin/pending_sellers.html', pending_sellers=sellers)


@app.route('/admin/approve-seller/<int:user_id>', methods=['POST'])
@admin_required
def approve_seller(user_id):
    user = User.query.get_or_404(user_id)
    user.is_seller_approved = True
    db.session.commit()
    flash(f'{user.company_name or user.username} başarıyla onaylandı!', 'success')
    return redirect(url_for('pending_sellers'))


@app.route('/admin/reject-seller/<int:user_id>', methods=['POST'])
@admin_required
def reject_seller(user_id):
    user = User.query.get_or_404(user_id)
    user.is_seller_approved = False
    user.tax_number = None
    user.tax_office = None
    user.document_tax_plate = None
    user.document_signature = None
    user.document_registry = None
    user.document_agriculture = None
    db.session.commit()
    flash(f'{user.company_name or user.username} reddedildi.', 'warning')
    return redirect(url_for('pending_sellers'))


# ============================================================================
# SATICI PANELİ ROUTE'LARI
# ============================================================================

@app.route('/seller/dashboard')
@seller_required
def seller_dashboard():
    user = User.query.get(session['user_id'])
    products = Product.query.filter_by(seller_id=session['user_id']).all()
    orders = Order.query.join(OrderItem).join(Product).filter(
        Product.seller_id == session['user_id']
    ).distinct().order_by(Order.created_at.desc()).all()
    
    pending_questions_count = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).count()
    
    return render_template('seller/dashboard.html', 
                         user=user, 
                         products=products, 
                         orders=orders,
                         pending_questions_count=pending_questions_count)


@app.route('/seller/products')
@seller_required
def seller_products():
    user = User.query.get(session['user_id'])
    products = Product.query.filter_by(seller_id=session['user_id']).all()
    pending_questions_count = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).count()
    return render_template('seller/products.html', user=user, products=products, pending_questions_count=pending_questions_count)


@app.route('/seller/product/add', methods=['GET', 'POST'])
@seller_required
def add_product():
    user = User.query.get(session['user_id'])
    
    # SECURITY CHECK: Block unapproved sellers from adding products
    if not user.is_seller_approved:
        flash('Ürün ekleyebilmek için önce hesabınızın onaylanması gerekmektedir.', 'danger')
        return redirect(url_for('seller_verify'))
    
    if request.method == 'POST':
        product = Product(
            seller_id=session['user_id'],
            category_id=request.form.get('category_id', type=int),
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price', type=float),
            stock=request.form.get('stock', type=int),
            desi=request.form.get('desi', type=float),
            image_url=request.form.get('image_url', '')
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Ürün başarıyla eklendi.', 'success')
        return redirect(url_for('seller_products'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    pending_questions_count = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).count()
    return render_template('seller/add_product.html', user=user, categories=categories, pending_questions_count=pending_questions_count)


@app.route('/seller/product/edit/<int:id>', methods=['GET', 'POST'])
@seller_required
def edit_product(id):
    user = User.query.get(session['user_id'])
    
    # SECURITY CHECK: Block unapproved sellers from editing products
    if not user.is_seller_approved:
        flash('Ürün düzenleyebilmek için önce hesabınızın onaylanması gerekmektedir.', 'danger')
        return redirect(url_for('seller_verify'))
    
    product = Product.query.get_or_404(id)
    
    if product.seller_id != session['user_id']:
        flash('Bu ürünü düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('seller_products'))
    
    if request.method == 'POST':
        product.category_id = request.form.get('category_id', type=int)
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price', type=float)
        product.stock = request.form.get('stock', type=int)
        product.desi = request.form.get('desi', type=float)
        product.image_url = request.form.get('image_url', '')
        product.is_active = 'is_active' in request.form
        
        db.session.commit()
        
        flash('Ürün başarıyla güncellendi.', 'success')
        return redirect(url_for('seller_products'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    pending_questions_count = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).count()
    return render_template('seller/edit_product.html', user=user, product=product, categories=categories, pending_questions_count=pending_questions_count)


@app.route('/seller/product/delete/<int:id>', methods=['POST'])
@seller_required
def delete_product(id):
    user = User.query.get(session['user_id'])
    
    # SECURITY CHECK: Block unapproved sellers from deleting products
    if not user.is_seller_approved:
        flash('Ürün silebilmek için önce hesabınızın onaylanması gerekmektedir.', 'danger')
        return redirect(url_for('seller_verify'))
    
    product = Product.query.get_or_404(id)
    
    if product.seller_id != session['user_id']:
        flash('Bu ürünü silme yetkiniz yok.', 'danger')
        return redirect(url_for('seller_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Ürün silindi.', 'success')
    return redirect(url_for('seller_products'))


@app.route('/seller/orders')
@seller_required
def seller_orders():
    user = User.query.get(session['user_id'])
    orders = Order.query.join(OrderItem).join(Product).filter(
        Product.seller_id == session['user_id']
    ).distinct().order_by(Order.created_at.desc()).all()
    pending_questions_count = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).count()
    
    return render_template('seller/orders.html', user=user, orders=orders, pending_questions_count=pending_questions_count)


@app.route('/seller/questions')
@seller_required
def seller_questions():
    user = User.query.get(session['user_id'])
    pending_questions = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.is_(None)
    ).order_by(ProductQuestion.created_at.desc()).all()
    
    answered_questions = ProductQuestion.query.join(Product).filter(
        Product.seller_id == session['user_id'],
        ProductQuestion.answer_text.isnot(None)
    ).order_by(ProductQuestion.answered_at.desc()).all()
    
    pending_questions_count = len(pending_questions)
    
    return render_template('seller/questions.html', 
                         user=user,
                         pending_questions=pending_questions,
                         answered_questions=answered_questions,
                         pending_questions_count=pending_questions_count)


@app.route('/seller/question/<int:id>/answer', methods=['POST'])
@seller_required
def answer_question(id):
    question = ProductQuestion.query.get_or_404(id)
    product = Product.query.get(question.product_id)
    
    if product.seller_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Yetki yok'}), 403
    
    answer_text = request.form.get('answer_text')
    question.answer_text = answer_text
    question.answered_at = datetime.utcnow()
    db.session.commit()
    
    flash('Cevap kaydedildi.', 'success')
    return redirect(url_for('seller_questions'))


# ============================================================================
# CHECKOUT & SIPARIŞ İŞLEMLERİ
# ============================================================================

@app.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    
    if not cart_items:
        flash('Sepetiniz boş.', 'warning')
        return redirect(url_for('index'))
    
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    total_desi = sum(item.product.desi * item.quantity for item in cart_items)
    shipping_info = get_shipping_info(total_desi)
    shipping_cost = 10.0 if total_desi < 30 else 50.0
    total_price = subtotal + shipping_cost
    
    return render_template('checkout.html',
                         cart_items=cart_items,
                         subtotal=subtotal,
                         total_desi=total_desi,
                         shipping_info=shipping_info,
                         shipping_cost=shipping_cost,
                         total_price=total_price)


@app.route('/confirm-order', methods=['POST'])
@login_required
def confirm_order():
    data = request.get_json()
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Sepet boş'}), 400
    
    try:
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        total_desi = sum(item.product.desi * item.quantity for item in cart_items)
        shipping_method = calculate_shipping_method(total_desi)
        
        shipping_address = f"{data.get('city', '')} / {data.get('district', '')}\n{data.get('address', '')}\nPosta Kodu: {data.get('zip_code', '')}"
        
        order = Order(
            buyer_id=session['user_id'],
            total_price=total_price,
            total_desi=total_desi,
            status='pending',
            shipping_method=shipping_method,
            shipping_address=shipping_address
        )
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
                desi=item.product.desi
            )
            db.session.add(order_item)
        
        CartItem.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'redirect_url': url_for('order_success', order_id=order.id)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.buyer_id != session['user_id']:
        flash('Bu siparişi görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order)


# ============================================================================
# ADMİN PANELİ ROUTE'LARI
# ============================================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    pending_sellers = User.query.filter_by(role='seller', is_seller_approved=False).all()
    all_users = User.query.all()
    all_products = Product.query.all()
    all_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    categories = Category.query.all()
    
    # Calculate KPIs
    total_sales = sum(order.total_price for order in Order.query.all() if order.status == 'delivered')
    approved_sellers = User.query.filter_by(role='seller', is_seller_approved=True).count()
    
    stats = {
        'total_users': len(all_users),
        'total_products': len(all_products),
        'total_orders': Order.query.count(),
        'total_sales': total_sales,
        'approved_sellers': approved_sellers,
        'pending_sellers': len(pending_sellers)
    }
    
    # Category distribution data for pie chart
    category_data = {}
    for cat in categories:
        category_data[cat.name] = len(cat.products)
    
    # Weekly sales data (mock data for demo)
    sales_data = {
        'Pazartesi': 3500,
        'Salı': 4200,
        'Çarşamba': 3800,
        'Perşembe': 5100,
        'Cuma': 6300,
        'Cumartesi': 7200,
        'Pazar': 4900
    }
    
    return render_template('admin/dashboard.html',
                         pending_sellers=pending_sellers,
                         users=all_users,
                         products=all_products,
                         orders=all_orders,
                         categories=categories,
                         stats=stats,
                         category_data=category_data,
                         sales_data=sales_data)


@app.route('/admin/category/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name')
    icon_class = request.form.get('icon_class', 'fa-leaf')
    
    if Category.query.filter_by(name=name).first():
        flash('Bu kategori zaten mevcut.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    category = Category(name=name, icon_class=icon_class)
    db.session.add(category)
    db.session.commit()
    
    flash('Kategori eklendi.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/category/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.products:
        flash('Bu kategoride ürünler var. Önce ürünleri taşıyın.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Kategori silindi.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================================
# YASAL SAYFA
# ============================================================================

@app.route('/legal')
def legal():
    categories = Category.query.all()
    tab = request.args.get('tab', 'privacy')
    
    return render_template('legal.html', 
                         categories=categories,
                         active_tab=tab)


# ============================================================================
# KURUMSAL SAYFALAR
# ============================================================================

@app.route('/corporate')
def corporate():
    categories = Category.query.all()
    tab = request.args.get('tab', 'about')
    
    return render_template('corporate.html', 
                         categories=categories,
                         active_tab=tab)


@app.route('/campaigns')
def campaigns():
    categories = Category.query.all()
    tab = request.args.get('tab', 'campaigns')
    
    return render_template('campaigns.html', 
                         categories=categories,
                         active_tab=tab)


@app.route('/seller-guide')
def seller_guide():
    categories = Category.query.all()
    
    return render_template('seller_guide.html', 
                         categories=categories)


@app.route('/help')
def help():
    categories = Category.query.all()
    
    return render_template('help.html', 
                         categories=categories)


@app.route('/about-us')
def about_us():
    categories = Category.query.all()
    
    return render_template('about_us.html', 
                         categories=categories)


@app.route('/security')
def security():
    categories = Category.query.all()
    
    return render_template('security.html', 
                         categories=categories)


@app.route('/contact')
def contact():
    categories = Category.query.all()
    
    return render_template('contact.html', 
                         categories=categories)


# ============================================================================
# VERİTABANI BAŞLATMA
# ============================================================================

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            from seed_data import seed_database
            seed_database(db)
            print("Veritabanı başlangıç verileriyle dolduruldu.")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)


# --- VERCEL ICIN TABLO OLUSTURMA ---
# Uygulama her calistiginda tablolarin varligini kontrol et ve yoksa olustur
with app.app_context():
    try:
        db.create_all()
        print("✅ Tablolar basariyla olusturuldu (Vercel /tmp).")
    except Exception as e:
        print(f"⚠️ Tablo olusturma hatasi: {e}")


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


# --- VERCEL ICIN OZEL KURTARICI FONKSIYON ---
def safe_get_categories():
    try:
        # Kategorileri çekmeyi dene
        return Category.query.all()
    except Exception:
        # Hata verirse (tablo yoksa), veritabanini olustur
        print("⚠️ Tablo bulunamadi, yeniden olusturuluyor...")
        with app.app_context():
            db.create_all()
            # Bos kalmasin diye ornek kategori ekle
            try:
                if not Category.query.first():
                    db.session.add(Category(name="Genel", slug="genel", icon_class="fa-leaf"))
                    db.session.commit()
            except:
                pass
        # Simdi tekrar dene, olmazsa bos liste don
        try:
            return Category.query.all()
        except:
            return []
# -------------------------------------------


# --- VERITABANI DOLDURMA ROTASI (VERCEL ICIN) ---
@app.route('/hazirla')
def veritabani_hazirla():
    try:
        from models import Category, Product
        from werkzeug.security import generate_password_hash
        
        # 1. Tablolari Garantile
        db.create_all()
        
        # 2. Kategorileri Ekle
        kategoriler = [
            {"name": "Meyve", "slug": "meyve", "icon_class": "fa-apple-alt"},
            {"name": "Sebze", "slug": "sebze", "icon_class": "fa-carrot"},
            {"name": "Tahıl & Bakliyat", "slug": "tahil", "icon_class": "fa-wheat"},
            {"name": "Süt & Kahvaltılık", "slug": "sut", "icon_class": "fa-cheese"},
            {"name": "Organik Ürünler", "slug": "organik", "icon_class": "fa-leaf"}
        ]
        
        eklenen_kat = 0
        for k in kategoriler:
            # Varsa ekleme, yoksa ekle
            if not Category.query.filter_by(slug=k['slug']).first():
                yeni = Category(name=k['name'], slug=k['slug'], icon_class=k['icon_class'])
                db.session.add(yeni)
                eklenen_kat += 1
        
        db.session.commit()
        
        return f'''
        <div style="font-family: sans-serif; padding: 50px; text-align: center; background: #d4edda; color: #155724;">
            <h1>✅ İşlem Tamam!</h1>
            <p>Veritabanı başarıyla oluşturuldu.</p>
            <p><strong>{eklenen_kat}</strong> adet kategori eklendi.</p>
            <br>
            <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Siteye Git</a>
        </div>
        '''
    except Exception as e:
        return f"<h1>Hata Oluştu:</h1><pre>{e}</pre>"
# -----------------------------------------------
