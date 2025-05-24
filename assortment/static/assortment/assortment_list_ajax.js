
// === Плавная анимация карточек ===
function animateProductCards() {
    document.querySelectorAll('.product-card').forEach(card => {
        card.classList.remove('fade-in'); // сброс, чтобы переиграть
        void card.offsetWidth; // ререндер
        card.classList.add('fade-in');
    });
}

// === Навесить обработчики для количества и корзины ===
function attachQuantityHandlersToAll() {
    document.querySelectorAll('.btn-group-container[id^="controls-"]').forEach(container => {
        const productId = container.id.replace('controls-', '');
        attachQuantityHandlers(productId);
    });
}

// === Обработка формы фильтров через AJAX ===
function setupAjaxFilterForm() {
    const form = document.getElementById('filter-form');
    const productGrid = document.getElementById('product-grid');

    if (!form || !productGrid) return;

    form.addEventListener('change', function () {
        const url = this.action + '?' + new URLSearchParams(new FormData(this)).toString();
        productGrid.classList.add('fade-out');

        setTimeout(() => {
            fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newGrid = doc.getElementById('product-grid');

                    productGrid.innerHTML = newGrid.innerHTML;
                    productGrid.classList.remove('fade-out');
                    animateProductCards();
                    attachQuantityHandlersToAll();
                    attachFavoriteHandlers();
                })
                .catch(error => {
                    console.error('Помилка під час AJAX фільтрації:', error);
                });
        }, 300);
    });
}

// === Обработка избранного (переустановка после ajax) ===
function attachFavoriteHandlers() {
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
}

document.addEventListener('DOMContentLoaded', () => {
    setupAjaxFilterForm();
    animateProductCards();
    attachQuantityHandlersToAll();
    attachFavoriteHandlers();
});
