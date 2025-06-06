// === Универсальная инициализация страницы ассортимента ===
function initAssortmentPage() {
    setupGramsButtons();
    setupCartControls();
    setupCardHover();
    initFilterToggles();
    setupProducerFilterClicks();
}

// === Граммовки ===
function setupGramsButtons() {
    document.querySelectorAll('.grams-button').forEach(button => {
        button.addEventListener('click', event => {
            const productId = event.target.dataset.productId;
            const variantId = event.target.dataset.variantId;
            const price = event.target.dataset.price;
            const oldPrice = event.target.dataset.oldPrice;
            const priceDisplay = document.getElementById(`price-display-${productId}`);

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
                    <button class="quantity-btn decrease-quantity" data-product-id="${productId}">−</button>
                    <input type="number" min="1" value="1" id="quantity-input-${productId}" class="quantity-input text-center" readonly>
                    <button class="quantity-btn increase-quantity" data-product-id="${productId}">+</button>
                    <button class="category-btn add-to-cart d-flex align-items-center justify-content-center" data-product-id="${productId}" data-variant-id="${variantId}">
                        <img src="/media/icons/cart_brown.png" data-hover="/media/icons/cart_white.png" data-original="/media/icons/cart_brown.png" alt="В корзину" class="category-icon" style="width: 24px; height: 24px;">
                    </button>`;
                const cardBody = event.target.closest('.card-body');
                cardBody.appendChild(container);
                attachQuantityHandlers(productId);
                
                // Initialize hover effect for the newly added cart icon
                const newCartIcon = container.querySelector('img[data-hover]');
                if (newCartIcon) {
                    const originalSrc = newCartIcon.getAttribute("src");
                    const hoverSrc = newCartIcon.dataset.hover;
                    const container = newCartIcon.closest("button");
                    
                    if (hoverSrc && container) {
                        container.addEventListener("mouseenter", () => {
                            newCartIcon.setAttribute("src", hoverSrc);
                        });
                        container.addEventListener("mouseleave", () => {
                            newCartIcon.setAttribute("src", originalSrc);
                        });
                    }
                }
            }
        });
    });
}

// === Обработчики корзины ===
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

function setupCartControls() {
    document.querySelectorAll('.btn-group-container[id^="controls-"]').forEach(container => {
        const productId = container.id.replace('controls-', '');
        attachQuantityHandlers(productId);
    });
}

// === Наведение на карточки ===
function setupCardHover() {
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'scale(1.05)';
            card.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        });
        card.addEventListener('mouseout', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = 'none';
        });
        card.classList.add('fade-in');
    });
}

// === Плюсики фильтров ===
function initFilterToggles() {
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
}

// === Картинки-производители ===
function setupProducerFilterClicks() {
    document.querySelectorAll('input[name="producer"]').forEach(input => {
        const label = input.closest('label');
        if (label) {
            label.addEventListener('click', () => {
                input.checked = !input.checked;
                document.getElementById('filter-form').dispatchEvent(new Event('change'));
            });
        }
    });
}

// === AJAX фильтрация ===
function setupAjaxFilterForm() {
    const form = document.getElementById('filter-form');
    const productGrid = document.getElementById('product-grid');
    if (!form || !productGrid) return;

    form.addEventListener('change', function () {
        const url = this.action + '?' + new URLSearchParams(new FormData(this)).toString();
        productGrid.classList.add('fade-out');

        setTimeout(() => {
            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newGrid = doc.getElementById('product-grid');
                    productGrid.innerHTML = newGrid.innerHTML;
                    productGrid.classList.remove('fade-out');
                    initAssortmentPage();
                });
        }, 300);
    });
}

// === Инициализация при загрузке ===
document.addEventListener('DOMContentLoaded', () => {
    initAssortmentPage();
    setupAjaxFilterForm();
});
