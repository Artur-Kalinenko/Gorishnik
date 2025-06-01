document.addEventListener('DOMContentLoaded', function () {
    // Повторная инициализация кнопок количества и корзины
    document.querySelectorAll('.product-card').forEach(card => {
        const productId = card.querySelector('.add-to-cart')?.dataset.productId;
        if (productId) {
            attachQuantityHandlers(productId);
        }
    });

    // Добавляем обработчик для избранного
    document.querySelectorAll('.favorite-toggle').forEach(el => {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handleFavoriteToggle(this);
        });
    });
});

function rebuildFavoritesCarousel(shouldFixActiveSlide = false) {
    const container = document.querySelector('.favorites-container');
    if (!container) return;

    const cardWrappers = Array.from(container.querySelectorAll('.product-card'))
        .map(card => card.closest('.col-md-4') || card.closest('.col-sm-12') || card.closest('.col-lg-4'))
        .filter(Boolean);

    if (!cardWrappers.length) {
        const carousel = document.getElementById('favoritesCarousel');
        if (carousel) carousel.remove();

        const parent = container.closest('.card-body');
        const emptyMessage = document.createElement('p');
        emptyMessage.className = 'text-center text-muted mt-3';
        emptyMessage.textContent = 'У вас ще немає обраних товарів.';
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

        const row = document.createElement('div');
        row.className = 'row justify-content-center';

        group.forEach(col => {
            row.appendChild(col);
        });

        item.appendChild(row);
        carouselInner.appendChild(item);
    });

    // Назначение активного слайда
    const allSlides = carouselInner.querySelectorAll('.carousel-item');
    const newActiveIndex = Math.min(oldActiveIndex, allSlides.length - 1);
    if (allSlides[newActiveIndex]) {
        allSlides[newActiveIndex].classList.add('active');
    }

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
                    const cardsInActiveSlide = activeSlide.querySelectorAll('.product-card');
                    if (cardsInActiveSlide.length === 0) {
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
