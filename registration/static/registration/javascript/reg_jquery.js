$(document).ready(function(){

  // Global variables to access when choosing 'proceed' from modal
  var formToSubmit = '';

  // Pulls registration history for delegate on new_delegate_search page
  // Also inserts conference_id into hidden input field
  $('body').on('click', '.show-delegate', function(){
    var delegate_id = $(this).attr('id');
    $.get('/registration/get_registration_history',
          {id: delegate_id}, function(data){
            $('#buyer-history' + delegate_id).html(data);
          });
    var confId = $('#id_event').val()
    $('input[name=conf_id]').val(confId);
  });


  // check that a conference is selected before allowing delegate registration
  $('body').on('click', '.register-delegate', function(e){
    var $event_select_box = $('#id_event');
    var submissionType = $(this).attr('register-type');
    var customerId = $(this).attr('customer-id');
    var confId = $('#id_event').val();
    formToSubmit = '#' + submissionType + customerId + ' form'
    if (confId == ''){
      $event_select_box.css('border-color', '#963634');
      $('.form-warning').show();
      $('html, body').animate({
        scrollTop: $('#id_event').offset().top - 180
      });
      // e.preventDefault();
    } else {
      // e.preventDefault();
      $.ajax({
        url: '/delegate/conf_has_regs/',
        type: 'POST',
        data: {
          'conf_id': confId,
        },
        success: function(data){
          var okToRegister = $('#first-reg', data).val() == 'true';
          if (okToRegister) {
            $(formToSubmit).submit();
          } else {
            $('#first-registration-modal').html(data);
            $('#confSetupModal').modal('show');
          };
        }
      });
    };
  });


  $('body').on('click', '#create-new-delegate-button', function(e){
    var $event_select_box = $('#id_event');
    // var submissionType = $(this).attr('register-type');
    // var customerId = $(this).attr('customer-id');
    var confId = $('#id_event').val();
    formToSubmit = '#' + $(this).parent().attr('id');
    if (confId == ''){
      $event_select_box.css('border-color', '#963634');
      $('.form-warning').show();
      $('html, body').animate({
        scrollTop: $('#id_event').offset().top - 180
      });
    } else {
      $.ajax({
        url: '/delegate/conf_has_regs/',
        type: 'POST',
        data: {
          'conf_id': confId,
        },
        success: function(data){
          var okToRegister = $('#first-reg', data).val() == 'true';
          if (okToRegister) {
            $(formToSubmit).submit();
          } else {
            $('#first-registration-modal').html(data);
            $('#confSetupModal').modal('show');
          };
        }
      });
    };
  });



  // Respond to button click to go to edit conference page
  $('body').on('click', '#edit-event', function(){
    var newConfId = $('#id_event').val();
    $(location).attr('href', '/registration/conference/?action=edit&id=' + newConfId);
  });


  // respond to button click to proceed with registration (from modal)
  $('body').on('click', '#proceed-with-registration', function(){
    $(formToSubmit).submit();
  });


  // clear border color when event is selected
  // update all hidden fields
  $('#id_event').change(function(){
    var event_selected = $(this).val();
    $('#id_event').css('border-color', '');
    $('.form-warning').hide();
    $('input[name=conf_id]').val(event_selected);
  });


  // Main logic for form submission on new_delegate_search
  function searchDels() {
    var eventId = $('#id_event').val();
    $.ajax({
      url: '/registration/search_dels/',
      type: 'POST',
      data: {first_name: $('#id_first_name').val(),
             last_name: $('#id_last_name').val(),
             company: $('#id_company').val(),
             postal_code: $('#id_postal_code').val(),
             event: $('#id_event').val(),
            //  csrfmiddlewaretoken: csrftoken
           },
      success: function(data) {
        $('#match-del-list').html(data);
      }
    })
  };

  // Submit search function for new_delegate_search
  $('#submit-delegate-search').on('submit', function(event){
    event.preventDefault();
    searchDels();
  });

  // Load ajax panels on index page
  $('body').on('click', '.ajax-load', function(){
    var ajaxPayload = $(this).attr('ajax-target');
    $.ajax({
      url: '/registration/index_panel/',
      type: 'GET',
      data: {
        'panel': ajaxPayload,
      },
      success: function(data) {
        $('#ajax-content').html(data);
      }
    });
  });

});
