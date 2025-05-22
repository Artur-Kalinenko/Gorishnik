document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.grams-button');
    const priceDisplay = document.getElementById('price-display');
    const mainImage = document.getElementById('mainImage');
    const thumbnails = document.querySelectorAll('.thumbnail-img');

    // Обновление главного изображения
    window.changeMainImage = function(thumbnail) {
        if (mainImage) {
            mainImage.src = thumbnail.src;
        }

        thumbnails.forEach(img => img.classList.remove('active-thumbnail'));
        thumbnail.classList.add('active-thumbnail');
    };

    // Обновление цены при выборе граммовки
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const price = button.dataset.price;
            const oldPrice = button.dataset.oldPrice;

            if (priceDisplay) {
                if (oldPrice && oldPrice !== "None") {
                    priceDisplay.innerHTML = `
                        <p class="mb-1 text-muted text-decoration-line-through">${oldPrice} ₴</p>
                        <p class="fw-bold text-danger">${price} ₴</p>
                    `;
                } else {
                    priceDisplay.innerHTML = `
                        <p class="fw-bold">${price} ₴</p>
                    `;
                }
            }
        });
    });
});
