$(document).ready(function(){

  // TODO: Format currency to 2 decimals & fx to 3 decimals

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
    var currentDelegateId = $('#current-registrant-id').val();
    if (currentDelegateId == '') {
      currentDelegateId = 'new';
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
    $('#crm-match-value').val(newCrmId);
  });


  // link different company record to delegate
  $('body').on('click', '.link-company-btn', function(){
    var newCompanyId = $(this).attr('company-id');
    var currentCompanyId = $('#company-match-value').val();
    var currentDelegateId = $('#current-registrant-id').val();
    if (currentDelegateId == '') {
      currentDelegateId = 'new';
    };
    $.ajax({
      url: '/delegate/link_new_company_record/',
      type: 'POST',
      data: {
        'company_match_id': newCompanyId,
        'delegate_id': currentDelegateId,
      },
      success: function(data){
        $('#selected-company-details').html(data);
      }
    });
    $('#company-match-value').val(newCompanyId);
  })


  // add new company and link to current delegate
  $('body').on('click', '#save-new-company', function(){
    var currentDelegateId = $('#current-registrant-id').val();
    if (currentDelegateId == '') {
      currentDelegateId = 'new';
    };
    var name = $('#new-company-entry #id_name').val();
    var nameForBadges = $('#new-company-entry #id_name_for_badges').val();
    var address1 = $('#new-company-entry #id_address1').val();
    var address2 = $('#new-company-entry #id_address2').val();
    var city = $('#new-company-entry #id_city').val();
    var postalCode = $('#new-company-entry #id_city').val();
    var country = $('#new-company-entry #id_country').val();
    var gstHstExempt = $('#new-company-entry #id_gst_hst_exempt').prop('checked');
    var qstExempt = $('#new-company-entry #id_qst_exempt').prop('checked');
    var gstHstExemptionNumber = $('#new-company-entry #id_gst_hst_exemption_number').val();
    var qstExemptionNumber = $('#new-company-entry #id_qst_examption_number').val();
    $.ajax({
      url: '/delegate/add_new_company/',
      type: 'POST',
      data: {
        'delegate_id': currentDelegateId,
        'name': name,
        'name_for_badges': nameForBadges,
        'address1': address1,
        'address2': address2,
        'city': city,
        'postal_code': postalCode,
        'country': country,
        'gst_hst_exempt': gstHstExempt,
        'qst_exempt': qstExempt,
        'gst_hst_exemption_number': gstHstExemptionNumber,
        'qst_exemption_number': qstExemptionNumber,
      },
      success: function(data){
        $('#company-sidebar-content').html(data);
        var newCompanyId = $('#inserted-company-id').val();
        $('#company-match-value').val(newCompanyId);
      }
    });
  });


  // updates display of current conference & saves variable when new conf chosen
  $('body').on('click', '#change-conference', function(){
    var newConfId = $('#id_event').val();
    if (newConfId != '') {
      var newConfName = $('#id_event option:selected').text();
      $('#displayed-conf-name').text(newConfName);
      $('#selected-conference-id').val(newConfId);
      $('#conference-details').removeClass('in');
      $.ajax({
        url: '/delegate/update_tax_information/',
        type: 'POST',
        data: {
          'conf_id': newConfId,
        },
        success: function(data){
          $('#registration-tax-information').html(data);
        }
      });
      $.ajax({
        url: '/delegate/update_fx_conversion/',
        type: 'POST',
        data: {
          'conf_id': newConfId,
        },
        success: function(data){
          $('#fx-details').html(data);
        }
      });
      $.ajax({
        url: '/delegate/update_conference_options/',
        type: 'POST',
        data: {
          'conf_id': newConfId,
        },
        success: function(data){
          $('#conference-options').html(data);
        }
      });
    };
  });


  // updates payment displays when registration status changes
  $('body').on('change', '#id_registration_status', function(){
    var newStatus = $(this).val();
    var currentRegDetailId = $('#current-regdetail-id').val()
    if (currentRegDetailId == '') {
      currentRegDetailId = 'new'
    };
    $.ajax({
      url: '/delegate/update_cxl_info/',
      type: 'POST',
      data: {
        'regdetail_id': currentRegDetailId,
        'reg_status': newStatus,
      },
      success: function(data){
        $('#cancellation-details').html(data);
      }
    });
    $.ajax({
      url: '/delegate/update_payment_details/',
      type: 'POST',
      data: {
        'regdetail_id': currentRegDetailId,
        'reg_status': newStatus,
      },
      success: function(data){
        $('#status-based-reg-fields').html(data);
      }
    });
  });


  // swap content in sidebar
  $('body').on('click', '.sidebar-button', function(){
    $('#crm-sidebar-content').toggle();
    $('#company-sidebar-content').toggle();
    var buttonText = $('#toggle-sidebar-button').text().trim();
    if (buttonText == 'Switch to Company') {
      $('#toggle-sidebar-button').text('Switch to CRM');
    } else {
      $('#toggle-sidebar-button').text('Switch to Company');
    };
  });


  // update company suggestions
  $('body').on('keyup', '#company-info #id-name', function(){
    var charsEntered = $('#company-info #id-name').val().length
    if (charsEntered > 1) {
      var CompanyNamePartial = $('#company-info #id-name').val();
    }
  })


  // toggles whether company name is editable
  $('body').on('click', '#toggle-company-edit', function(){
    $('#company-info #id_name').prop('disabled', function(i, v){
      return !v;
    });
  })


  // Toggle display of assistant panel if choose to send to assistant
  $('body').on('change', '#id_contact_option', function(){
    var contactOption = $('#id_contact_option').val();
    if (contactOption == 'C' || contactOption == 'A') {
      if (!$('#assistant-details').hasClass('collapse in')){
        $('#assistant-details').collapse('show');
      };
    };
  });


});
