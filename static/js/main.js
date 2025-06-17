// Получение CSRF-токена из cookies
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
    }
    return null;
}

// Сохранение сессии перед переходом на Google OAuth
function saveSessionAndRedirect() {
    fetch("/save-pre-session/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    }).then(() => {
        window.location.href = "/auth/login/google-oauth2/?next=/";
    }).catch((error) => {
        console.error('Помилка збереження сесії:', error);
        window.location.href = "/auth/login/google-oauth2/?next=/";
    });
}

// AJAX автоподсказка поиска
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("search-input");
    const suggestions = document.getElementById("suggestions");

    if (input && suggestions) {
        input.addEventListener("input", function () {
            const query = input.value.trim();
            if (!query) {
                suggestions.innerHTML = "";
                return;
            }

            fetch(`/assortment/search_suggest/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestions.innerHTML = "";
                    data.results.forEach(item => {
                        const link = document.createElement("a");
                        link.href = item.url;
                        link.className = "list-group-item list-group-item-action";
                        link.innerHTML = `
                          <div style="display: flex; align-items: center;">
                            ${item.image ? `<img src="${item.image}" alt="" style="width:32px;height:32px;object-fit:cover;border-radius:4px;margin-right:10px;">` : ''}
                            <div>
                              <strong>${item.name}</strong>
                              ${item.category ? `<br><small class="text-muted">${item.category}</small>` : ''}
                            </div>
                          </div>
                        `;
                        suggestions.appendChild(link);
                    });
                });
        });

        document.addEventListener("click", function (e) {
            if (!input.contains(e.target) && !suggestions.contains(e.target)) {
                suggestions.innerHTML = "";
            }
        });
    }
});

// Проверка срока жизни корзины
(function() {
    const CART_TTL_MS = 24 * 60 * 60 * 1000; // 24 часа
    const cartCreatedAt = parseInt(localStorage.getItem('cart_created_at'));
    const sessionId = localStorage.getItem('session_id');
    const now = Date.now();

    if (cartCreatedAt && now - cartCreatedAt > CART_TTL_MS) {
        localStorage.removeItem('cart_created_at');
        localStorage.removeItem('session_id');
        window.cartCleared = true;

        if (sessionId) {
            fetch('/clear-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ session_id: sessionId })
            });
        }
    }

    if (!cartCreatedAt) {
        localStorage.setItem('cart_created_at', now.toString());
    }
})();

function updateCartItemCount(count) {
    const countEl = document.getElementById('cart-item-count');
    if (countEl) {
        countEl.textContent = count;
        console.log('updateCartItemCount:', count);
    } else {
        console.log('updateCartItemCount: element not found');
    }
}

function addToCart(productId, quantity = 1, variantId = null) {
    const csrfToken = getCookie('csrftoken');
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
        console.error('Помилка при додаванні в корзину:', error);
    });
}

// Показ уведомления, если корзина была очищена
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

// Toast functions
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showFavoriteToast(message, isAdded) {
    const toastEl = document.getElementById('favorite-toast');
    const toastMessage = document.getElementById('favorite-toast-message');

    if (!toastEl || !toastMessage) return;

    toastMessage.textContent = message;
    toastEl.classList.remove('bg-success', 'bg-danger');
    toastEl.classList.add(isAdded ? 'bg-success' : 'bg-danger');

    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 5000 });
    toast.show();
}

function hideFavoriteToast() {
    const toastEl = document.getElementById('favorite-toast');
    if (!toastEl) return;

    const toast = bootstrap.Toast.getInstance(toastEl);
    if (toast) toast.hide();
}

function showCartToast() {
    const toastEl = document.getElementById('cartToast');
    if (!toastEl) return;

    const toastBody = toastEl.querySelector('.toast-body');
    let msg = '';
    if (typeof translations !== 'undefined' && translations.item_added_to_cart && translations.cart) {
        msg = translations.item_added_to_cart + ' <a href="/cart/" class="text-white text-decoration-underline">' + translations.cart + '</a>!';
    } else {
        msg = 'Товар добавлен в корзину!';
    }
    if (toastBody) {
        toastBody.innerHTML = msg;
    }
    console.log('showCartToast:', msg, translations);
    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 5000 });
    toast.show();
}

function showRemoveCartToast() {
    const toastEl = document.getElementById('removeCartToast');
    if (!toastEl) return;

    const toastBody = toastEl.querySelector('.toast-body');
    if (toastBody) {
        toastBody.textContent = translations.item_removed_from_cart + '!';
    }

    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 5000 });
    toast.show();
}

// Cart functions
function updateCart(productId, action) {
    fetch(`/cart/${action}/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const message = action === 'add' ? translations.item_added_to_cart : translations.item_removed_from_cart;
            showToast(message);
            updateCartCount(data.cart_count);
        } else {
            showToast(data.error || translations.server_error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast(translations.server_error, 'error');
    });
}

// Мобильное меню
function toggleMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const body = document.body;

    // Show mobile menu button only on mobile screens
    if (window.innerWidth <= 480) {
        mobileMenuBtn.style.display = 'flex';
    } else {
        mobileMenuBtn.style.display = 'none';
    }

    // Toggle mobile menu
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close mobile menu
    const closeBtn = document.querySelector('.mobile-menu-close');
    closeBtn.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        body.style.overflow = '';
    });

    // Handle mobile menu tabs
    const tabs = document.querySelectorAll('.mobile-menu-tab');
    const content = document.getElementById('mobile-menu-content');

    function renderSection(tabName) {
        if (tabName === 'categories') {
            const tpl = document.getElementById('mobile-menu-categories');
            content.innerHTML = tpl ? tpl.innerHTML : '';
        } else if (tabName === 'navigation') {
            const tpl = document.getElementById('mobile-menu-navigation');
            content.innerHTML = tpl ? tpl.innerHTML : '';
        }
    }

    // Инициализация: показываем первую вкладку
    let activeTab = document.querySelector('.mobile-menu-tab.active');
    if (!activeTab && tabs.length > 0) {
        activeTab = tabs[0];
        activeTab.classList.add('active');
    }
    if (activeTab) {
        renderSection(activeTab.getAttribute('data-tab'));
    }

    // Переключение вкладок
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderSection(tab.getAttribute('data-tab'));
        });
    });
}

// Initialize mobile menu
document.addEventListener('DOMContentLoaded', () => {
    toggleMobileMenu();
    
    // Update mobile menu on window resize
    window.addEventListener('resize', () => {
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        if (window.innerWidth <= 480) {
            mobileMenuBtn.style.display = 'flex';
        } else {
            mobileMenuBtn.style.display = 'none';
            document.querySelector('.mobile-menu').classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});

// Language switcher
document.addEventListener('DOMContentLoaded', function() {
    const languageSelect = document.querySelector('select[name="language"]');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }
});
