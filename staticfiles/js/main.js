// Проверка срока жизни корзины
(function() {
    const CART_TTL_MS = 24 * 60 * 60 * 1000; // 24 часа в мс
    const cartCreatedAt = parseInt(localStorage.getItem('cart_created_at')); // изменил
    const sessionId = localStorage.getItem('session_id');
    const now = Date.now();

    // Если корзина устарела — очищаем
    if (cartCreatedAt && now - parseInt(cartCreatedAt) > CART_TTL_MS) {
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

    // Если корзина новая — сохраняем дату создания
    if (!cartCreatedAt) {
        localStorage.setItem('cart_created_at', now.toString());
    }

    // Получение CSRF-токена из cookies
    function getCookie(name) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            let [key, value] = cookie.trim().split('=');
            if (key === name) return decodeURIComponent(value);
        }
        return null;
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
