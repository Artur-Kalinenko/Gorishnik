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

    // --- Новая логика выбора граммовки и количества ---
    let selectedVariantId = null;
    let selectedGrams = '';
    let selectedPrice = null;

    // --- Кнопки выбора варианта и добавления в корзину ---
    const selectVariantBtn = document.querySelector('.select-variant-btn');
    const addToCartBtn = document.querySelector('.add-to-cart-btn');

    function showSelectVariantBtn() {
        if (selectVariantBtn) selectVariantBtn.style.display = 'block';
        if (addToCartBtn) addToCartBtn.style.display = 'none';
    }
    function showAddToCartBtn() {
        if (selectVariantBtn) selectVariantBtn.style.display = 'none';
        if (addToCartBtn) addToCartBtn.style.display = 'block';
    }
    // По умолчанию показываем только select-variant
    showSelectVariantBtn();

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
            selectedVariantId = this.dataset.variantId;
            selectedGrams = this.dataset.grams;
            selectedPrice = this.dataset.price;
            // Обновляем цену только для выбранного варианта
            if (priceDisplay) {
                priceDisplay.innerHTML = `<p class="fw-bold mb-2 fs-4">${selectedPrice} ₴</p>`;
            }
            showAddToCartBtn();
        });
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

    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const quantity = quantityInput ? parseInt(quantityInput.value, 10) : 1;
            addToCart(productId, quantity, selectedVariantId, selectedGrams);
        });
    }

    // Функция добавления в корзину (скопирована из product_card.js)
    function getCSRFToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    }

    function addToCart(productId, quantity, variantId = null, grams = '') {
        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ quantity, variant_id: variantId, grams }),
        })
        .then(response => response.json())
        .then(data => {
            showCartToast('Товар додано в кошик');
            if (data.cart_total_quantity !== undefined) {
                const cartCount = document.getElementById('cart-item-count');
                if (cartCount) cartCount.textContent = data.cart_total_quantity;
            }
            // Сбросить счетчик количества до 1
            if (quantityInput) quantityInput.value = 1;
            // Сбросить выбор граммовки и показать select-variant
            gramsButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
            selectedVariantId = null;
            selectedGrams = '';
            selectedPrice = null;
            showSelectVariantBtn();
            // Вернуть диапазон цен, если есть
            if (minPrice && maxPrice && priceDisplay) {
                priceDisplay.innerHTML = `<p class="fw-bold mb-2 fs-4">${minPrice} ₴${minPrice !== maxPrice ? ' – ' + maxPrice + ' ₴' : ''}</p>`;
            }
        })
        .catch(err => console.error('Помилка при додаванні:', err));
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
