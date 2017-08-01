$(document).ready(function() {

  $('body').on('click', 'tr', function(){
    var file_id = $(this).attr('file_id');
    console.log('selected a tr for file # ' + file_id);
  })

});
