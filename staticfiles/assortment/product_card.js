// Получение CSRF-токена
function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

// Добавление товара в корзину
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

// Показ тоста
function showCartToast(message) {
    const toastEl = document.getElementById('cartToast');
    if (toastEl) {
        toastEl.querySelector('.toast-body').textContent = message;
        new bootstrap.Toast(toastEl).show();
    }
}

// Обработчики корзины
function attachQuantityHandlers(productId) {
    const root = document.getElementById(`controls-${productId}`);
    if (!root) return;

    const input = root.querySelector(`#quantity-input-${productId}`);
    const buttons = root.querySelectorAll('.quantity-btn');
    const addToCartBtn = root.querySelector('.add-to-cart');

    // Первая кнопка - уменьшение, вторая - увеличение
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
            // Не даём добавить в корзину без выбранной граммовки
            if (!variantId && addToCartBtn.hasAttribute('data-variant-id')) {
                showCartToast('Оберіть грамовку перед додаванням!');
                return;
            }
            addToCart(productId, parseInt(input.value, 10), variantId, grams);
            input.value = 1;
        };
    }
}

// Главный обработчик
document.addEventListener('DOMContentLoaded', () => {
    // Скрыть все cart-controls, показать select-variant-button-block
    document.querySelectorAll('.cart-switch').forEach(cartSwitch => {
        const selectVariantBlock = cartSwitch.querySelector('.select-variant-button-block');
        const cartControls = cartSwitch.querySelector('.cart-controls');
        if (selectVariantBlock && cartControls) {
            cartControls.style.display = 'none';
            selectVariantBlock.style.display = 'block';
        }
    });

    // При выборе граммовки
    document.querySelectorAll('.gram-button').forEach(button => {
        button.addEventListener('click', event => {
            const btn = event.currentTarget;
            const productId = btn.dataset.productId;
            const variantId = btn.dataset.variantId;
            const price = btn.dataset.price;
            const card = btn.closest('.product-card');
            const cartSwitch = card.querySelector(`#cart-switch-${productId}`);
            const selectVariantBlock = cartSwitch.querySelector('.select-variant-button-block');
            const cartControls = cartSwitch.querySelector('.cart-controls');

            // Обновление цены
            const priceDisplay = document.getElementById(`price-display-${productId}`);
            if (priceDisplay) {
                priceDisplay.innerHTML = `<span class="price">${price} ₴</span>`;
            }

            // Обновление стилей выбора
            document.querySelectorAll(`.gram-button[data-product-id="${productId}"]`)
                .forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            // Показать cart-controls, скрыть select-variant-button-block
            if (selectVariantBlock && cartControls) {
                selectVariantBlock.style.display = 'none';
                cartControls.style.display = 'flex';
                // Обновить data-variant-id и data-grams у кнопки корзины
                const addToCartBtn = cartControls.querySelector('.add-to-cart');
                if (addToCartBtn) {
                    addToCartBtn.setAttribute('data-variant-id', variantId);
                    addToCartBtn.setAttribute('data-grams', btn.textContent.trim());
                }
            }
            attachQuantityHandlers(productId);
        });
    });

    // Навесить обработчики на уже существующие блоки
    document.querySelectorAll('.cart-controls[id^="controls-"]').forEach(el => {
        const productId = el.id.replace('controls-', '');
        attachQuantityHandlers(productId);
    });
});
