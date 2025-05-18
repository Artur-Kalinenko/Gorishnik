document.addEventListener('DOMContentLoaded', () => {
    const selectedVariants = {};

    document.querySelectorAll('.grams-button').forEach(button => {
        button.addEventListener('click', event => {
            const productId = event.target.getAttribute('data-product-id');
            const variantId = event.target.getAttribute('data-variant-id');
            const price = event.target.getAttribute('data-price');
            const priceDisplay = document.getElementById(`price-display-${productId}`);

            selectedVariants[productId] = variantId;

            if (priceDisplay) {
                priceDisplay.textContent = `${price} ₴`;
            }

            document.querySelectorAll(`.grams-button[data-product-id="${productId}"]`).forEach(btn => {
                btn.classList.remove('selected');
            });
            event.target.classList.add('selected');

            const selectBtn = document.getElementById(`select-variant-${productId}`);
            if (selectBtn) selectBtn.style.display = 'none';

            if (!document.getElementById(`controls-${productId}`)) {
                const container = document.createElement('div');
                container.className = 'd-flex align-items-center justify-content-center btn-group-container';
                container.id = `controls-${productId}`;
                container.innerHTML = `
                    <button class="btn btn-primary decrease-quantity" data-product-id="${productId}">−</button>
                    <input type="number" min="1" value="1" id="quantity-input-${productId}" class="quantity-input text-center" readonly>
                    <button class="btn btn-primary increase-quantity" data-product-id="${productId}">+</button>
                    <button class="btn btn-primary add-to-cart" data-product-id="${productId}" data-variant-id="${variantId}">В корзину</button>
                `;

                const cardBody = event.target.closest('.card-body');
                cardBody.appendChild(container);

                attachQuantityHandlers(productId);
            }
        });
    });

    function attachQuantityHandlers(productId) {
        const decreaseBtn = document.querySelector(`#controls-${productId} .decrease-quantity`);
        const increaseBtn = document.querySelector(`#controls-${productId} .increase-quantity`);
        const addToCartBtn = document.querySelector(`#controls-${productId} .add-to-cart`);

        decreaseBtn?.addEventListener('click', () => {
            const input = document.getElementById(`quantity-input-${productId}`);
            const value = parseInt(input.value, 10);
            if (value > 1) input.value = value - 1;
        });

        increaseBtn?.addEventListener('click', () => {
            const input = document.getElementById(`quantity-input-${productId}`);
            input.value = parseInt(input.value, 10) + 1;
        });

        addToCartBtn?.addEventListener('click', event => {
            const input = document.getElementById(`quantity-input-${productId}`);
            const quantity = input.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            let variantId = selectedVariants[productId] || event.target.dataset.variantId;

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quantity: quantity, variant_id: variantId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.session_id) {
                    localStorage.setItem('session_id', data.session_id);
                }
                alert(data.message);
                input.value = 1;
            })
            .catch(error => {
                console.error('Помилка при додаванні в корзину:', error);
            });
        });
    }

    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'scale(1.05)';
            card.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        });
        card.addEventListener('mouseout', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = 'none';
        });
    });
});
