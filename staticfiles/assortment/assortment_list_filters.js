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
                // Триггерим событие change, чтобы форма автоотправилась
                document.getElementById('filter-form').dispatchEvent(new Event('change'));
            });
        }
    });
}

// === Показываем «недоступные» фильтры внутри каждой группы ===
function setupUnavailableToggle() {
    document.querySelectorAll('.show-unavailable').forEach(btn => {
        const groupId = btn.getAttribute('data-group-id');
        const container = document.getElementById(`group-${groupId}`);
        if (!container) {
            // если вдруг блок не найден — сразу прячем кнопку
            btn.style.display = 'none';
            return;
        }

        // 1) Сразу после загрузки скрываем кнопку, если в группе нет ни одного элемента .unavailable
        const unavailableItems = container.querySelectorAll('.unavailable');
        if (unavailableItems.length === 0) {
            // Нет ни одного «недоступного» <label>, поэтому кнопку прячем
            btn.style.display = 'none';
            return;
        }

        // 2) Если «недоступные» элементы всё-таки есть, навешиваем обработчик, чтобы по клику показать их
        btn.addEventListener('click', () => {
            // Убираем у всех .unavailable внутри этой группы класс hidden
            container.querySelectorAll('.unavailable').forEach(el => {
                el.classList.remove('hidden');
            });
            // и прячем саму кнопку, чтобы её нельзя было нажать повторно
            btn.style.display = 'none';
        });
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

// === Инициализация при загрузке страницы ===
document.addEventListener('DOMContentLoaded', () => {
    initFilterToggles && initFilterToggles();
    setupProducerFilterClicks && setupProducerFilterClicks();
    setupUnavailableToggle && setupUnavailableToggle();
    setupFilterAutoSubmit && setupFilterAutoSubmit();
});
