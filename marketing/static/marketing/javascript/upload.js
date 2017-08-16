$(document).ready(function() {
  //////////////////////
  // Globals
  //////////////////////
  let activeUpload;

  //////////////////////
  // make uploaded file active
  //////////////////////
  $('body').on('click', '.upload-file-row', function(){
    $('#incomplete-upload-data').removeClass('in');
    $('.upload-file-row').each(function(){
      $(this).removeClass('info');
    });
    $(this).addClass('info');
    activeUpload = $(this).attr('file_id');
    var target_url = '/marketing/field_matcher/' + activeUpload + '/';
    $.ajax({
      url: target_url,
      type: 'GET',
      success: function(data){
        $('#field-matcher').html(data);
      }
    });
  });

  //////////////////////
  // toggle display of next 10 records
  //////////////////////
  $('body').on('click', '#btn-toggle-records', function(){
    if ($(this).hasClass('glyphicon-chevron-down')){
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#ten-record-detail').addClass('in');
      $('#ten-record-detail').removeClass('out');
    } else {
      $(this).addClass('glyphicon-chevron-down');
      $(this).removeClass('glyphicon-chevron-up');
      $('#ten-record-detail').removeClass('in');
      $('#ten-record-detail').addClass('out');
    };
  });


  //////////////////////
  // Process request to delete file
  //////////////////////
  $('body').on('click', '#delete-step-1', function(){
    $('#row-action-buttons').html(
      `<button class="btn btn-danger col-sm-6 pull-left" id="delete-step-2">Yes - Delete</button>
      <button class="btn btn-success col-sm-6 pull-right" id="btn-no-delete">Oops - don't delete</button>`
    );
  });
  $('body').on('click', '#btn-no-delete', function(){
    $('#row-action-buttons').html(
      `<button class="btn btn-success col-sm-6 pull-left" id="btn-start-input">Input File to Database</button>
      <button class="btn btn-warning col-sm-6 pull-right" id="delete-step-1">Delete This File</button>`
    );
  });
  $('body').on('click', '#delete-step-2', function(){
    target_url = '/marketing/delete_upload/' + activeUpload + '/';
    $.ajax({
      url: target_url,
      type: 'POST',
      success: function(){
        $('tr[file_id=' + activeUpload + ']').remove();
        activeUpload = null;
        $('#field-matcher').html('');
      }
    });
  });

  ///////////////////////
  // Process uploaded file
  ///////////////////////
  function noDupeFields(){
    var fieldMatches = {};
    var selectedFields = [];
    var allGood = true;
    $('.header-match-row').each(function(){
      var currentField = $('select[name="field_option"]', this).val();
      var cellOrderNumber = $(this).attr('cell-order-num');;
      if (currentField != '') {
        if ($.inArray(currentField, selectedFields) > -1) {
          allGood = false;
          fieldMatches[currentField].push(cellOrderNumber);
        } else {
          selectedFields.push(currentField);
          fieldMatches[currentField] = [cellOrderNumber,];
        };
      };
    });
    return [allGood, fieldMatches];
  };
  function flagDupeFields(fieldMatches) {
    for (key in fieldMatches) {
      if (fieldMatches[key].length > 1) {
        fieldMatches[key].forEach(function(item){
          $('#field-error-' + item).text(
            'ERROR: You cannot use the same field for two different columns.'
          );
        });
      };
    };
  };
  function minimalFieldsChosen(fieldMatches) {
    if (!('name' in fieldMatches)) {
      return false;
    };
    if (!('company' in fieldMatches)) {
      return false;
    }
    if ('email' in fieldMatches) {
      return true;
    }
    if ('phone' in fieldMatches) {
      return true;
    }
    return false;
  };
  function startImport(fieldMatches){
    var ignoreFirstRow = $('#id_import_first_row').prop('checked');
    console.log(ignoreFirstRow);
    var passedJson = {
      'file_id': activeUpload,
      'field_matches': fieldMatches,
    }
    $.ajax({
      url: '/marketing/process_upload/',
      type: 'POST',
      data: {
        'json': JSON.stringify(passedJson),
        'ignore_first_row': ignoreFirstRow,
      },
      dataType: 'json',
      success: function(data){
        var processComplete = data.processComplete;
        if (processComplete) {
          $('tr[file_id="' + activeUpload + '"]').remove();
          $('#field-matcher').addClass('collapse');
        } else {
          $('#incomplete-upload-data').addClass('in');
          $('html, body').animate({
            scrollTop: $("#incomplete-upload-data").offset().top
          }, 500);
          $('#rowsSuccess').text(data.rowsImported.success);
          $('#rowsTotal').text(data.rowsImported.total);
        }
        alert('Import Complete');
      }
    });
  };
  $('body').on('click', '#btn-start-input', function(){
    $('.field-error').each(function(){
      $(this).text('');
    });
    $('#import-warnings').removeClass('in');
    $('#incomplete-upload-data').removeClass('in');
    var [noDupes, fieldMatches] = noDupeFields();
    if (noDupes){
      if (minimalFieldsChosen(fieldMatches)){
        alert('This may take a while.  Do not refresh or leave this page.');
        startImport(fieldMatches);
      } else {
        $('#import-warnings').addClass('in');
      }
    } else {
      flagDupeFields(fieldMatches);
    };
  });

  //////////////////////////
  // Download errors
  //////////////////////////
  $('body').on('click', '.download-errors', function(){
    var url = '/marketing/download_errors?fileformat=';
    url += $(this).attr('download-format');
    url += '&file_id=' + activeUpload;
    window.open(url);
    $('#incomplete-upload-data').removeClass('in');
    $('tr[file_id=' + activeUpload + ']').remove();
    activeUpload = null;
    $('#field-matcher').html('');    
  })

});
