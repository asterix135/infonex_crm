$(document).ready(function() {

  $('body').on('click', '.upload-file-row', function(){
    $('.upload-file-row').each(function(){
      $(this).removeClass('info');
    });
    $(this).addClass('info');
    var file_id = $(this).attr('file_id');
    $.ajax({
      url: '/marketing/field_matcher/' + file_id,
      type: 'GET',
      success: function(data){
        $('#field-matcher').html(data);
      }
    })
  })

});
