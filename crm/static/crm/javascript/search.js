$(document).ready(function() {

  $('body').on('click', '#btn-toggle-adv-search', function(){
    console.log('triggered function');
    if ($(this).hasClass('glyphicon-chevron-down')) {
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
    };
    $('#search-panel').toggle();
  });
});
