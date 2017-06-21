$(document).ready(function() {
  // Toggles display/hide of sidebar on small canvases
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });


  // Toggle and/or retrieve view of recently viewed contacts
  $('body').on('click', '#icon-toggle-recent-viewed', function(){
    if ($('#recent-contact-list').hasClass('collapse in')){
      $('#recent-contact-list').collapse('hide');
      $('#icon-toggle-recent-viewed').removeClass('glyphicon-chevron-up');
      $('#icon-toggle-recent-viewed').addClass('glyphicon-chevron-down');
    } else {
      $('#icon-toggle-recent-viewed').removeClass('glyphicon-chevron-down');
      $('#icon-toggle-recent-viewed').addClass('glyphicon-chevron-up');
      $('#recent-contact-list').collapse('show');
      $.ajax({
        url: '/crm/get_recent_contacts/',
        type: 'GET',
        success: function(data){
          $('#recent-contact-list').html(data);
        }
      });
    };
  });

  // Change active conference in sidebar
  $('body').on('click', '.sidebar-territory-option', function(){
    var eventAssignmentId = $(this).val();
    // csrfValue comes from ajax_setup.js
    var formHtml = '<form action="/crm/select_active_conference/" method="post">' +
                   '<input name="csrfmiddlewaretoken" value="' + csrfValue + '" type="hidden"/>' +
                   '<input name="event_assignment" value="' + eventAssignmentId + '"/>' +
                   '</form>';
    $(formHtml).appendTo('body').submit();
  });

});
