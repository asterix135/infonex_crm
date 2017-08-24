$(document).ready(function() {
  let oldValue;
  var filterString = $('#filter-string').val();
  var filterRowVisible = filterString != '';

  ///////////////////
  // adjust layout
  ///////////////////
  $('body').on('click', '#expand-company-btn', function(){
    if ($(this).attr('direction') == 'expand') {
      $(this).removeClass('glyphicon-chevron-right');
      $(this).addClass('glyphicon-chevron-left');
      $(this).attr('direction', 'collapse');
      $('.company-cell').each(function(){
        $(this).removeClass('mktg-col-xl');
        $(this).addClass('mktg-col-xxl');
      });
    } else {
      $(this).removeClass('glyphicon-chevron-left');
      $(this).addClass('glyphicon-chevron-right');
      $(this).attr('direction', 'expand');
      $('.company-cell').each(function(){
        $(this).removeClass('mktg-col-xxl');
        $(this).addClass('mktg-col-xl');
      });
    };
  });

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
  function deleteRecord(recordId){
    $.ajax({
      url: '/marketing/delete/',
      type: 'POST',
      data: {'record_id': recordId,},
      success: function(){
        $('tr[record_id="' + recordId + '"]').remove();
      },
    });
  }
  $('body').on('click', '.delete-step-1', function(){
    var recordId = $(this).attr('record_id');
    $(this).removeClass('delete-step-1 btn-link');
    $(this).addClass('delete-step-2 btn-warning');
    $(this).text('Delete');
    $('.btn-duplicate[record_id="' + recordId + '"]').removeClass('in');
    $('<button class="btn btn-success btn-restore" type="button" record_id="' + recordId + '">Oops..</button>').insertAfter(this);
  });
  $('body').on('click', '.btn-restore', function(){
    var recordId = $(this).attr('record_id');
    var removeBtn = $('.delete-step-2[record_id="' + recordId + '"]');
    removeBtn.removeClass('delete-step-2 btn-warning');
    removeBtn.addClass('delete-step-1 btn-link');
    removeBtn.html('<span class="glyphicon glyphicon-remove-sign"></span>');
    $(this).remove();
    $('.btn-duplicate[record_id="' + recordId + '"]').addClass('in');
  });
  $('body').on('click', '.delete-step-2', function(){
    var recordId = $(this).attr('record_id');
    deleteRecord(recordId);
  });

  ////////////////////
  // Add record
  ////////////////////
  $('body').on('click', '#btn-add-record', function(){
    $.ajax({
      url: '/marketing/add/',
      type: 'POST',
      success: function(data){
        $('.marketing-table').prepend(data);
        $('input[name="company"]:first').focus();
      }
    });
  });
  $('body').on('click', '.btn-duplicate', function(){
    var personId = $(this).attr('record_id');
    $.ajax({
      url: '/marketing/add/',
      type: 'POST',
      data: {
        'person_id': personId,
      },
      success: function(data){
        $('.marketing-table').prepend(data);
        $('input[name="company"]:first').focus();
      }
    });
  });

  ////////////////////
  // filter records
  ////////////////////
  function clearFilters() {
    $('.filter-input').each(function(){
      if ($(this).attr('type') == 'checkbox') {
        $(this).attr('checked', false);
      } else {
        $(this).val('');
      };
    });
  };
  $('body').on('click', '#btn-filter', function(){
    if ($('#filter-row').hasClass('in')) {
      $('#filter-row').removeClass('in');
      filterRowVisible = false;
    } else {
      $('#filter-row').addClass('in');
      filterRowVisible = true;
      $('#btn-see-all').removeClass('disabled');
    }
  })
  $('body').on('click', '#btn-see-all', function(){
    if (filterString != '') {
      window.location.href = '/marketing/';
    } else {
      clearFilters();
      $('#filter-row').removeClass('in');
      filterRowVisible = false;
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
        newFilterString += $(this).attr('filter-field') + '=' + $(this).val().trim() + '&';
      };
    });
    newFilterString = newFilterString.slice(0,-1);
    if (newFilterString.length) {
      newFilterString = newFilterString.replace(/\s/g, '%20');
      if ($('#sort-by').val()) {
        newFilterString += '&sort_by=' + $('#sort-by').val();
        newFilterString += '&order=' + $('#order').val();
      }
      if ($('#page-number').val()) {
        newFilterString += '&page=' + $('#page-number').val();
      }
      window.location.href = newFilterString;
    };
  });
  $('body').on('click', '#btn-clear-filter', function(){
    clearFilters();
  });
  $('body').on('keypress', '.filter-input', function(e){
    if (e.which === 13) {
      $('#btn-apply-filter').click();
    };
  });
  $('body').on('keypress, click', '.same-page', function(e){
    if (filterString) {
      if (e.which === 13 || e.type === 'click') {
        var currentHref = $(this).attr('href');
        if (currentHref.indexOf('?') > -1) {
          currentHref += '&' + filterString;
        } else {
          currentHref += '?' + filterString;
        };
        $(this).attr('href', currentHref);
      };
    };
  });

  ////////////////////
  // bulk delete
  ////////////////////
  function resetActionCell(cell){
    var recordId = cell.attr('record_id');
    cell.html(
      '<button type="button" class="btn btn-link delete-step-1 float-left" record_id="' + recordId + '">' +
        '<span class="glyphicon glyphicon-remove-sign"></span>' +
      '</button>' +
      '<button type="button" class="btn btn-link btn-duplicate float-right collapse in" record_id="' + recordId + '">' +
        '<span class="glyphicon glyphicon-duplicate"></span>' +
      '</button>'
    );
  };
  function removeDeleteStuff() {
    $('.row-action-cell').each(function(){
      resetActionCell($(this));
    });
  };
  $('body').on('click', '#btn-bulk-delete', function(){
    if ($(this).hasClass('btn-info')) {
      $(this).removeClass('btn-info');
      $(this).addClass('btn-default');
      $('#first-cell').html('');
      removeDeleteStuff();
      $('#btn-bulk-update').removeClass('disabled');
    } else {
      $('#btn-bulk-update').addClass('disabled');
      var numRows = $('.marketing-table tr').length - 3;
      if (numRows > 250) {
        alert('You can only use this for less than 250 records');
      } else {
        $(this).removeClass('btn-default');
        $(this).addClass('btn-info');
        $('.row-action-cell').each(function(){
          var recordId = $(this).attr('record_id');
          $(this).html(
            '<input class="form-control delete-checkbox" record_id="' + recordId +'" type="checkbox" checked="true" />'
          );
        });
        $('#first-cell').html(
          '<button type="button" class="btn btn-danger btn-xs" id="process-bulk-delete" id="process-bulk-delete">' +
            'Delete Checked' +
          '</button>'
        );
      };
    }
  });
  $('body').on('click', '#process-bulk-delete', function(){
    $('.row-action-cell').each(function(){
      var recordId = $(this).attr('record_id');
      var isChecked = $(this).find('input[type="checkbox"]').prop('checked');
      if (isChecked) {
        deleteRecord(recordId);
      } else {
        resetActionCell($(this));
      }
    });
    $('#btn-bulk-delete').removeClass('btn-info');
    $('#btn-bulk-delete').addClass('btn-default');
    $('#first-cell').html('');
  });


  ////////////////////
  // bulk update
  ////////////////////
  function clearBulkUpdateRow(){
    $('.update-input').each(function(){
      if ($(this).attr('type') == 'checkbox') {
        $(this).attr('checked', false);
      } else {
        $(this).val('');
      };
    });
  };
  $('body').on('click', '#btn-bulk-update', function(){
    if ($(this).hasClass('btn-info')) {
      $(this).removeClass('btn-info');
      $(this).addClass('btn-default');
      $('#bulk-update-row').removeClass('in');
      clearBulkUpdateRow();
      removeDeleteStuff();
      $('#btn-bulk-delete').removeClass('disabled');
      if (filterRowVisible) {
        $('#filter-row').addClass('in');
      };
    } else {
      $('#btn-bulk-delete').addClass('disabled');
      var numRows = $('.marketing-table tr').length - 3;
      alert('You will be updating ' + numRows + ' records.');
      $('#filter-row').removeClass('in');
      $('#bulk-update-row').addClass('in');
      $(this).removeClass('btn-default');
      $(this).addClass('btn-info');
      $('.row-action-cell').each(function(){
        var recordId = $(this).attr('record_id');
        $(this).html(
          '<input class="form-control update-checkbox" record_id="' + recordId +'" type="checkbox" checked="true" />'
        );
      });
    }
  });
  $('body').on('click', '#btn-do-bulk-update', function(){
    var updateData = {};
    var recordsToUpdate = [];
    $('.update-input').each(function(){
      if ($(this).val().trim() != '') {
        var fieldname = $(this).attr('update-field');
        if ($(this).attr('response-type') == 'bool') {
          updateData[fieldname] = $(this).val().trim() == 'true';
        } else {
          updateData[fieldname] = $(this).val().trim();
        };
      };
    });
    $('.update-checkbox').each(function(){
      if ($(this).is(':checked')) {
        recordsToUpdate.push($(this).attr('record_id'))
      };
    });
    var passedJson = {
      'record_list': recordsToUpdate,
      'field_dict': updateData,
    };
    if (recordsToUpdate.length > 0 && Object.keys(updateData).length > 0) {
      $.ajax({
        url: '/marketing/bulk_update/',
        type: 'POST',
        data: {
          'json': JSON.stringify(passedJson),
        },
        dataType: 'json',
        success: function(data){
          console.log('need to process response');
        }
      })
    };
  });

});
