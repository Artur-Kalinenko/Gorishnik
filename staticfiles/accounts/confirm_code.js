document.addEventListener('DOMContentLoaded', function () {
    const resendBtn = document.querySelector('[data-code-resend]');
    if (!resendBtn) return;

    const form = document.getElementById('confirm-form');
    const hiddenResendInput = document.getElementById('resend-hidden-field');
    const sentAtStr = resendBtn.dataset.sentAt;
    const isFirst = resendBtn.dataset.isFirst === 'true';
    const delaySeconds = 60;
    let remaining = 0;

    // Создаём и вставляем span прямо после кнопки
    let timerSpan = document.createElement('span');
    timerSpan.classList.add('ms-2', 'text-muted');
    resendBtn.parentNode.insertBefore(timerSpan, resendBtn.nextSibling);

    // Вычисляем сколько осталось
    if (!isFirst && sentAtStr) {
        const sentAt = new Date(sentAtStr);
        const now = new Date();
        remaining = Math.max(delaySeconds - Math.floor((now - sentAt) / 1000), 0);
    }

    function updateTimerDisplay() {
        if (remaining > 0) {
            resendBtn.disabled = true;
            timerSpan.textContent = `Можна надіслати повторно через ${remaining} сек.`;
        } else {
            resendBtn.disabled = false;
            timerSpan.textContent = '';
        }
    }

    updateTimerDisplay();

    if (remaining > 0) {
        const interval = setInterval(() => {
            remaining--;
            updateTimerDisplay();
            if (remaining <= 0) clearInterval(interval);
        }, 1000);
    }

    resendBtn.addEventListener('click', function () {
        if (resendBtn.disabled) return;

        if (hiddenResendInput) {
            hiddenResendInput.disabled = false;
        }

        form.submit();
    });
});
