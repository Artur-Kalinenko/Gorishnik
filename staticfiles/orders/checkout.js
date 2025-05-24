$(function () {
    console.log("checkout.js loaded");

    // 🎯 Маска телефона
    const phoneInput = document.getElementById("order-phone-input");
    if (phoneInput) {
        Inputmask({
            mask: "+380 (99) 999-99-99",
            placeholder: "_",
            showMaskOnHover: false,
            showMaskOnFocus: true,
            clearIncomplete: true,
        }).mask(phoneInput);
    }

    // 📦 Логика отображения полей
    const deliveryRadios = document.querySelectorAll('input[name="delivery_method"]');
    const novaPoshtaFields = document.getElementById('nova-poshta-fields');
    const ukrPoshtaFields = document.getElementById('ukr-poshta-fields');

    function toggleFields() {
        const selected = document.querySelector('input[name="delivery_method"]:checked').value;
        novaPoshtaFields.style.display = selected === 'nova_poshta' ? 'block' : 'none';
        ukrPoshtaFields.style.display = selected === 'ukr_poshta' ? 'block' : 'none';
    }

    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', toggleFields);
    });

    toggleFields(); // initial

    // 🏙️ Select2 (city)
    $('#id_city').select2({
        placeholder: 'Оберіть місто',
        ajax: {
            url: '/delivery/city-autocomplete/',
            dataType: 'json',
            delay: 250,
            data: params => ({ q: params.term }),
            processResults: data => ({ results: data }),
            cache: true
        }
    });

    $('#id_warehouse').select2({
        placeholder: 'Оберіть відділення',
        ajax: {
            url: '/delivery/warehouse-autocomplete/',
            dataType: 'json',
            delay: 250,
            data: params => ({
                city_ref: $('#hidden_city_ref').val()
            }),
            processResults: data => ({ results: data }),
            cache: true
        }
    });

    $('#id_city').on('select2:select', function (e) {
        $('#hidden_city_ref').val(e.params.data.id);
        $('#id_warehouse').val(null).trigger('change');
    });

    $('#id_warehouse').on('select2:select', function (e) {
        $('#hidden_warehouse_ref').val(e.params.data.id);
    });
});
