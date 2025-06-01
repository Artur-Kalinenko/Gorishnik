document.addEventListener('DOMContentLoaded', function() {
    // Image Gallery
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-img');

    // Make changeMainImage function globally available
    window.changeMainImage = function(thumbnail) {
        if (mainImage) {
            mainImage.src = thumbnail.src;
            thumbnails.forEach(thumb => thumb.classList.remove('active-thumbnail'));
            thumbnail.classList.add('active-thumbnail');
        }
    };

    // Add click event listeners to thumbnails
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            changeMainImage(this);
        });
    });

    // Variant Selection
    const gramsButtons = document.querySelectorAll('.grams-button');
    const priceDisplay = document.getElementById('price-display');
    let minPrice = null, maxPrice = null;
    if (priceDisplay) {
        // Сохраняем min-max цену для сброса
        const priceText = priceDisplay.textContent;
        const match = priceText.match(/([\d.,]+)\s*₴(?:\s*–\s*([\d.,]+)\s*₴)?/);
        if (match) {
            minPrice = match[1];
            maxPrice = match[2] || match[1];
        }
    }
    gramsButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            gramsButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
            this.classList.add('btn-primary');
        });
        button.addEventListener('mouseleave', function() {
            gramsButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
        });
        button.addEventListener('click', function() {
            gramsButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
            this.classList.add('btn-primary', 'active');
            const price = this.dataset.price;
            const oldPrice = this.dataset.oldPrice;
            updatePriceDisplay(price, oldPrice);
        });
    });

    function updatePriceDisplay(price, oldPrice) {
        if (oldPrice && oldPrice !== 'None') {
            priceDisplay.innerHTML = `
                <p class="mb-1 text-muted text-decoration-line-through">${oldPrice} ₴</p>
                <p class="fw-bold text-danger mb-2 fs-4">${price} ₴</p>
            `;
        } else {
            priceDisplay.innerHTML = `
                <p class="fw-bold mb-2 fs-4">${price} ₴</p>
            `;
        }
    }

    // Сброс цены на min-max при клике вне кнопок
    document.addEventListener('click', function(e) {
        if (![...gramsButtons].some(btn => btn.contains(e.target))) {
            gramsButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
            if (minPrice && maxPrice) {
                priceDisplay.innerHTML = `<p class=\"fw-bold mb-2 fs-4\">${minPrice} ₴${minPrice !== maxPrice ? ' – ' + maxPrice + ' ₴' : ''}</p>`;
            }
        }
    });

    // Quantity controls
    const quantityInput = document.querySelector('.quantity-input');
    const decreaseBtn = document.querySelector('.decrease-quantity');
    const increaseBtn = document.querySelector('.increase-quantity');
    if (quantityInput && decreaseBtn && increaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            let val = parseInt(quantityInput.value, 10);
            if (val > 1) quantityInput.value = val - 1;
        });
        increaseBtn.addEventListener('click', function() {
            let val = parseInt(quantityInput.value, 10);
            quantityInput.value = val + 1;
        });
    }

    // Add to Cart
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const selectedVariant = document.querySelector('.grams-button.active');
            const variantGrams = selectedVariant ? selectedVariant.dataset.grams : null;
            const quantity = quantityInput ? parseInt(quantityInput.value, 10) : 1;
            addToCart(productId, variantGrams, quantity);
        });
    }

    function addToCart(productId, variantGrams, quantity) {
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                variant_grams: variantGrams,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Товар додано до кошика', 'success');
                updateCartCount(data.cart_count);
            } else {
                showNotification(data.message || 'Помилка при додаванні до кошика', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Помилка при додаванні до кошика', 'error');
        });
    }

    // Utility Functions
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            min-width: 300px;
            padding: 15px 20px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    function updateCartCount(count) {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
        }
    }

    // Add CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});
