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
//// === Обработка избранного после замены DOM ===
//function attachFavoriteHandlers() {
//    if (!window.IS_USER_CABINET) {
//        document.querySelectorAll('.favorite-toggle').forEach(el => {
//            el.addEventListener('click', function () {
//                const productId = el.dataset.productId;
//
//                fetch(`/favorites/toggle/${productId}/`, {
//                    method: 'GET',
//                    headers: {
//                        'X-Requested-With': 'XMLHttpRequest',
//                    },
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
//
//                    // ВАЖНО: используем сохранённую переменную el
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
//                    const toastEl = document.getElementById('loginToast');
//                    if (toastEl) {
//                        const toast = new bootstrap.Toast(toastEl);
//                        toast.show();
//                    }
//                });
//            });
//        });
//    }
//}
//
//// === Обновление кнопок граммовок ===
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
//                    priceDisplay.innerHTML = `
//                        <span class="text-muted text-decoration-line-through">${oldPrice} ₴</span><br>
//                        <strong class="text-danger">${price} ₴</strong>
//                    `;
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
//            }
//        });
//    });
//}
//
//// === AJAX фильтрация ===
//function setupAjaxFilterForm() {
//    const form = document.getElementById('filter-form');
//    const productGrid = document.getElementById('product-grid');
//
//    if (!form || !productGrid) return;
//
//    console.log("AJAX фильтр: обработчик навешен");
//
//    form.addEventListener('change', function () {
//        const url = this.action + '?' + new URLSearchParams(new FormData(this)).toString();
//        productGrid.classList.add('fade-out');
//
//        setTimeout(() => {
//            fetch(url, {
//                headers: { 'X-Requested-With': 'XMLHttpRequest' }
//            })
//                .then(response => response.text())
//                .then(html => {
//                    const parser = new DOMParser();
//                    const doc = parser.parseFromString(html, 'text/html');
//                    const newGrid = doc.getElementById('product-grid');
//
//                    console.log("AJAX фильтр: получили HTML. newGrid найден?", !!newGrid);
//
//                    if (!newGrid) {
//                        console.warn("AJAX фильтр: блок product-grid не найден в ответе сервера.");
//                        return;
//                    }
//
//                    productGrid.innerHTML = newGrid.innerHTML;
//                    productGrid.classList.remove('fade-out');
//
//                    animateProductCards();
//                    attachQuantityHandlersToAll();
//                    attachFavoriteHandlers();
//                    setupVariantButtons();
//                })
//                .catch(error => {
//                    console.error('Помилка під час AJAX фільтрації:', error);
//                });
//        }, 300);
//    });
//}
//
//// === Init ===
//document.addEventListener('DOMContentLoaded', () => {
//    setupAjaxFilterForm();
//    animateProductCards();
//    attachQuantityHandlersToAll();
//    attachFavoriteHandlers();
//    setupVariantButtons();
//});