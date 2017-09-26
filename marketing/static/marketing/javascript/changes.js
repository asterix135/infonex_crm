$(document).ready(function() {

  $('body').on('click', '.change-row', function(){
    $.ajax({
      url: '/marketing/change_details/',
      type: 'GET',
      // data: {},
      success: function(data) {
        $('#comparison-panel').html(data);
      }
    })
  });

});
