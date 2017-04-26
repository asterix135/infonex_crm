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
});
