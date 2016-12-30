$(document).ready(function() {

  $('body').on('click', '#btn-toggle-adv-search', function(){
    console.log('triggered function');
    if ($('#icon-toggle-adv-search').hasClass('glyphicon-chevron-down')) {
      $('#icon-toggle-adv-search').removeClass('glyphicon-chevron-down');
      $('#icon-toggle-adv-search').addClass('glyphicon-chevron-up');
    } else {
      $('#icon-toggle-adv-search').removeClass('glyphicon-chevron-up');
      $('#icon-toggle-adv-search').addClass('glyphicon-chevron-down');
    }
  });
});
