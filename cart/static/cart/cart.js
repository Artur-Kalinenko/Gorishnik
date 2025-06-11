document.addEventListener('DOMContentLoaded', () => {
    // Функция для обновления количества
    const updateQuantity = (itemId, action) => {
        // Универсально ищем оба варианта инпута
        const quantityInputMobile = document.getElementById(`quantity-input-mobile-${itemId}`);
        const quantityInput = document.getElementById(`quantity-input-${itemId}`);
        // Выбираем тот, что есть (или оба)
        let quantity = 1;
        if (quantityInputMobile) {
            quantity = parseInt(quantityInputMobile.value);
        } else if (quantityInput) {
            quantity = parseInt(quantityInput.value);
        }

        if (action === 'increase') {
            quantity++;
        } else if (action === 'decrease' && quantity > 1) {
            quantity--;
        }

        // Get current language prefix from URL
        const langPrefix = window.location.pathname.split('/')[1];
        const baseUrl = langPrefix === 'uk' || langPrefix === 'ru' ? `/${langPrefix}` : '';

        fetch(`${baseUrl}/cart/update_quantity/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (quantityInput) quantityInput.value = quantity;
                    if (quantityInputMobile) quantityInputMobile.value = quantity;
                    // Обновляем цену и в мобильной карточке, если есть
                    const mobileTotal = document.getElementById(`total-price-mobile-${itemId}`);
                    if (mobileTotal) mobileTotal.textContent = data.item_total_price;
                    const total = document.getElementById(`total-price-${itemId}`);
                    if (total) total.textContent = data.item_total_price;
                    document.getElementById('cart-total-price').textContent = data.cart_total_price;

                    // ✅ Обновляем иконку корзины в шапке
                    updateCartItemCount(data.cart_total_quantity);
                } else {
                    console.error(data.message || 'Не вдалося оновити кількість');
                }
            })
            .catch(error => console.error('Помилка:', error));
    };

    // Функция для показа тоста удаления
    const showRemoveToast = () => {
        const removeToast = document.getElementById('removeCartToast');
        const toast = new bootstrap.Toast(removeToast);
        toast.show();
    };

    // Функция для удаления товара
    const removeItem = (itemId) => {
        // Get current language prefix from URL
        const langPrefix = window.location.pathname.split('/')[1];
        const baseUrl = langPrefix === 'uk' || langPrefix === 'ru' ? `/${langPrefix}` : '';

        fetch(`${baseUrl}/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Удаляем элемент из DOM
                    const itemElement = document.getElementById(`cart-mobile-item-${itemId}`);
                    if (itemElement) itemElement.remove();

                    // Обновляем общую сумму
                    document.getElementById('cart-total-price').textContent = data.cart_total_price;

                    // Обновляем количество в корзине
                    updateCartItemCount(data.cart_total_quantity);

                    // Показываем тост
                    showRemoveToast();

                    // Если корзина пуста, перезагружаем страницу
                    if (data.cart_total_quantity === 0) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                }
            })
            .catch(error => console.error('Помилка:', error));
    };

    // Обработка кнопок изменения количества
    document.querySelectorAll('.update-quantity').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.getAttribute('data-item-id');
            const action = button.getAttribute('data-action');
            updateQuantity(itemId, action);
        });
    });

    // Обработка кнопок удаления товара
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.getAttribute('data-item-id');
            removeItem(itemId);
        });
    });
});

// Сообщение об очистке корзины
if (window.cartCleared && window.location.pathname === '/cart/') {
    const container = document.querySelector('.container');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-warning text-center mt-5">
                Ваша корзина була очищена через неактивність.
            </div>
        `;
    }
}
