document.addEventListener('DOMContentLoaded', function() {
    initAddToCartForms();
    initQuantitySelectors();
    initCartOperations();
    initWishlistButtons();
    initTooltips();
    initPasswordValidation();
});

function initWishlistButtons() {
    $(document).on('click', '.wishlist-btn', function(e) {
        e.preventDefault();
        const btn = $(this);
        const productId = btn.data('product-id');
        const url = btn.attr('href');
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const icon = btn.find('i');
                if (data.action === 'added') {
                    btn.addClass('text-danger');
                    icon.removeClass('fa-regular').addClass('fa-solid');
                    showToast('Favorilere eklendi.', 'success');
                } else {
                    btn.removeClass('text-danger');
                    icon.removeClass('fa-solid').addClass('fa-regular');
                    showToast('Favorilerden çıkarıldı.', 'warning');
                }
            } else {
                showToast(data.message || 'Bir hata oluştu.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Bir hata oluştu.', 'danger');
        });
    });
}

function initAddToCartForms() {
    const forms = document.querySelectorAll('.add-to-cart-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.action;
            const button = this.querySelector('button[type="submit"]');
            
            if (!button) return;
            
            if (button.disabled) {
                showToast('Sepete eklemek için giriş yapmalısınız.', 'warning');
                return;
            }
            
            button.disabled = true;
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ekleniyor...';
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    updateCartBadge(data.cart_count);
                } else {
                    showToast(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Bir hata oluştu.', 'danger');
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = originalHTML;
            });
        });
    });
}

function initQuantitySelectors() {
    document.querySelectorAll('.qty-btn').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            const input = this.parentElement.querySelector('.qty-input');
            let value = parseInt(input.value) || 1;
            const max = parseInt(input.max) || 999;
            const min = parseInt(input.min) || 1;
            
            if (action === 'increase' && value < max) {
                value++;
            } else if (action === 'decrease' && value > min) {
                value--;
            }
            
            input.value = value;
            
            if (this.dataset.item) {
                updateCartItem(this.dataset.item, value);
            }
        });
    });
    
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', function() {
            if (this.dataset.item) {
                updateCartItem(this.dataset.item, this.value);
            }
        });
    });
}

function initCartOperations() {
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.item;
            removeCartItem(itemId);
        });
    });
}

function updateCartItem(itemId, quantity) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/cart/update/${itemId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartDisplay(data);
        } else {
            showToast(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Bir hata oluştu.', 'danger');
    });
}

function removeCartItem(itemId) {
    fetch(`/cart/remove/${itemId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
            if (itemElement) {
                itemElement.remove();
            }
            updateCartDisplay(data);
            showToast(data.message, 'success');
            
            if (data.cart_count === 0) {
                location.reload();
            }
        } else {
            showToast(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Bir hata oluştu.', 'danger');
    });
}

function updateCartDisplay(data) {
    const subtotalEl = document.getElementById('subtotal');
    const grandTotalEl = document.getElementById('grand-total');
    const totalDesiEl = document.getElementById('total-desi');
    const shippingMethodEl = document.getElementById('shipping-method');
    const shippingIconEl = document.getElementById('shipping-icon');
    const shippingBoxEl = document.getElementById('shipping-method-box');
    const shippingDescEl = document.getElementById('shipping-description');
    
    if (subtotalEl) subtotalEl.textContent = data.total.toFixed(2) + ' ₺';
    if (grandTotalEl) grandTotalEl.textContent = data.total.toFixed(2) + ' ₺';
    if (totalDesiEl) totalDesiEl.textContent = data.total_desi.toFixed(1);
    if (shippingMethodEl) shippingMethodEl.textContent = data.shipping_method;
    
    if (shippingIconEl) {
        shippingIconEl.className = 'fas ' + data.shipping_icon + ' fa-lg me-2';
    }
    
    if (shippingBoxEl) {
        shippingBoxEl.className = 'shipping-method-box alert alert-' + data.shipping_color;
    }
    
    if (shippingDescEl) {
        if (data.total_desi < 30) {
            shippingDescEl.textContent = 'Desi < 30 olduğu için Kargo ile gönderilecektir.';
        } else {
            shippingDescEl.textContent = 'Desi >= 30 olduğu için Ambar/Nakliye ile gönderilecektir.';
        }
    }
    
    updateCartBadge(data.cart_count);
}

function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = count;
    }
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

function initPasswordValidation() {
    const passwordInput = document.getElementById('passwordInput');
    if (!passwordInput) return;
    
    const rules = {
        'rule-length': /^.{8,}$/,
        'rule-upper': /[A-Z]/,
        'rule-lower': /[a-z]/,
        'rule-number': /[0-9]/,
        'rule-special': /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/
    };
    
    const registerBtn = document.getElementById('registerBtn');
    
    passwordInput.addEventListener('input', function(e) {
        const password = e.target.value;
        let allValid = true;
        
        for (const [ruleId, regex] of Object.entries(rules)) {
            const ruleElement = document.getElementById(ruleId);
            const isValid = regex.test(password);
            
            if (isValid) {
                ruleElement.classList.add('text-success');
                ruleElement.classList.remove('text-danger');
                const icon = ruleElement.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-check-circle text-success me-1';
                }
            } else {
                ruleElement.classList.add('text-danger');
                ruleElement.classList.remove('text-success');
                const icon = ruleElement.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-times-circle text-danger me-1';
                }
                allValid = false;
            }
        }
        
        if (registerBtn) {
            registerBtn.disabled = !allValid;
        }
    });
}

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
