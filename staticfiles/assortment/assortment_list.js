// Функция: обработка кнопок изменения количества и добавления в корзину
function attachQuantityHandlers(productId) {
    const decreaseBtn = document.querySelector(`#controls-${productId} .decrease-quantity`);
    const increaseBtn = document.querySelector(`#controls-${productId} .increase-quantity`);
    const addToCartBtn = document.querySelector(`#controls-${productId} .add-to-cart`);

    if (decreaseBtn) {
        const newDec = decreaseBtn.cloneNode(true);
        decreaseBtn.parentNode.replaceChild(newDec, decreaseBtn);
        newDec.addEventListener('click', () => {
            const input = document.getElementById(`quantity-input-${productId}`);
            const value = parseInt(input.value, 10);
            if (value > 1) input.value = value - 1;
        });
    }

    if (increaseBtn) {
        const newInc = increaseBtn.cloneNode(true);
        increaseBtn.parentNode.replaceChild(newInc, increaseBtn);
        newInc.addEventListener('click', () => {
            const input = document.getElementById(`quantity-input-${productId}`);
            input.value = parseInt(input.value, 10) + 1;
        });
    }

    if (addToCartBtn) {
        const newAdd = addToCartBtn.cloneNode(true);
        addToCartBtn.parentNode.replaceChild(newAdd, addToCartBtn);
        newAdd.addEventListener('click', event => {
            const input = document.getElementById(`quantity-input-${productId}`);
            const quantity = input.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            const variantId = event.target.getAttribute('data-variant-id') || null;

            fetch(`/cart/add/${productId}/`, {
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
                showCartToast();
                input.value = 1;
            })
            .catch(error => {
                console.error('Помилка при додаванні в корзину:', error);
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const selectedVariants = {};

    // === Обработка граммовок ===
    document.querySelectorAll('.grams-button').forEach(button => {
        button.addEventListener('click', event => {
            const productId = event.target.dataset.productId;
            const variantId = event.target.dataset.variantId;
            const price = event.target.dataset.price;
            const oldPrice = event.target.dataset.oldPrice;
            const priceDisplay = document.getElementById(`price-display-${productId}`);

            selectedVariants[productId] = variantId;
            if (priceDisplay) {
                if (oldPrice && oldPrice !== "None") {
                    priceDisplay.innerHTML = `
                        <span class="text-muted text-decoration-line-through">${oldPrice} ₴</span><br>
                        <strong class="text-danger">${price} ₴</strong>
                    `;
                } else {
                    priceDisplay.innerHTML = `<strong>${price} ₴</strong>`;
                }
            }

            document.querySelectorAll(`.grams-button[data-product-id="${productId}"]`).forEach(btn => {
                btn.classList.remove('selected');
            });
            event.target.classList.add('selected');

            const selectBtn = document.getElementById(`select-variant-${productId}`);
            if (selectBtn) selectBtn.style.display = 'none';

            const oldControls = document.getElementById(`controls-${productId}`);
            if (oldControls) {
                const existingAddButton = oldControls.querySelector('.add-to-cart');
                if (existingAddButton) {
                    existingAddButton.setAttribute('data-variant-id', variantId);
                }
            } else {
                const container = document.createElement('div');
                container.className = 'd-flex align-items-center justify-content-center btn-group-container';
                container.id = `controls-${productId}`;
                container.innerHTML = `
                    <button class="btn btn-primary decrease-quantity" data-product-id="${productId}">−</button>
                    <input type="number" min="1" value="1" id="quantity-input-${productId}" class="quantity-input text-center" readonly>
                    <button class="btn btn-primary increase-quantity" data-product-id="${productId}">+</button>
                    <button class="btn btn-primary add-to-cart" data-product-id="${productId}" data-variant-id="${variantId}">В корзину</button>
                `;
                const cardBody = event.target.closest('.card-body');
                cardBody.appendChild(container);
                attachQuantityHandlers(productId);
            }
        });
    });

    // === Навесить обработчики на уже отрисованные товары ===
    document.querySelectorAll('.btn-group-container[id^="controls-"]').forEach(container => {
        const productId = container.id.replace('controls-', '');
        attachQuantityHandlers(productId);
    });

    // === Эффект наведения на карточку товара ===
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'scale(1.05)';
            card.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        });
        card.addEventListener('mouseout', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = 'none';
        });
    });


    // === Раскрытие фильтров с сохранением состояния ===
    const OPENED_FILTERS_KEY = 'opened_filter_groups';

    function saveOpenedGroups(openedIds) {
        localStorage.setItem(OPENED_FILTERS_KEY, JSON.stringify(openedIds));
    }

    function getOpenedGroups() {
        try {
            return JSON.parse(localStorage.getItem(OPENED_FILTERS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    let openedGroups = getOpenedGroups();

    document.querySelectorAll('.filter-header').forEach(header => {
        const groupId = header.dataset.groupId;
        const options = document.getElementById(`group-${groupId}`);
        const icon = document.getElementById(`icon-${groupId}`);

        if (openedGroups.includes(groupId)) {
            options.style.display = 'block';
            icon.textContent = '−';
        }

        header.addEventListener('click', () => {
            const isOpen = options.style.display === 'block';

            options.style.display = isOpen ? 'none' : 'block';
            icon.textContent = isOpen ? '+' : '−';

            if (isOpen) {
                openedGroups = openedGroups.filter(id => id !== groupId);
            } else {
                openedGroups.push(groupId);
            }

            saveOpenedGroups(openedGroups);
        });
    });

    // === Автоотправка формы при изменении чекбоксов ===
    document.querySelectorAll('#filter-form input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            document.getElementById('filter-form').submit();
        });
    });

    // === Очистка фильтров ===
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const url = new URL(window.location.href);
            const params = url.searchParams;

            params.delete('filters');
            params.delete('q');
            params.delete('discounted');
            params.delete('new');

            localStorage.removeItem(OPENED_FILTERS_KEY);

            const queryString = params.toString();
            const target = queryString ? url.pathname + '?' + queryString : url.pathname;
            window.location.href = target;
        });
    }
});

// === Обработка избранного ===
if (!window.IS_USER_CABINET) {
    document.querySelectorAll('.favorite-toggle').forEach(el => {
        el.addEventListener('click', function () {
            const productId = this.dataset.productId;

            fetch(`/favorites/toggle/${productId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => {
                if (response.status === 403) {
                    const toastEl = document.getElementById('loginToast');
                    if (toastEl) {
                        const toast = new bootstrap.Toast(toastEl);
                        toast.show();
                    }
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;
                if (data.status === 'added') {
                    this.innerHTML = '<i class="fas fa-star text-warning"></i>';
                    showFavoriteToast('Товар додано в обране', true);
                } else if (data.status === 'removed') {
                    this.innerHTML = '<i class="far fa-star"></i>';
                    showFavoriteToast('Товар видалено з обраного', false);
                }
            })
            .catch(error => {
                console.error('Помилка при додаванні в обрані:', error);
                const toastEl = document.getElementById('loginToast');
                if (toastEl) {
                    const toast = new bootstrap.Toast(toastEl);
                    toast.show();
                }
            });
        });
    });
}