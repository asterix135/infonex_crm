$(document).ready(function(){

  // update list of crm suggestion names on keyup
  $('body').on('keyup', '#delegate-info #id_first_name,#delegate-info #id_last_name', function(){
    var charsEntered = $('#delegate-info #id_first_name').val().length +
      $('#delegate-info #id_last_name').val().length +
      $('#company-info #id_name').val().length;
    if (charsEntered > 5) {
      var firstName = $('#delegate-info #id_first_name').val();
      var lastName = $('#delegate-info #id_last_name').val();
      var companyName = $('#company-info #id_name').val();
      $.ajax({
        url: '/delegate/update_crm_match_list/',
        type: 'POST',
        data: {
          'first_name': firstName,
          'last_name': lastName,
          'company': companyName,
        },
        success: function(data){
          $('#crm-sidebar-details').html(data);
        }
      })
    }
  });


  // link different crm record to delegate
  $('body').on('click', '.link-record-btn', function(){
    var newCrmId = $(this).attr('crm-id');
    var currentCrmId = $('#crm-match-value').val();
    var currentDelegateId = $('#current-registrant-id').val()
    if (currentDelegateId == '') {
      currentDelegateId = 'new'
    };
    $.ajax({
      url: '/delegate/link_new_crm_record/',
      type: 'POST',
      data: {
        'crm_match_id': newCrmId,
        'delegate_id': currentDelegateId,
      },
      success: function(data){
        $('#selected-crm-person-details').html(data);
      }
    });
  });


  // updates display of current conference & saves variable
  $('body').on('click', '#change-conference', function(){
    var newConfId = $('#id_event').val();
    var newConfName = $('#id_event option:selected').text();
    $('#displayed-conf-name').text(newConfName);
    $('#selected-conference-id').val(newConfId);
    $('#conference-details').hide();
  })

});
