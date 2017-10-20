$(document).ready(function(){
  /////////////////
  // Global variables
  /////////////////
  var newEmailId = 0;

  ////////////////
  // Functions dealing with submit buttons
  ////////////////
  $('body').on('click', '#btn-all-ok', function(){
    $(this).attr('id', 'btn-all-not-ok');
    $(this).text('Wait a second...');
    $(this).removeClass('btn-info');
    $(this).addClass('btn-success');
    $('<button id="btn-send-email" class="btn btn-warning col-sm-6" type="submit">Send Email</button>').insertAfter(this);
  });

  $('body').on('click', '#btn-all-not-ok', function(){
    $(this).attr('id', 'btn-all-ok');
    $(this).text('Everything looks good');
    $(this).removeClass('btn-success');
    $(this).addClass('btn-info');
    $('#btn-send-email').remove();
  });

  $('body').on('click', '#btn-send-email', function(){
    var emptyFields = $('input[required]').filter(function(){
      return $(this).val().trim() == '';
    }).length;
    if (emptyFields == 0) {
      $('#doNotCloseModal').modal('show');
    };
  });

  ///////////////////
  // Functions dealing with removing email from list
  ///////////////////
  $('body').on('click', '.delete-step-1', function(){
    var rowId = $(this).attr('related-email');
    $(this).removeClass('delete-step-1 btn-default');
    $(this).addClass('delete-step-2 btn-warning');
    $(this).text('Remove');
    $('<button class="btn btn-success btn-restore" type="button" related-email="' + rowId + '">Oops..</button>').insertAfter(this);
  });

  $('body').on('click', '.btn-restore', function(){
    var rowId = $(this).attr('related-email');
    var removeBtn = $('#remove-email-btn-' + rowId);
    removeBtn.removeClass('delete-step-2 btn-warning');
    removeBtn.addClass('delete-step-1 btn-default');
    removeBtn.html('<span class="glyphicon glyphicon-remove"></span>');
    $(this).remove();
  });

  $('body').on('click', '.delete-step-2', function(){
    var rowId = $(this).attr('related-email');
    $('#row' + rowId).remove();
  });


  ///////////////////
  // Functions dealing with adding a new email recipient
  ///////////////////
  function isEmail(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
  };

  $('body').on('click', '.add-email-btn', function(){
    var rowId = $(this).attr('related-email');
    var newEmailAddress = $('#' + rowId).val()
    if (isEmail(newEmailAddress)){
      $(this).removeClass('add-email-btn');
      $(this).addClass('delete-step-1');
      $(this).html('<span class="glyphicon glyphicon-remove"></span>');
      newEmailId += 1;
      var rowId = newEmailId.toString();
      $('<tr id="rowN' + rowId + '">' +
        '<td><button class="btn btn-default ' +
          'add-email-btn" type="button" related-email="N' + rowId +
          '" id="remove-email-btn-N' + rowId + '">' +
          '<span class="glyphicon glyphicon-plus"></span></button></td>' +
        '<td><input type="email" name="address_N"' + rowId +
          ' class="form-control" id="N' + rowId + '" /></td>' +
        '<td><input name="salutation_N' + rowId + '" class="form-control" ' +
          'id="salutation_N' + rowId + '" /></td>' +
        '<td>New Recipient</td></tr>').insertAfter(
          '#rowN' + (newEmailId - 1).toString()
        )
    }
  });

});
