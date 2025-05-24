//// === Универсальная инициализация ===
//function initAssortmentPage() {
//    animateProductCards();
//    attachQuantityHandlersToAll();
//    attachFavoriteHandlers();
//    setupVariantButtons();
//}
//
//// === Анимация карточек ===
//function animateProductCards() {
//    document.querySelectorAll('.product-card').forEach(card => {
//        card.classList.remove('fade-in');
//        void card.offsetWidth;
//        card.classList.add('fade-in');
//    });
//}
//
//// === Обработчики количества и корзины ===
//function attachQuantityHandlersToAll() {
//    document.querySelectorAll('.btn-group-container[id^="controls-"]').forEach(container => {
//        const productId = container.id.replace('controls-', '');
//        attachQuantityHandlers(productId);
//    });
//}
//
//function attachQuantityHandlers(productId) {
//    const decreaseBtn = document.querySelector(`#controls-${productId} .decrease-quantity`);
//    const increaseBtn = document.querySelector(`#controls-${productId} .increase-quantity`);
//    const addToCartBtn = document.querySelector(`#controls-${productId} .add-to-cart`);
//
//    if (decreaseBtn) {
//        const newDec = decreaseBtn.cloneNode(true);
//        decreaseBtn.parentNode.replaceChild(newDec, decreaseBtn);
//        newDec.addEventListener('click', () => {
//            const input = document.getElementById(`quantity-input-${productId}`);
//            const value = parseInt(input.value, 10);
//            if (value > 1) input.value = value - 1;
//        });
//    }
//
//    if (increaseBtn) {
//        const newInc = increaseBtn.cloneNode(true);
//        increaseBtn.parentNode.replaceChild(newInc, increaseBtn);
//        newInc.addEventListener('click', () => {
//            const input = document.getElementById(`quantity-input-${productId}`);
//            input.value = parseInt(input.value, 10) + 1;
//        });
//    }
//
//    if (addToCartBtn) {
//        const newAdd = addToCartBtn.cloneNode(true);
//        addToCartBtn.parentNode.replaceChild(newAdd, addToCartBtn);
//        newAdd.addEventListener('click', event => {
//            const input = document.getElementById(`quantity-input-${productId}`);
//            const quantity = input.value;
//            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
//            const variantId = event.target.getAttribute('data-variant-id') || null;
//
//            fetch(`/cart/add/${productId}/`, {
//                method: 'POST',
//                headers: {
//                    'X-CSRFToken': csrfToken,
//                    'Content-Type': 'application/json',
//                },
//                body: JSON.stringify({ quantity, variant_id: variantId }),
//            })
//            .then(response => response.json())
//            .then(data => {
//                if (data.session_id) {
//                    localStorage.setItem('session_id', data.session_id);
//                }
//                showCartToast();
//                input.value = 1;
//            })
//            .catch(error => {
//                console.error('Помилка при додаванні в корзину:', error);
//            });
//        });
//    }
//}
//
//// === Обработка избранного ===
//function attachFavoriteHandlers() {
//    if (!window.IS_USER_CABINET) {
//        document.querySelectorAll('.favorite-toggle').forEach(el => {
//            el.addEventListener('click', function () {
//                const productId = el.dataset.productId;
//
//                fetch(`/favorites/toggle/${productId}/`, {
//                    method: 'GET',
//                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
//                })
//                .then(response => {
//                    if (response.status === 403) {
//                        const toastEl = document.getElementById('loginToast');
//                        if (toastEl) {
//                            const toast = new bootstrap.Toast(toastEl);
//                            toast.show();
//                        }
//                        return;
//                    }
//                    return response.json();
//                })
//                .then(data => {
//                    if (!data) return;
//                    if (data.status === 'added') {
//                        el.innerHTML = '<i class="fas fa-star text-warning"></i>';
//                        showFavoriteToast('Товар додано в обране', true);
//                    } else if (data.status === 'removed') {
//                        el.innerHTML = '<i class="far fa-star"></i>';
//                        showFavoriteToast('Товар видалено з обраного', false);
//                    }
//                })
//                .catch(error => {
//                    console.error('Помилка при додаванні в обрані:', error);
//                });
//            });
//        });
//    }
//}
//
//// === Обработка выбора граммовки ===
//function setupVariantButtons() {
//    document.querySelectorAll('.grams-button').forEach(button => {
//        button.addEventListener('click', event => {
//            const productId = event.target.dataset.productId;
//            const variantId = event.target.dataset.variantId;
//            const price = event.target.dataset.price;
//            const oldPrice = event.target.dataset.oldPrice;
//            const priceDisplay = document.getElementById(`price-display-${productId}`);
//
//            if (priceDisplay) {
//                if (oldPrice && oldPrice !== "None") {
//                    priceDisplay.innerHTML = `<span class="text-muted text-decoration-line-through">${oldPrice} ₴</span><br><strong class="text-danger">${price} ₴</strong>`;
//                } else {
//                    priceDisplay.innerHTML = `<strong>${price} ₴</strong>`;
//                }
//            }
//
//            document.querySelectorAll(`.grams-button[data-product-id="${productId}"]`).forEach(btn => {
//                btn.classList.remove('selected');
//            });
//            event.target.classList.add('selected');
//
//            const selectBtn = document.getElementById(`select-variant-${productId}`);
//            if (selectBtn) selectBtn.style.display = 'none';
//
//            const oldControls = document.getElementById(`controls-${productId}`);
//            if (oldControls) {
//                const existingAddButton = oldControls.querySelector('.add-to-cart');
//                if (existingAddButton) {
//                    existingAddButton.setAttribute('data-variant-id', variantId);
//                }
//            } else {
//                const container = document.createElement('div');
//                container.className = 'd-flex align-items-center justify-content-center btn-group-container';
//                container.id = `controls-${productId}`;
//                container.innerHTML = `
//                    <button class="btn btn-primary decrease-quantity" data-product-id="${productId}">−</button>
//                    <input type="number" min="1" value="1" id="quantity-input-${productId}" class="quantity-input text-center" readonly>
//                    <button class="btn btn-primary increase-quantity" data-product-id="${productId}">+</button>
//                    <button class="btn btn-primary add-to-cart" data-product-id="${productId}" data-variant-id="${variantId}">В корзину</button>
//                `;
//                const cardBody = event.target.closest('.card-body');
//                cardBody.appendChild(container);
//                attachQuantityHandlers(productId);
//            }
//        });
//    });
//}
//
//// === AJAX фильтрация ===
//function setupAjaxFilterForm() {
//    const form = document.getElementById('filter-form');
//    const productGrid = document.getElementById('product-grid');
//    if (!form || !productGrid) return;
//
//    form.addEventListener('change', function () {
//        const url = this.action + '?' + new URLSearchParams(new FormData(this)).toString();
//        productGrid.classList.add('fade-out');
//
//        setTimeout(() => {
//            fetch(url, {
//                headers: { 'X-Requested-With': 'XMLHttpRequest' }
//            })
//            .then(response => response.text())
//            .then(html => {
//                const parser = new DOMParser();
//                const doc = parser.parseFromString(html, 'text/html');
//                const newGrid = doc.getElementById('product-grid');
//                productGrid.innerHTML = newGrid.innerHTML;
//                productGrid.classList.remove('fade-out');
//
//                initAssortmentPage(); // 🔁 Повторная инициализация после замены DOM
//            });
//        }, 300);
//    });
//}
//
//// === Инициализация при загрузке страницы ===
//document.addEventListener('DOMContentLoaded', () => {
//    initAssortmentPage();
//    setupAjaxFilterForm();
//});
