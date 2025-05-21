// EventBooker Ana JavaScript Dosyası

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltip'leri etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Kart numarası formatla
    const cardNumberInput = document.getElementById('id_card_number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = value.match(new RegExp('.{1,4}', 'g')).join(' ');
            }
            e.target.value = value;
        });
    }
    
    // Son kullanma tarihi formatla
    const expiryDateInput = document.getElementById('id_expiry_date');
    if (expiryDateInput) {
        expiryDateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
    
    // CVV sadece sayı kabul et
    const cvvInput = document.getElementById('id_cvv');
    if (cvvInput) {
        cvvInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
        });
    }
    
    // Rezervasyon butonunu tıklandığında onay iste
    const reservationForms = document.querySelectorAll('.reservation-form');
    reservationForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Bu etkinlik için rezervasyon yapmak istediğinize emin misiniz?')) {
                e.preventDefault();
            }
        });
    });
}); 