$(document).ready(function() {

  $('body').on('click', '#btn-toggle-adv-search', function(){
    if ($(this).hasClass('glyphicon-chevron-down')) {
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      // $('#search-panel').collapse('show');
      $('.advanced-search-panel').collapse('show');

    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      // $('#search-panel').collapse('hide');
      $('.advanced-search-panel').collapse('hide');

    };
  });

  function clearSearchBoxes(){
    $('#id_name').val('');
    $('#id_title').val('');
    $('#id_dept').val('');
    $('#id_company').val('');
    $('#id_state_province').val('');
    $('#id_phone_number').val('');
    $('#id_past_customer').val('');
  };

  // button action to clear search form
  $('body').on('click', '#resetSearchForm', function(){
    clearSearchBoxes();
  });

});
