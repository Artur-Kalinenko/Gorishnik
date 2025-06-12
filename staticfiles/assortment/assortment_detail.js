document.addEventListener('DOMContentLoaded', () => {
    // --- ГАЛЕРЕЯ ПРОДУКТА ---
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            if (mainImage) {
                mainImage.src = this.src;
                thumbnails.forEach(t => t.classList.remove('active-thumbnail'));
                this.classList.add('active-thumbnail');
            }
        });
    });

    // --- ПРОКРУТКА ГАЛЕРЕИ СТРЕЛКАМИ ---
    const gallery = document.getElementById('thumbnailGallery');
    const leftArrow = document.getElementById('galleryArrowLeft');
    const rightArrow = document.getElementById('galleryArrowRight');

    function updateArrows() {
        if (!gallery || !leftArrow || !rightArrow) return;
        const isScrollable = gallery.scrollWidth > gallery.clientWidth + 5;
        leftArrow.style.display = isScrollable ? '' : 'none';
        rightArrow.style.display = isScrollable ? '' : 'none';

        leftArrow.disabled = gallery.scrollLeft < 5;
        rightArrow.disabled = gallery.scrollLeft + gallery.clientWidth + 5 >= gallery.scrollWidth;
    }

    function scrollGalleryBy(offset) {
        if (!gallery) return;
        gallery.scrollBy({ left: offset, behavior: 'smooth' });
    }

    if (gallery && leftArrow && rightArrow) {
        updateArrows();

        leftArrow.addEventListener('click', () => {
            scrollGalleryBy(-120);
            setTimeout(updateArrows, 300);
        });
        rightArrow.addEventListener('click', () => {
            scrollGalleryBy(120);
            setTimeout(updateArrows, 300);
        });

        gallery.addEventListener('scroll', updateArrows);
        window.addEventListener('resize', updateArrows);

        setTimeout(updateArrows, 500);
    }

    // --- КОРЗИНА, ГРАММОВКИ, ДОБАВЛЕНИЕ ---
    const cartSwitch = document.querySelector('.cart-switch');
    if (cartSwitch) {
        const productId = cartSwitch.id.replace('cart-switch-', '');
        const gramButtons = document.querySelectorAll('.gram-button');
        const priceDisplay = document.getElementById(`price-display-${productId}`);
        const selectVariantBlock = document.getElementById(`select-variant-${productId}`);
        const cartControls = document.getElementById(`controls-${productId}`);

        function resetDetailCart() {
            gramButtons.forEach(b => b.classList.remove('selected'));
            if (selectVariantBlock) selectVariantBlock.style.display = 'block';
            if (cartControls) cartControls.style.display = 'none';
        }

        gramButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                gramButtons.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                const variantId = btn.dataset.variantId;
                const price = btn.dataset.price;
                if (priceDisplay) {
                    priceDisplay.innerHTML = `<span class="price">${price} ₴</span>`;
                }
                if (selectVariantBlock) selectVariantBlock.style.display = 'none';
                if (cartControls) {
                    cartControls.style.display = 'flex';
                    const addToCartBtn = cartControls.querySelector('.add-to-cart');
                    if (addToCartBtn) {
                        addToCartBtn.setAttribute('data-variant-id', variantId);
                        addToCartBtn.setAttribute('data-grams', btn.textContent.trim());
                    }
                }
                attachQuantityHandlers(productId);
            });
        });

        function attachQuantityHandlers(productId) {
            const root = document.getElementById(`controls-${productId}`);
            if (!root) return;
            const input = root.querySelector(`#quantity-input-${productId}`);
            const buttons = root.querySelectorAll('.quantity-btn');
            const addToCartBtn = root.querySelector('.add-to-cart');

            if (buttons.length >= 2) {
                buttons[0].onclick = () => {
                    const val = parseInt(input.value, 10);
                    if (val > 1) input.value = val - 1;
                };
                buttons[1].onclick = () => {
                    input.value = parseInt(input.value, 10) + 1;
                };
            }
            if (addToCartBtn) {
                addToCartBtn.onclick = (e) => {
                    const variantId = addToCartBtn.getAttribute('data-variant-id') || null;
                    const grams = addToCartBtn.getAttribute('data-grams') || '';
                    if (!variantId && addToCartBtn.hasAttribute('data-variant-id')) {
                        showCartToast();
                        return;
                    }
                    addToCart(productId, parseInt(input.value, 10), variantId, grams);
                    input.value = 1;
                };
            }
        }

        resetDetailCart();
        attachQuantityHandlers(productId);
    }

    // --- ОСТАЛЬНОЕ (ТОСТЫ, CSRF) ---
    function getCSRFToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    }
    function addToCart(productId, quantity = 1, variantId = null, grams = '') {
        const csrfToken = getCSRFToken();
        // Get current language prefix from URL
        const langPrefix = window.location.pathname.split('/')[1];
        const baseUrl = langPrefix === 'uk' || langPrefix === 'ru' ? `/${langPrefix}` : '';
        
        fetch(`${baseUrl}/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity, variant_id: variantId, grams }),
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
            console.error('Error:', error);
        });
    }

    // --- КАСТОМНАЯ МОДАЛКА ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ ОТЗЫВА ---
    let deleteUrlToGo = null;
    let lastActiveBtn = null;

    document.querySelectorAll('.review-delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            // 1. Сохраняем ссылку для удаления
            deleteUrlToGo = btn.getAttribute('href');
            // 2. Открываем модалку
            document.getElementById('customConfirmModal').classList.add('active');

            // 3. Снимаем активный статус с прошлого, если был
            if (lastActiveBtn) {
                lastActiveBtn.classList.remove('active');
                let icon = lastActiveBtn.querySelector('.review-delete-icon');
                if (icon) icon.src = icon.dataset.brown;
            }

            // 4. Делаем текущую кнопку активной
            btn.classList.add('active');
            let icon = btn.querySelector('.review-delete-icon');
            if (icon) icon.src = icon.dataset.white;
            lastActiveBtn = btn;
        });
    });

    // Закрытие модалки — убираем активную кнопку
    function closeModal() {
        document.getElementById('customConfirmModal').classList.remove('active');
        deleteUrlToGo = null;
        if (lastActiveBtn) {
            lastActiveBtn.classList.remove('active');
            let icon = lastActiveBtn.querySelector('.review-delete-icon');
            if (icon) icon.src = icon.dataset.brown;
            lastActiveBtn = null;
        }
    }
    document.getElementById('cancelDeleteBtn').onclick = closeModal;
    document.getElementById('closeConfirmModal').onclick = closeModal;
    window.addEventListener('keydown', function(e){
        if (e.key === "Escape") closeModal();
    });
    document.getElementById('confirmDeleteBtn').onclick = function() {
        if (deleteUrlToGo) window.location.href = deleteUrlToGo;
    };

    // --- Ховер эффект для иконки удаления ---
    document.querySelectorAll('.review-delete-btn').forEach(btn => {
        const icon = btn.querySelector('.review-delete-icon');
        if (!icon) return;

        btn.addEventListener('mouseenter', function() {
            // Если сейчас не активная кнопка (в модалке уже белая)
            if (!btn.classList.contains('active')) {
                icon.src = icon.dataset.white;
            }
        });
        btn.addEventListener('mouseleave', function() {
            // Если не активная кнопка — возвращаем brown
            if (!btn.classList.contains('active')) {
                icon.src = icon.dataset.brown;
            }
        });
    });

    // --- Интерактивные звёзды рейтинга ---
    const stars = document.querySelectorAll('#ratingStars > .star');
    const ratingInput = document.getElementById('ratingInput');
    let currentRating = 0;

    stars.forEach((star, idx) => {
        star.addEventListener('mouseenter', () => {
            // Подсвечиваем только до наведённой включительно
            stars.forEach((s, i) => {
                if (i <= idx) s.classList.add('selected');
                else s.classList.remove('selected');
            });
        });
        star.addEventListener('mouseleave', () => {
            // Возвращаем к текущему выбранному рейтингу
            stars.forEach((s, i) => {
                if (i < currentRating) s.classList.add('selected');
                else s.classList.remove('selected');
            });
        });
        star.addEventListener('click', () => {
            currentRating = idx + 1;
            ratingInput.value = currentRating;
            // Отразить выбранные
            stars.forEach((s, i) => {
                if (i < currentRating) s.classList.add('selected');
                else s.classList.remove('selected');
            });
        });
    });

// Инициализация текущей подсветки при загрузке (если была ошибка валидации и рейтинг вернулся)
if (ratingInput && ratingInput.value > 0) {
    currentRating = parseInt(ratingInput.value, 10);
    stars.forEach((s, i) => {
        if (i < currentRating) s.classList.add('selected');
        else s.classList.remove('selected');
    });
}

    // --- Счетчик символов для textarea отзыва ---
    function bindCounter(textareaId, counterId, max) {
        var textarea = document.getElementById(textareaId);
        var counter = document.getElementById(counterId);
        if (textarea && counter) {
            textarea.addEventListener("input", function() {
                counter.textContent = textarea.value.length + "/" + max;
            });
            counter.textContent = textarea.value.length + "/" + max;
        }
    }
    bindCounter("id_comment", "charCount", 500);
});
