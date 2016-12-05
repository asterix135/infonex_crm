$(document).ready(function(){

  $('body').on('keyup', '#id_first_name,#id_last_name', function(){
    var charsEntered = $('#id_first_name').val().length +
      $('#id_last_name').val().length;  
    // TODO: I think id_name might be repeated - check
    charsEntered += $('#id_name').val().length;
    console.log(charsEntered);
  })

});
