document.addEventListener('DOMContentLoaded', () => {
    // Обработка кликов по кнопкам граммовки
    document.querySelectorAll('.grams-button').forEach(button => {
        button.addEventListener('click', event => {
            const price = event.target.getAttribute('data-price');
            const priceDisplay = document.getElementById('price-display');

            console.log(`Кнопка нажата:`, event.target);
            console.log(`Обновление ціни: ${price}`);

            // Обновляем отображаемую цену
            if (priceDisplay) {
                priceDisplay.textContent = `${price}`;
                console.log("Ціна успішно оновлена!");
            } else {
                console.error(`Елемент з ID price-display не знайдено!`);
            }
        });
    });
});
