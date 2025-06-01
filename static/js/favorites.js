// Function to show favorite toast notification
function showFavoriteToast(message, isAdded) {
    const toastEl = document.getElementById('favorite-toast');
    const toastMessage = document.getElementById('favorite-toast-message');

    if (!toastEl || !toastMessage) return;

    toastMessage.textContent = message;
    toastEl.classList.remove('bg-success', 'bg-danger');
    toastEl.classList.add(isAdded ? 'bg-success' : 'bg-danger');

    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 5000 });
    toast.show();
}

// Function to handle favorite toggle
function handleFavoriteToggle(element) {
    const productId = element.dataset.productId;

    fetch(`/favorites/toggle/${productId}/`, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
    .then(response => {
        if (response.status === 403) {
            const toastEl = document.getElementById('loginToast');
            if (toastEl) new bootstrap.Toast(toastEl).show();
            return;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        
        if (data.status === 'added') {
            element.innerHTML = '<i class="fas fa-star text-warning"></i>';
            showFavoriteToast('Товар додано в обране', true);
        } else if (data.status === 'removed') {
            element.innerHTML = '<i class="far fa-star"></i>';
            showFavoriteToast('Товар видалено з обраного', false);
            
            // If in user cabinet, remove the card
            if (window.IS_USER_CABINET) {
                const cardWrapper = element.closest('.col-md-4') || element.closest('.col-sm-12') || element.closest('.col-lg-4');
                if (cardWrapper) {
                    cardWrapper.remove();
                    rebuildFavoritesCarousel(true);
                }
            }
        }
    })
    .catch(error => {
        console.error('Помилка при додаванні в обрані:', error);
    });
}

// Initialize favorite toggles
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.favorite-toggle, .favorite-toggle-detail').forEach(el => {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handleFavoriteToggle(this);
        });
    });
}); 