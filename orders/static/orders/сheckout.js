document.addEventListener('DOMContentLoaded', function () {
    const deliveryMethod = document.getElementById('delivery-method');
    const addressField = document.getElementById('address-field');

    // Показывает или скрывает поле адреса в зависимости от способа доставки
    function toggleAddressField() {
        if (deliveryMethod.value === 'pickup') {
            addressField.parentElement.style.display = 'none';
            addressField.value = '';
        } else {
            addressField.parentElement.style.display = 'block';
        }
    }

    if (deliveryMethod && addressField) {
        toggleAddressField();
        deliveryMethod.addEventListener('change', toggleAddressField);
    }
});