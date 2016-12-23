$(document).ready(function() {
  // alert('hello');

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


  // Execute quick search from sidebar
  $('body').on('click', '#quick-search', function(){
    var searchTerms = $('#quick-search-term').val().trim();
    if (searchTerms.length > 0) {
      $.ajax({
        url: '/crm/quick_search/',
        type: 'POST',
        data: {'search_terms': searchTerms,},
        success: function(data){
          $('#main-panel').html(data);
        }
      });
    };
  })


});
