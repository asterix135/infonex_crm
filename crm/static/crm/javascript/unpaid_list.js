// Javascript for project home page
// TODO: Should be combined with similar script in home.js
$(document).ready(function() {

  $('body').on('click', '.glyph-button', function(){
    var toggleObject = $(this).attr('toggle-obj');
    if ($(this).hasClass('glyphicon-chevron-down')) {
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $(toggleObject).addClass('in');

    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $(toggleObject).removeClass('in');
    };
  });

});
