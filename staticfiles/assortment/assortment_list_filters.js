// === Плюсики фильтров ===
function initFilterToggles() {
    const OPENED_FILTERS_KEY = 'opened_filter_groups';
    function saveOpenedGroups(openedIds) {
        localStorage.setItem(OPENED_FILTERS_KEY, JSON.stringify(openedIds));
    }
    function getOpenedGroups() {
        try {
            return JSON.parse(localStorage.getItem(OPENED_FILTERS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }
    let openedGroups = getOpenedGroups();
    document.querySelectorAll('.filter-header').forEach(header => {
        const groupId = header.dataset.groupId;
        const options = document.getElementById(`group-${groupId}`);
        const icon = document.getElementById(`icon-${groupId}`);

        if (openedGroups.includes(groupId)) {
            options.style.display = 'block';
            icon.textContent = '−';
        }

        header.addEventListener('click', () => {
            const isOpen = options.style.display === 'block';
            options.style.display = isOpen ? 'none' : 'block';
            icon.textContent = isOpen ? '+' : '−';
            if (isOpen) {
                openedGroups = openedGroups.filter(id => id !== groupId);
            } else {
                openedGroups.push(groupId);
            }
            saveOpenedGroups(openedGroups);
        });
    });
}

// === Картинки-производители ===
function setupProducerFilterClicks() {
    document.querySelectorAll('input[name="producer"]').forEach(input => {
        const label = input.closest('label');
        if (label) {
            label.addEventListener('click', () => {
                input.checked = !input.checked;
                document.getElementById('filter-form').dispatchEvent(new Event('change'));
            });
        }
    });
}

// === Обычная отправка фильтров ===
function setupFilterAutoSubmit() {
    const form = document.getElementById('filter-form');
    if (!form) return;
    // Автоотправка формы при изменении любого фильтра
    form.querySelectorAll('input[type="checkbox"], select').forEach(input => {
        input.addEventListener('change', function() {
            form.submit();
        });
    });
    // Кнопка очистки фильтров
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            form.querySelectorAll('input[type="checkbox"]').forEach(input => input.checked = false);
            form.submit();
        });
    }
}

// === Инициализация при загрузке ===
document.addEventListener('DOMContentLoaded', () => {
//    initAssortmentPage && initAssortmentPage();
    initFilterToggles && initFilterToggles();
    setupProducerFilterClicks && setupProducerFilterClicks();
    setupFilterAutoSubmit();
});
