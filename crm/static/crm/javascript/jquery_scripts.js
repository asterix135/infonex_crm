$(document).ready(function() {

  $("#checkAllBoxes").click(function(){
    var checked_status = this.checked;
    $("input[name='reflag']").each(function(){
      this.checked = checked_status;
    });
  });

  $("#masterFlag").change(function(){
    var masterFlagValue = $(this).val() - 1;
    $("select[name='personFlag']").each(function(){
      this.selectedIndex = masterFlagValue;
    })
    console.log('masterFlagValue');
  });


  // Toggles display/hide of sidebar on small canvases
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });


  // Toggle and/or retrieve view of recently viewed contacts
  $('body').on('click', '#toggle-recently-viewed', function(){
    if ($('#recent-contact-list').hasClass('collapse in')){
      $('#recent-contact-list').collapse('hide');
    } else {
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


});
