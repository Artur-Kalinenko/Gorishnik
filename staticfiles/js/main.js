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
