document.addEventListener('DOMContentLoaded', () => {
    // --- ГАЛЕРЕЯ ПРОДУКТА ---
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            if (mainImage) {
                mainImage.src = this.src;
                thumbnails.forEach(t => t.classList.remove('active-thumbnail'));
                this.classList.add('active-thumbnail');
            }
        });
    });

    // --- КОРЗИНА, ГРАММОВКИ, ДОБАВЛЕНИЕ ---
    const cartSwitch = document.querySelector('.cart-switch');
    if (!cartSwitch) return;
    const productId = cartSwitch.id.replace('cart-switch-', '');

    // Граммовки
    const gramButtons = document.querySelectorAll('.gram-button');
    const priceDisplay = document.getElementById(`price-display-${productId}`);
    const selectVariantBlock = document.getElementById(`select-variant-${productId}`);
    const cartControls = document.getElementById(`controls-${productId}`);

    function resetDetailCart() {
        gramButtons.forEach(b => b.classList.remove('selected'));
        if (selectVariantBlock) selectVariantBlock.style.display = 'block';
        if (cartControls) cartControls.style.display = 'none';
        // Если нужно, можно вернуть диапазон цен тут
    }

    // Логика выбора граммовки
    gramButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            gramButtons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            const variantId = btn.dataset.variantId;
            const price = btn.dataset.price;
            // Обновить цену
            if (priceDisplay) {
                priceDisplay.innerHTML = `<span class="price">${price} ₴</span>`;
            }
            // Показать cart-controls
            if (selectVariantBlock) selectVariantBlock.style.display = 'none';
            if (cartControls) {
                cartControls.style.display = 'flex';
                // Пропиши variantId на кнопке корзины
                const addToCartBtn = cartControls.querySelector('.add-to-cart');
                if (addToCartBtn) {
                    addToCartBtn.setAttribute('data-variant-id', variantId);
                    addToCartBtn.setAttribute('data-grams', btn.textContent.trim());
                }
            }
            attachQuantityHandlers(productId);
        });
    });

    // Управление количеством и добавлением в корзину
    function attachQuantityHandlers(productId) {
        const root = document.getElementById(`controls-${productId}`);
        if (!root) return;
        const input = root.querySelector(`#quantity-input-${productId}`);
        const buttons = root.querySelectorAll('.quantity-btn');
        const addToCartBtn = root.querySelector('.add-to-cart');

        if (buttons.length >= 2) {
            buttons[0].onclick = () => {
                const val = parseInt(input.value, 10);
                if (val > 1) input.value = val - 1;
            };
            buttons[1].onclick = () => {
                input.value = parseInt(input.value, 10) + 1;
            };
        }
        if (addToCartBtn) {
            addToCartBtn.onclick = (e) => {
                const variantId = addToCartBtn.getAttribute('data-variant-id') || null;
                const grams = addToCartBtn.getAttribute('data-grams') || '';
                if (!variantId && addToCartBtn.hasAttribute('data-variant-id')) {
                    showCartToast('Оберіть грамовку перед додаванням!');
                    return;
                }
                addToCart(productId, parseInt(input.value, 10), variantId, grams);
                input.value = 1;
                resetDetailCart();
            };
        }
    }

    // Инициализация: скрываем cart-controls, показываем "Оберіть грамовку"
    resetDetailCart();
    attachQuantityHandlers(productId);

    // --- Остальные функции (addToCart, showCartToast и т.д.) ---
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
        })
        .catch(err => console.error('Помилка при додаванні:', err));
    }
    function showCartToast(message) {
        const toastEl = document.getElementById('cartToast');
        if (toastEl) {
            toastEl.querySelector('.toast-body').textContent = message;
            // Для Bootstrap 5:
            if (typeof bootstrap !== "undefined") {
                const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
                toast.show();
            }
        }
    }
});
