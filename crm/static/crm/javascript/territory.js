// Javascript for territory.html page
$(document).ready(function() {
  var eventAssignmentId = $('#my-event-assignment').val()

  // Process individual flag change
  $('body').on('click', '.flag-icon', function(){
    var personId = $(this).attr('flag-for');
    var flagColor = $(this).attr('flag-color');
    $.ajax({
      url: '/crm/change_flag/',
      type: 'POST',
      data: {
        'person_id': personId,
        'flag_color': flagColor,
        'event_assignment_id': eventAssignmentId,
      },
      success: function(data){
        $('#flag-button-' + personId).html(data);
      }
    });
  });

  // select or de-select all flags on page
  $('body').on('click', '#select-all-flags', function(){
    var checkedStatus = $('#select-all-flags').prop('checked');
    console.log(checkedStatus);
    $('.personal-flag-select').each(function(){
      $(this).prop('checked', checkedStatus);
    });
  });


  // process batch flag changes
  $('body').on('click', '.master-flag-icon', function(){
    var flagColor = $(this).attr('flag-color');
    var checkedPeople = []
    $('.personal-flag-select').each(function(){
      if ($(this).is(':checked')){
        checkedPeople.push($(this).attr('select-person'));
      };
    });
    console.log(checkedPeople);
  });


});
