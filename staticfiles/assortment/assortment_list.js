document.addEventListener('DOMContentLoaded', () => {
    // Анимация появления карточек
    document.querySelectorAll('.product-card').forEach(card => {
        card.classList.add('fade-in');
    });

    // Фильтры с сохранением состояния
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

    // Автоотправка формы при смене фильтров
    document.querySelectorAll('#filter-form input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            document.getElementById('filter-form').submit();
        });
    });

    // Очистка фильтров
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const url = new URL(window.location.href);
            const params = url.searchParams;

            ['filters', 'q', 'discounted', 'new', 'producer'].forEach(key => params.delete(key));
            localStorage.removeItem(OPENED_FILTERS_KEY);

            const queryString = params.toString();
            const target = queryString ? url.pathname + '?' + queryString : url.pathname;
            window.location.href = target;
        });
    }
});
