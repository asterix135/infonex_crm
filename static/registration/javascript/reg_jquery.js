$(document).ready(function(){
  // AJAX CSRF Setup
  // CSRF code
  function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (i; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });


  // Pulls registration history for delegate on new_delegate_search page
  // Also inserts conference_id into hidden input field
  $('body').on('click', '.show-delegate', function(){
    var delegate_id = $(this).attr('id');
    $.get('/registration/get_registration_history',
          {id: delegate_id}, function(data){
            $('#buyer-history' + delegate_id).html(data);
          });
    var confId = $('#id_event').val()
    console.log('conf')
    $('input[name=conf_id]').val(confId);
  });


  // check that a conference is selected before allowing delegate registration
  $('body').on('click', '.register-delegate', function(e){
    var $event_select_box = $('#id_event');
    var conf_id = $('#id_event').val();
    if (conf_id == ''){
      $event_select_box.css('border-color', '#963634');
      $('.form-warning').show();
      $('html, body').animate({
        scrollTop: $('#id_event').offset().top - 180
      });
      e.preventDefault();
    };
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
    console.log(eventId);
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

});
