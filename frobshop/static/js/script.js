<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
$(document).ready(function() {
    var location = $('#location').val();
    var checkInDate = $('#checkInDate').val();
    var checkOutDate = $('#checkOutDate').val();
    var adults = $('.single-quantity:eq(0) .pro-qty input').val();
    var roomQuantity = $('.single-quantity:last .pro-qty input').val();

    $.ajax({
      url: '/hotel-search',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        cityCode: cityCode,
        checkInDate: checkInDate,
        checkOutDate: checkOutDate,
        adults: adults,
        roomQuantity: roomQuantity,
        paymentPolicy: 'PAYMENT_POLICY',
        bestRateOnly: 'true'
      }),
      success: function(response) {
        console.log(response);
      },
      error: function(error) {
        console.log(error);
      }
    });
  });
});