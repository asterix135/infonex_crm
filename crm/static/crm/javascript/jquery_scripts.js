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


  // quick search logic/ajax call
  function executeQuickSearch(searchString){
    $.ajax({
      url: '/crm/quick_search/',
      type: 'POST',
      data: {'search_terms': searchString,},
      success: function(data){
        $('#main-panel').html(data);
      }
    });
  }

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


  // // Execute quick search when search button clicked
  // $('body').on('click', '#quick-search', function(){
  //   var searchTerms = $('#quick-search-term').val().trim();
  //   if (searchTerms.length > 0) {
  //     executeQuickSearch(searchTerms);
  //   };
  // })
  //
  //
  // // Execute quick search when enter pressed in quick search field
  // $('body').on('keyup', '#quick-search-term', function(event){
  //   if (event.keyCode == 13) {
  //     var searchTerms = $(this).val().trim();
  //     if (searchTerms.length > 0) {
  //       executeQuickSearch(searchTerms);
  //     };
  //   };
  // })
  //
  //
  // AJAX call to load person details page
  $('body').on('click', '.person-detail-link', function(){
    var personId = $(this).attr('person-id');
    $.ajax({
      url: '/crm/person_detail/',
      type: 'GET',
      data: {
        'person_id': personId,
      },
      success: function(data){
        $('#main-panel').html(data);
      }
    });
  })

});
