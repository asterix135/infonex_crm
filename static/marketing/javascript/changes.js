$(document).ready(function() {

  ////////////////////////
  // Load change records and highlight differences
  ////////////////////////

  const formGroupBefore = '<span class="input-group-addon revert-field"><span class="glyphicon glyphicon-arrow-left"></span></span>'

  const highlightChanges = () => {
    $('#change-record-panel input').each(function(){
      var fieldName = $(this).attr('name');
      if ($(this).attr('type') == 'checkbox') {
        var thisIsChecked = $(this).prop('checked');
        var thatIsChecked = $('#current-record-panel input[name="' + fieldName + '"]').prop('checked');
        if (thisIsChecked !== thatIsChecked) {
          $(this).wrap('<div class="input-group yellow-box"></div>');
          $(this).before(formGroupBefore);
        };
      } else if ($(this).val() !== $('#current-record-panel').find('[name="' + fieldName + '"]').val()) {
        $(this).addClass('yellow-box');
        $(this).wrap('<div class="input-group"></div>');
        $(this).before(formGroupBefore);
      }
    });
    $('#change-record-panel select').each(function(){
      var fieldName = $(this).attr('name');
      if ($(this).val() !== $('#current-record-panel select[name="' + fieldName + '"]').val()) {
        $(this).addClass('yellow-box');
        $(this).wrap('<div class="input-group"></div>');
        $(this).before(formGroupBefore);
      }
    });
    $('#change-record-panel textarea').each(function(){
      var fieldName = $(this).attr('name');
      if ($(this).val() !== $('#current-record-panel textarea[name="' + fieldName +'"]').val()) {
        $(this).addClass('yellow-box');
        $(this).wrap('<div class="input-group"></div>');
        $(this).before(formGroupBefore);
      }
    })
  };

  $('body').on('click', '.change-row', function(){
    let changeId = $(this).attr('change-record-id');
    $.ajax({
      url: '/marketing/change_details/' + changeId + '/',
      type: 'GET',
      // data: {},
      success: function(data) {
        $('#comparison-panel').html(data);
        if ($('#current-record-panel #id_name').length) {
          highlightChanges();
        } else {
          const changeHeight = $('#change-record-panel').height();
          $('#current-record-panel').css({height: changeHeight});
        };
      }
    })
  });

  ///////////////////////
  // Revert field to pre-change value
  ///////////////////////
  $('body').on('click', '.revert-field', function(){
    const fieldName = $(this).next().attr('name');
    if ($(this).next().attr('type') === 'checkbox') {
      const changeFieldVal = $(this).next().prop('checked');
      $('#current-record-panel').find('[name="' + fieldName + '"]').prop('checked', changeFieldVal);
    } else {
      const changeFieldVal = $(this).next().val();
      $('#current-record-panel').find('[name="' + fieldName + '"]').val(changeFieldVal);
    }
  });

  //////////////////////
  // Delete change record and update DOM
  //////////////////////
  $('body').on('click', '#delete-change-record', function(){
    const changeId = $(this).attr('record-id');
    $.ajax({
      url: '/marketing/delete_change/' + changeId + '/',
      type: 'POST',
      success: function(){
        location.reload();
      }
    })
  })

  //////////////////////
  // Restore deleted record
  //////////////////////
  $('body').on('click', '#restore-deleted-record', function(){
    const changeId = $(this).attr('record-id');
    $.ajax({
      url: '/marketing/restore_deleted_record/' + changeId + '/',
      type: 'POST',
      success: function(data){
        $('#comparison-panel').html('<h3 class="comparison-placeholder">Record Restored</h3>');
        $('.change-row[change-record-id="' + data.change_id + '"]').remove();
      }
    });
  });

  $('body').on('submit', '#update-record-form', function(e){
    e.preventDefault();
    const changeId = $(this).attr('record-id');
    $.ajax({
      url: '/marketing/change_details/' + changeId + '/',
      type: 'POST',
      data: $("#update-record-form").serialize(),
      success: function(data, status, xhr) {
        const ct = xhr.getResponseHeader('content-type') || '';
        if (ct.indexOf('html') > -1) {
          $('#comparison-panel').html(data);
          highlightChanges();
        } else {
          $('.change-row[change-record-id="' + changeId + '"]').remove();
          $('#comparison-panel').html(
            '<h3 class="comparison-placeholder">Update Successful</h3>'
          );
        }
      }
    })

  })

});
