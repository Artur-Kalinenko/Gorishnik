// Получение CSRF-токена
function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

// Добавление товара в корзину
function addToCart(productId, quantity = 1, variantId = null) {
    const csrfToken = getCSRFToken();
    // Get current language prefix from URL
    const langPrefix = window.location.pathname.split('/')[1];
    const baseUrl = langPrefix === 'uk' || langPrefix === 'ru' ? `/${langPrefix}` : '';

    fetch(`${baseUrl}/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity, variant_id: variantId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.session_id) {
            localStorage.setItem('session_id', data.session_id);
        }
        if (data.cart_item_count !== undefined) {
            updateCartItemCount(data.cart_item_count);
        }
        showCartToast();
    })
    .catch(error => {
        console.error('Error:', error);
    });
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
                showCartToast();
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
