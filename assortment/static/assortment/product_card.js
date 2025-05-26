// Получение CSRF-токена
function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

// Добавление товара в корзину
function addToCart(productId, quantity, variantId = null) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ quantity, variant_id: variantId }),
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
    root.querySelector('.decrease-quantity')?.addEventListener('click', () => {
        const val = parseInt(input.value, 10);
        if (val > 1) input.value = val - 1;
    });

    root.querySelector('.increase-quantity')?.addEventListener('click', () => {
        input.value = parseInt(input.value, 10) + 1;
    });

    root.querySelector('.add-to-cart')?.addEventListener('click', e => {
        const variantId = e.target.getAttribute('data-variant-id') || null;
        addToCart(productId, parseInt(input.value, 10), variantId);
        input.value = 1;
    });
}

// Основной обработчик DOM
document.addEventListener('DOMContentLoaded', () => {
    const selectedVariants = {};

    // === Граммовки ===
    document.querySelectorAll('.gram-button').forEach(button => {
        button.addEventListener('click', event => {
            const btn = event.currentTarget;
            const productId = btn.dataset.productId;
            const variantId = btn.dataset.variantId;
            const price = btn.dataset.price;
            const oldPrice = btn.dataset.oldPrice;
            const card = btn.closest('.product-card');

            selectedVariants[productId] = variantId;

            // Обновить цену
            const priceDisplay = document.getElementById(`price-display-${productId}`);
            if (priceDisplay) {
                priceDisplay.innerHTML = oldPrice && oldPrice !== 'None'
                    ? `<span class="old-price">${oldPrice} ₴</span><br><span class="price">${price} ₴</span>`
                    : `<span class="price">${price} ₴</span>`;
            }

            // Выделить выбранную граммовку
            document.querySelectorAll(`.gram-button[data-product-id="${productId}"]`)
                .forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            // Скрыть "Оберіть грамовку"
            const placeholder = card.querySelector('.variant-placeholder');
            if (placeholder) {
                placeholder.classList.add('fade-out');
                setTimeout(() => {
                    placeholder.innerHTML = '';
                    placeholder.classList.remove('fade-out');
                }, 300);
            }

            // Обработать корзину
            const existing = document.getElementById(`controls-${productId}`);
            if (existing) {
                existing.querySelector('.add-to-cart')?.setAttribute('data-variant-id', variantId);
            } else {
                const cartEl = document.createElement('div');
                cartEl.className = 'cart-controls fade-in';
                cartEl.id = `controls-${productId}`;
                cartEl.innerHTML = `
                    <button class="quantity-btn decrease-quantity" data-product-id="${productId}">−</button>
                    <input type="number" min="1" value="1" id="quantity-input-${productId}" class="quantity-input" readonly>
                    <button class="quantity-btn increase-quantity" data-product-id="${productId}">+</button>
                    <button class="add-to-cart" data-product-id="${productId}" data-variant-id="${variantId}">В корзину</button>
                `;
                const target = card.querySelector(`.cart-controls-placeholder#controls-${productId}`);
                if (target) {
                    target.replaceWith(cartEl);
                    attachQuantityHandlers(productId);
                }
            }
        });
    });

    // Уже отрисованные корзины
    document.querySelectorAll('.cart-controls[id^="controls-"]').forEach(el => {
        const productId = el.id.replace('controls-', '');
        attachQuantityHandlers(productId);
    });

    // === Избранное ===
    if (!window.IS_USER_CABINET) {
        document.querySelectorAll('.favorite-toggle').forEach(el => {
            el.addEventListener('click', () => {
                const productId = el.dataset.productId;
                fetch(`/favorites/toggle/${productId}/`, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                })
                .then(resp => {
                    if (resp.status === 403) {
                        document.getElementById('loginToast') && new bootstrap.Toast(document.getElementById('loginToast')).show();
                        return;
                    }
                    return resp.json();
                })
                .then(data => {
                    if (!data) return;
                    el.innerHTML = data.status === 'added'
                        ? '<i class="fas fa-star text-warning"></i>'
                        : '<i class="far fa-star"></i>';
                    showFavoriteToast(
                        data.status === 'added' ? 'Товар додано в обране' : 'Товар видалено з обраного',
                        data.status === 'added'
                    );
                })
                .catch(err => console.error('Помилка обраного:', err));
            });
        });
    }
});
