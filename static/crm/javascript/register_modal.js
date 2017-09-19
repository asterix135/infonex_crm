$(document).ready(function() {
  // Globals
  const PAID_STATUS_VALUES = ['DP', 'SP', 'DX'];
  const SPEAKER_VALUES = ['K', 'KX',];


  // Fix ids for input fields in modal to make them unique
  $('#registrationModal input, #registrationModal select, #registrationModal textarea').each(function(){
    if ($(this).attr('id').slice(0,2) == 'id') {
      $(this).attr('id', 'reg_fld' + $(this).attr('id').slice(2));
    } else {
      $(this).attr('id', 'reg_fld_' + $(this).attr('id'));
    };
  });


  // Pre-populate modal when called
  $('body').on('click', '#btn-start-registration', function(){
    var nameArray = $('#id_name').val().split(' ');
    $('#reg_fld_first_name').val(nameArray[0]);
    $('#reg_fld_last_name').val(nameArray.slice(1).join(' '));

    $('#reg_fld_title').val($('#id_title').val());
    $('#reg_fld_email1').val($('#id_email').val());
    $('#reg_fld_email2').val($('#id_email_alternate').val());
    $('#reg_fld_phone1').val($('#id_phone').val());
    $('#reg_fld_phone2').val($('#id_phone_alternate').val());
    $('#reg_fld_name').val($('#id_company').val());
    $('#reg_fld_city').val($('#id_city').val());

    $('#registrationModal').modal('show');
  });


  // Respond to choice of Event
  $('body').on('change', '#reg_fld_event', function(){
    let eventId = $(this).val();
    let personId = $('#person_id').val();
    $.ajax({
      url: '/crm/reg_options/',
      type: 'GET',
      data: {
        'event_id': eventId,
        'person_id': personId,
      },
      success: function(data, textStatus, xhr){
        if (xhr.status == 202) {
          $('#conf-select-error').addClass('in');
        } else {
          $('#conf-select-error').removeClass('in');
          $('#event-options').html(data);
        }
      }
    })
  });


  // Respond to choice of registration status
  $('body').on('change', '#reg_fld_registration_status', function(){
    var regStatus = $(this).val();
    if ($.inArray(regStatus, PAID_STATUS_VALUES) > -1) {
      $('#payment-method').addClass('in');
      $('#payment-warning').addClass('in');
    } else {
      $('#payment-method').removeClass('in');
    };
    if ($.inArray(regStatus, SPEAKER_VALUES) > -1) {
      $('#payment-option-details').removeClass('in');
    } else {
      $('#payment-option-details').addClass('in');
    };
  })


  // Submit forms
  $('body').on('click', '#download-reg-form', function(){
    alert('Not yet coded');
  });



  // Submit form generation
  $('body').on('click', '#submit-registration', function(){
    alert('Not yet coded');
    // 1. Verify form
    // 2. Submit via Ajax
    // 3. If successful: update contact history section
  });

});
