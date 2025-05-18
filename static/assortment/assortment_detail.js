document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.grams-button').forEach(button => {
        button.addEventListener('click', event => {
            const price = event.target.getAttribute('data-price');
            const priceDisplay = document.getElementById('price-display');

            console.log(`Кнопка нажата:`, event.target);
            console.log(`Обновление ціни: ${price}`);

            if (priceDisplay) {
                priceDisplay.textContent = `${price}`;
                console.log("Ціна успішно оновлена!");
            } else {
                console.error(`Елемент з ID price-display не знайдено!`);
            }
        });
    });
});
