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

// AJAX
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("search-input");
    const suggestions = document.getElementById("suggestions");

    if (!input || !suggestions) return;

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

                    // Основное название товара
                    link.innerHTML = `<strong>${item.name}</strong>`;

                    // Если есть категория — показываем под названием
                    if (item.category) {
                        link.innerHTML += `<br><small class="text-muted">${item.category}</small>`;
                    }

                    suggestions.appendChild(link);
                });
            });
    });

    document.addEventListener("click", function (e) {
        if (!input.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.innerHTML = "";
        }
    });
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

// Тосты
function showFavoriteToast(message, isAdded) {
    const toastEl = document.getElementById('favorite-toast');
    const toastMessage = document.getElementById('favorite-toast-message');

    if (!toastEl || !toastMessage) return;

    // Устанавливаем сообщение и цвет
    toastMessage.textContent = message;
    toastEl.classList.remove('bg-success', 'bg-danger');
    toastEl.classList.add(isAdded ? 'bg-success' : 'bg-danger');

    // Инициализация и показ тоста
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

    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 5000 });
    toast.show();
}