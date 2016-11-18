$(document).ready(function(){

  // Hide form warnings
  // $('#form-warning').hide();

  // Pulls registration history for delegate on new_delegate_search page
  $('.show-delegate').click(function(){
    var delegate_id;
    delegate_id = $(this).attr('id');
    $.get('/registration/get_registration_history', {id: delegate_id}, function(data){
      $('#buyer-history' + delegate_id).html(data);
    });
  });

  // check that a conference is selected before allowing delegate registration
  $('.register-delegate').click(function(e){
    var conf_id;
    var $event_select_box = $('#id_event');
    conf_id = $('#id_event').val();
    if (conf_id == ''){
      // alert('Please choose a conference');
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
    $('input[name=conf-id]').val(event_selected);
  });

  // Used to get csrftoken in AJAX requests
  // var csrftoken = getCookie('csrftoken');
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  // Submit post on submit
  $('#create-new-conference').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!");  // sanity check
    var csrftoken = getCookie('csrftoken');
    create_conference();
  });

});
