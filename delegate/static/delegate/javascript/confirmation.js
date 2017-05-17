$(document).ready(function(){

  var newEmailField = `
  <div class="input-group">
    <span class="input-group-btn">
      <button class="btn btn-default activate-email" type="button" id="add_to" foo="bar"><span class="glyphicon glyphicon-plus"></span></button>
    </span>
    <input type="email" name="to_field[]" class="form-control" placeholder="Add" disabled="" />
  </div>
  `

  // Show email modal on page load
  var regStatus = $('#registration-type').val();
  var regAction = $('#reg-action-type').val();
  if (regStatus != 'K' && regStatus != 'KX' && regAction == 'new') {
    $('#email-confirmation-modal').modal('show');
  };

  // Send email confirmation
  $('body').on('click', '#send-email', function(){
    // Verify stuff here
    var regDetailId = $('#reg-id').val();
    var emailMessage = $('#email_message').val();
    var emailSubject = $('#email_subject').val();
    var emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}$/;
    var toList = [];
    var ccList = [];
    var bccList = [];
    $('input[name="to_field"]').each(function(){
      if (!$(this).prop('disabled')){
        if (emailPattern.test($(this).val())) {
          toList.push($(this).val());
        };
      };
    });
    $('input[name="cc_field"]').each(function(){
      if (!$(this).prop('disabled')){
        if (emailPattern.test($(this).val())) {
          ccList.push($(this).val());
        };
      };
    });
    $('input[name="bcc_field"]').each(function(){
      if (!$(this).prop('disabled')){
        if (emailPattern.test($(this).val())) {
          bccList.push($(this).val());
        };
      };
    });
    // Verify that there is an address, subject & body
    if (toList.length > 0  && emailSubject.length > 14 && emailMessage.length > 49) {
      $.ajax({
        url: '/delegate/send_conf_email/',
        type: 'POST',
        data: {
          'reg_id': regDetailId,
          'email_message': emailMessage,
          'email_subject': emailSubject,
          'to_list': toList,
          'cc_list': ccList,
          'bcc_list': bccList,
        },
        success: function(){
          $('#email-confirmation-modal').modal('hide');
        }
      });
    } else {
      $('#modal-error-warnings').html(
        `<h5 class="errorlist">
           Please fix the errors indicated below
         </h5>`
      )
      if (emailMessage.length < 50) {
        $('#email-message-warnings').html(
          `<h5 class="errorlist">
             Message must be at least 50 characters long
           </h5>`
        );
        // $('#email_message').focus();
        $('#email-confirmation-modal').animate({
          scrollTop: $('#email_message').offset().top
        });
      };
      if (emailSubject.length < 15) {
        $('#email-subject-warnings').html(
          `<h5 class="errorlist">
             Subject line must be at least 15 characters long
           </h5>`
        );
        $('#email-confirmation-modal').animate({
          scrollTop: $('#email_subject').offset().top - 180
        });
      };
      if (toList.length == 0) {
        $('#to-address-warnings').html(
          `<h5 class="errorlist">
             Must include at least one valid To: address
           </h5>`
        );
        $('#email-confirmation-modal').animate({
          scrollTop: $('#to-address-list').offset().top - 180
        });
      };
      if (emailSubject.length < 15) {
        $('#email-subject-warnings').html(
          `<h5 class="errorlist">
             Subject line must be at least 15 characters long
           </h5>`
        );
      };
    };
  });


  // Disable email address
  $('body').on('click', '.deactivate-email', function(){
    $(this).children('span').removeClass('glyphicon-remove');
    $(this).children('span').addClass('glyphicon-plus');
    $(this).removeClass('deactivate-email');
    $(this).addClass('activate-email');
    $(this).parent().next('input').prop('disabled', true);
    if ($(this).parent().next('input').val() != ''){
      var oldEmail = $(this).parent().next('input').val();
    } else {
      var oldEmail = 'Add'
    };
    $(this).parent().next('input').prop('placeholder', oldEmail);
    $(this).parent().next('input').val('');
  });


  // Enable email address and add new blank field if needed
  $('body').on('click', '.activate-email', function(){
    $(this).children('span').removeClass('glyphicon-plus');
    $(this).children('span').addClass('glyphicon-remove');
    $(this).removeClass('activate-email');
    $(this).addClass('deactivate-email');
    $(this).parent().next('input').removeAttr('disabled');
    if ($(this).parent().next('input').prop('placeholder') != 'Add'){
      var newEmail = $(this).parent().next('input').prop('placeholder');
    } else {
      var newEmail = '';
    };
    $(this).parent().next('input').val(newEmail);
    var numOfEmails = $(this).parent().parent().parent().children('.input-group').length;
    var isLast = $(this).parent().parent().is(':last-child');
    if (isLast && numOfEmails < 7){
      $(this).parent().parent().parent().append(newEmailField);
      var newName = $(this).parent().next('input').prop('name');
      $(this).parent().parent().parent().find('input').last().attr('name', newName);
    } else if (isLast && !$(this).parent().parent().parent().find('h5').length){
      $(this).parent().parent().parent().append(
        '<h5 class="errorlist">Cannot add more addresses</h5>'
      )
    };
  });
});
