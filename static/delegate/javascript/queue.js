$(document).ready(function(){

  $('#spam-add').click(function(){
    $.ajax({
      url: '/crm/submit_registration/',
      type: 'POST'
    })
  });

  $('body').on('click', '.process-queue', function(){
    const queueId = $(this).attr('queue-id');
    console.log(queueId);
  })

});
