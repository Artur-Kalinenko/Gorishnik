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
                } else {
                    console.error(data.message || 'Не вдалося оновити кількість');
                }
            })
            .catch(error => console.error('Помилка:', error));
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

                    const cartItems = document.querySelectorAll('tbody tr');
                    if (cartItems.length === 0) {
                        document.querySelector('tbody').innerHTML = `
                            <tr>
                                <td colspan="6" class="text-center">Ваша корзина пуста.</td>
                            </tr>
                        `;
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
