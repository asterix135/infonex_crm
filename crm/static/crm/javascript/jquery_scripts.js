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
    var newConfId = $(this).val();
    $.ajax({
      url: '/crm/select_active_conference/',
      type: 'POST',
      data: {
        'new_conf_id': newConfId,
      },
      success: function(data){
        $('#territory-selector').html(data);
        console.log('success');
      }
    });
  });

});
