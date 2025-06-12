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
    const isCurrentlyFavorite = element.querySelector('.fas.fa-star') !== null;

    // Prevent double clicks
    if (element.dataset.processing === 'true') return;
    element.dataset.processing = 'true';

    fetch(`/favorites/toggle/${productId}/`, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                if (response.status === 403 && data.error === 'login_required') {
                    const toastEl = document.getElementById('loginToast');
                    if (toastEl) new bootstrap.Toast(toastEl).show();
                    return Promise.reject('login_required');
                }
                return Promise.reject('server_error');
            });
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        
        if (data.status === 'added') {
            element.innerHTML = '<i class="fas fa-star text-warning"></i>';
            showFavoriteToast(translations.product_added_to_favorites, true);
        } else if (data.status === 'removed') {
            element.innerHTML = '<i class="far fa-star"></i>';
            showFavoriteToast(translations.product_removed_from_favorites, false);
            
            // If in user cabinet, remove the card with animation
            if (window.IS_USER_CABINET) {
                const productCard = element.closest('.product-card');
                if (productCard) {
                    productCard.classList.add('removing');
                    setTimeout(() => {
                        rebuildFavoritesCarousel(true);
                    }, 500);
                }
            }
        }
    })
    .catch(error => {
        if (error === 'login_required') return;
        console.error('Помилка при додаванні в обрані:', error);
        if (error === 'server_error') {
            showFavoriteToast(translations.server_error, false);
        } else {
            showFavoriteToast(translations.error_updating_favorites, false);
        }
    })
    .finally(() => {
        // Remove processing flag after a short delay
        setTimeout(() => {
            element.dataset.processing = 'false';
        }, 500);
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