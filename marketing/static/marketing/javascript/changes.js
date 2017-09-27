$(document).ready(function() {

  ////////////////////////
  // Load change records and highlight differences
  ////////////////////////

  const formGroupBefore = '<span class="input-group-addon revert-field"><span class=" glyphicon glyphicon-arrow-left"></span></span>'

  const highlightChanges = () => {
    $('#change-record-panel input').each(function(){
      var fieldName = $(this).attr('name');
      if ($(this).attr('type') == 'checkbox') {
        var thisIsChecked = $(this).prop('checked');
        var thatIsChecked = $('#current-record-panel input[name="' + fieldName + '"]').prop('checked');
        if (thisIsChecked !== thatIsChecked) {
          // $(this).addClass('yellow-box');
          $(this).wrap('<div class="input-group yellow-box"></div>');
          $(this).before(formGroupBefore);
        };
      } else if ($(this).val() !== $('#current-record-panel input[name="' + fieldName + '"]').val()) {
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
          console.log(changeHeight);
        };
      }
    })
  });

  ///////////////////////
  // Revert field to pre-change value
  ///////////////////////
  $('body').on('click', '.revert-field', function(){
    console.log('we are going back');
  })

});
