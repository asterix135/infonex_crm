$(document).ready(function() {
  let oldValue;

  // submit changes to record as they are completed
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
  $('body').on('focusin', 'input, textarea', function(){
    oldValue = $(this).val();
  });
  $('body').on('focusout', 'input, textarea', function(){
    if ($(this).attr('type') != 'checkbox') {
      var newValue = $(this).val();
      if (newValue != oldValue) {
        var field = $(this).attr('name');
        var recordId = $(this).attr('record_id');
        updateRecord(recordId, field, newValue);
        }
    };
  });
  $('body').on('change', 'input[type="checkbox"], select', function(){
    var field = $(this).attr('name');
    var recordId = $(this).attr('record_id');
    if ($(this).is('input')) {
      var newValue = $(this).prop('checked');
    } else {
      var newValue = $(this).val();
    };
    updateRecord(recordId, field, newValue);
  });

});
