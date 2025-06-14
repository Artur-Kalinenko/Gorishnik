document.addEventListener('DOMContentLoaded', function () {
    // Повторная инициализация кнопок количества и корзины
    document.querySelectorAll('.product-card').forEach(card => {
        const productId = card.querySelector('.add-to-cart')?.dataset.productId;
        if (productId) {
            attachQuantityHandlers(productId);
        }
    });
});

// Функция для перестроения карусели
function rebuildFavoritesCarousel(shouldFixActiveSlide = false) {
    const container = document.querySelector('.favorites-container');
    if (!container) return;

    // Remove any cards that are in the process of being removed
    const removingCards = container.querySelectorAll('.product-card.removing');
    removingCards.forEach(card => {
        if (card.style.opacity === '0') {
            card.remove();
        }
    });

    const cardWrappers = Array.from(container.querySelectorAll('.product-card:not(.removing)'))
        .map(card => card.closest('.col-auto') || card)
        .filter(Boolean);

    if (!cardWrappers.length) {
        const carousel = document.getElementById('favoritesCarousel');
        if (carousel) {
            carousel.style.display = 'none';
        }

        const parent = container.closest('.card-body');
        // Remove any existing empty message
        const existingMessage = parent.querySelector('.text-muted, .no-favorites-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Определяем язык страницы
        let lang = document.documentElement.getAttribute('lang') || 'uk';
        let emptyText = 'У вас ще немає обраних товарів.';
        if (lang.startsWith('ru')) {
            emptyText = 'У вас пока нет избранных товаров.';
        } else if (lang.startsWith('en')) {
            emptyText = 'You have no favorite products yet.';
        }

        const emptyMessage = document.createElement('p');
        emptyMessage.className = 'text-center no-favorites-message mt-3';
        emptyMessage.textContent = emptyText;
        parent.appendChild(emptyMessage);
        return;
    }

    const carouselInner = document.querySelector('.carousel-inner');
    if (!carouselInner) return;

    const oldActiveIndex = Array.from(carouselInner.children).findIndex(item => item.classList.contains('active'));

    carouselInner.innerHTML = '';

    const chunks = [];
    for (let i = 0; i < cardWrappers.length; i += 3) {
        chunks.push(cardWrappers.slice(i, i + 3));
    }

    chunks.forEach((group, index) => {
        const item = document.createElement('div');
        item.className = 'carousel-item';
        if (index === 0) {
            item.classList.add('active');
        }

        const row = document.createElement('div');
        row.className = 'row justify-content-center';

        group.forEach(col => {
            if (col) {
                row.appendChild(col);
            }
        });

        item.appendChild(row);
        carouselInner.appendChild(item);
    });

    // Управление видимостью стрелок
    const carouselControls = document.querySelectorAll('#favoritesCarousel .carousel-control-prev, #favoritesCarousel .carousel-control-next');
    if (cardWrappers.length <= 3) {
        carouselControls.forEach(btn => btn.style.display = 'none');
    } else {
        carouselControls.forEach(btn => btn.style.display = '');
    }

    // Если надо, корректируем текущий слайд
    if (shouldFixActiveSlide) {
        setTimeout(() => {
            const carouselElement = document.getElementById('favoritesCarousel');
            if (carouselElement) {
                const carousel = bootstrap.Carousel.getInstance(carouselElement) || new bootstrap.Carousel(carouselElement);
                const activeSlide = carouselElement.querySelector('.carousel-item.active');

                if (activeSlide) {
                    const cardsInActiveSlide = activeSlide.querySelectorAll('.product-card:not(.removing)');
                    if (cardsInActiveSlide.length === 0) {
                        const allSlides = carouselElement.querySelectorAll('.carousel-item');
                        const currentIndex = Array.from(allSlides).indexOf(activeSlide);
                        const newIndex = Math.max(0, currentIndex - 1);
                        if (newIndex !== currentIndex) {
                            carousel.to(newIndex);
                        }
                    }
                }
            }
        }, 0);
    }
}
