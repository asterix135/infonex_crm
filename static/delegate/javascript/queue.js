$(document).ready(function(){

  $('#spam-add').click(function(){
    $.ajax({
      url: '/crm/submit_registration/',
      type: 'POST'
    })
  })

});
