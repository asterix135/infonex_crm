$(document).ready(function() {
  let oldValue;
  var filterString = $('#filter-string').val();

  ///////////////////
  // submit changes to record as they are completed
  ///////////////////
  function updateRecord(recordId, field, newValue){
    $.ajax({
      url: '/marketing/update/',
      type: 'POST',
      data: {
        'record_id': recordId,
        'field': field,
        'new_value': newValue,
      },
      success: function(data){
        $('span[name="state_prov"][record_id="' + recordId + '"]').text(data.state_prov);
        $('span[name="date_modified"][record_id="' + recordId + '"]').text(data.date_modified);
      },
    });
  };
  $('body').on('focusin', '.record-field', function(){
    oldValue = $(this).val();
  });
  $('body').on('focusout', '.record-field', function(){
    if ($(this).attr('type') != 'checkbox') {
      var newValue = $(this).val();
      if (newValue != oldValue) {
        var field = $(this).attr('name');
        var recordId = $(this).attr('record_id');
        updateRecord(recordId, field, newValue);
        }
    };
  });
  $('body').on('change', '.record-checkbox, .record-select', function(){
    var field = $(this).attr('name');
    var recordId = $(this).attr('record_id');
    if ($(this).is('input')) {
      var newValue = $(this).prop('checked');
    } else {
      var newValue = $(this).val();
    };
    updateRecord(recordId, field, newValue);
  });

  ///////////////////////
  // delete record
  ///////////////////////
  $('body').on('click', '.delete-step-1', function(){
    var recordId = $(this).attr('record_id');
    $(this).removeClass('delete-step-1 btn-link');
    $(this).addClass('delete-step-2 btn-warning');
    $(this).text('Delete');
    $('<button class="btn btn-success btn-restore" type="button" record_id="' + recordId + '">Oops..</button>').insertAfter(this);
  });
  $('body').on('click', '.btn-restore', function(){
    var recordId = $(this).attr('record_id');
    var removeBtn = $('.delete-step-2[record_id="' + recordId + '"]');
    removeBtn.removeClass('delete-step-2 btn-warning');
    removeBtn.addClass('delete-step-1 btn-link');
    removeBtn.html('<span class="glyphicon glyphicon-remove-sign"></span>');
    $(this).remove();
  });
  $('body').on('click', '.delete-step-2', function(){
    var recordId = $(this).attr('record_id');
    $.ajax({
      url: '/marketing/delete/',
      type: 'POST',
      data: {'record_id': recordId,},
      success: function(){
        $('tr[record_id="' + recordId + '"]').remove();
      },
    });
  });

  ////////////////////
  // Add record
  ////////////////////
  $('body').on('click', '#btn-add-record', function(){
    $.ajax({
      url: '/marketing/add/',
      type: 'POST',
      success: function(data){
        console.log('success');
        $('.marketing-table').prepend(data);
        $('input[name="company"]:first').focus();
      }
    });
  });

  ////////////////////
  // filter records
  ////////////////////
  $('body').on('click', '#btn-filter', function(){
    $('#filter-row').addClass('in');
    $(this).addClass('disabled');
    $('#btn-see-all').removeClass('disabled');
  })
  $('body').on('click', '#btn-see-all', function(){
    if (filterString != '') {
      window.location.href = '/marketing/';
    } else {
      $('#filter-row').removeClass('in');
      $(this).addClass('disabled');
      $('#btn-filter').removeClass('disabled');
    }
  });
  $('body').on('click', '#btn-apply-filter', function(){
    var newFilterString = '?';
    $('.filter-input').each(function(){
      if ($(this).attr('type') == 'checkbox') {
        if ($(this).is(':checked')){
          newFilterString += $(this).attr('filter-field') + '=' + 'true' + '&';
        };
      } else if ($(this).val() != '' ) {
        newFilterString += $(this).attr('filter-field') + '=' + $(this).val() + '&';
      };
    });
    newFilterString = newFilterString.slice(0,-1);

    // TODO: break if newFilterString == ''

    newFilterString = newFilterString.replace(/\s/g, '%20');
    if ($('#sort-by').val()) {
      newFilterString += '&sort_by=' + $('#sort-by').val();
      newFilterString += '&order=' + $('#order').val();
    }
    if ($('#page-number').val()) {
      newFilterString += '&page=' + $('#page-number').val();
    }

    console.log(newFilterString);
  });


});
