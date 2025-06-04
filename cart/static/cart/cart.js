document.addEventListener('DOMContentLoaded', () => {
    // Функция для обновления количества
    const updateQuantity = (itemId, action) => {
        const quantityInput = document.getElementById(`quantity-input-${itemId}`);
        let quantity = parseInt(quantityInput.value);

        if (action === 'increase') {
            quantity++;
        } else if (action === 'decrease' && quantity > 1) {
            quantity--;
        }

        fetch(`/cart/update_quantity/${itemId}/`, {
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
                    quantityInput.value = quantity;
                    document.getElementById(`total-price-${itemId}`).textContent = data.item_total_price;
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

    // Удаление товара
    const removeItem = (itemId) => {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`cart-item-${itemId}`).remove();
                    document.getElementById('cart-total-price').textContent = data.cart_total_price;

                    // Показываем тост об удалении
                    showRemoveToast();

                    // Корректно обновляем иконку корзины в шапке
                    updateCartItemCount(data.cart_total_quantity);

                    // Проверяем, остались ли товары
                    const cartTable = document.querySelector('.cart-table');
                    const cartItems = document.querySelectorAll('.cart-table tbody tr');
                    if (cartItems.length === 0) {
                        if (cartTable) cartTable.style.display = 'none';
                        // Скрываем или удаляем блок с общей суммой
                        let cartTotalBlock = document.querySelector('.cart-total');
                        if (cartTotalBlock) cartTotalBlock.style.display = 'none';
                        let emptyBlock = document.querySelector('.empty-cart');
                        if (emptyBlock) {
                            emptyBlock.style.display = 'block';
                        } else {
                            // Если блока нет, создаём его
                            const cartContainer = document.querySelector('.cart-container');
                            if (cartContainer) {
                                cartContainer.insertAdjacentHTML('beforeend', `
                                    <div class="empty-cart">
                                        <i class="fas fa-shopping-cart empty-cart-icon"></i>
                                        <p class="empty-cart-text">Ваша корзина пуста</p>
                                        <a href="/assortment/" class="checkout-btn">
                                            <i class="fas fa-arrow-left"></i>
                                            Перейти к покупкам
                                        </a>
                                    </div>
                                `);
                            }
                        }
                    }
                } else {
                    console.error(data.message || 'Не вдалося видалити товар');
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
