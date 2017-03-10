$(document).ready(function(){

  // TODO: Format currency to 2 decimals & fx to 3 decimals

  // Check & adjust display of reg details on page load/reload
  displayHideRegDetails();
  // Update display of tax and invoice
  updateTaxAndInvoice();

  // Activate datepicker
  $('#id_register_date').datepicker({
    dateFormat: 'yy-mm-dd'
  });
  $('#id_cancellation_date').datepicker({
    dateFormat: 'yy-mm-dd'
  });
  $('#id_payment_date').datepicker({
    dateFormat: 'yy-mm-dd'
  });


  // Respond to button click to go to edit conference page
  $('body').on('click', '#edit-event', function(){
    var newConfId = $('#id_event').val();
    $(location).attr('href', '/registration/conference/?action=edit&id=' + newConfId);
  });


  // function to reload page when changing to a conference where delegate is already registered
  function loadRegisteredDelegate(confId, registrantId){
    var csrfToken = null;
    var i = 0;
    if (document.cookie && document.cookie !== ''){
      var cookies = document.cookie.split(';');
      for (i; i < cookies.length; i++){
        var cookie = jQuery.trim(cookies[i]);
        if (cookie.substring(0,10) === 'csrftoken='){
          csrfToken = decodeURIComponent(cookie.substring(10));
          break;
        };
      };
    };
    var formHtml = '<form action="/delegate/" method="post">' +
                   '<input name="csrfmiddlewaretoken" value="' + csrfToken +'" type="hidden"/>' +
                   '<input name="conf_id" value="' + confId + '" type="hidden"/>' +
                   '<input name="registrant_id" value="' + registrantId + '" type="hidden"/>' +
                   '<input name="crm_id" value="" type="hidden"/>' +
                   '</form>';
    $(formHtml).appendTo('body').submit();
  };


  // function to change active conference for delegate
  function changeActiveConference(newConfId){
    var newConfName = $('#id_event option:selected').text();
    var companyId = $('#company-match-value').val();
    $('#displayed-conf-name').text(newConfName);
    $('#selected-conference-id').val(newConfId);
    $('#conference-details').removeClass('in');
    $.ajax({
      url: '/delegate/update_tax_information/',
      type: 'POST',
      data: {
        'conf_id': newConfId,
        'company_id': companyId,
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


  // updates display of current conference & saves variable when new conf chosen
  $('body').on('click', '#change-conference', function(){
    var newConfId = $('#id_event').val();
    var currentDelegateId = $('#current-registrant-id').val();
    if (newConfId != '') {
      $.ajax({
        url: '/delegate/person_is_registered/',
        type: 'POST',
        data: {
          'conf_id': newConfId,
          'registrant_id': currentDelegateId,
        },
        success: function(data){
          var isRegistered = $('#person-is-registered', data).val() == 'True';
          if (isRegistered) {
            loadRegisteredDelegate(newConfId, currentDelegateId)
          } else {
            $.ajax({
              url: '/delegate/conf_has_regs/',
              type: 'POST',
              data: {
                'conf_id': newConfId,
              },
              success: function(data){
                var okToRegister = $('#first-reg', data).val() == 'true';
                if (okToRegister) {
                  changeActiveConference(newConfId);
                } else {
                  $('#first-registration-modal').html(data);
                  $('#confSetupModal').modal('show');
                };
              }
            });
          };
        }
      });
    };
  });


  // Update short company name when main name is changed (and short is blank)
  $('body').on('change', '#id_company_name', function(){
    var companyName = $(this).val();
    var shortName = $('#id_name_for_badges').val();
    if (shortName == ''){
      $('#id_name_for_badges').val(companyName.slice(0,30))
    }
  });


  // Proceed with registration when appropriate button clicked in modal
  $('body').on('click', '#proceed-with-registration', function(){
    var newConfId = $('#id_event').val();
    $('#confSetupModal').modal('hide');
    changeActiveConference(newConfId);
  });


  // function to ensure proper display/hide of reg details
  function displayHideRegDetails(){
    var nonInvoiceVals = ['G', 'K', 'KX', 'SD', 'SE', ''];
    var cxlVals = ['DX', 'SX', 'KX'];
    var regStatus = $('#id_registration_status').val();
    var detailsDisplayed = $('#invoice-details').hasClass('in');
    var cxlDisplayed = $('#cancellation-panel').hasClass('in');
    if (jQuery.inArray(regStatus, nonInvoiceVals) >= 0) {
      if (detailsDisplayed) {
        $('#invoice-details').removeClass('in');
      };
    } else {
      if (!detailsDisplayed) {
        $('#invoice-details').addClass('in');
      };
    };
    if (jQuery.inArray(regStatus, cxlVals) >= 0){
      if (!cxlDisplayed) {
        $('#cancellation-panel').addClass('in');
      };
    } else {
      if (cxlDisplayed) {
        $('$cancellation-panel').removeClass('in');
      };
    };
  };


  // updates payment displays when registration status changes
  $('body').on('change', '#id_registration_status', function(){
    displayHideRegDetails();
    var newStatus = $(this).val();
    var currentRegDetailId = $('#current-regdetail-id').val();
    if (currentRegDetailId == '') {
      currentRegDetailId = 'new';
    };
    var detailsDisplayed = $('#invoice-details').hasClass('in');

    if (detailsDisplayed) {
      $('#invoice-details').addClass('in');
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
        $('#id_payment_date').datepicker({
          dateFormat: 'yy-mm-dd'
        });
        $('#id_payment_date')
      }
    });
  });


  // function to update tax and invoice total on screen
  function updateTaxAndInvoice() {
    var preTaxPrice = $('#id_pre_tax_price').val();
    if ($('#id_gst_rate').val() != undefined){
      var gstRate = $('#id_gst_rate').val();
    } else {
      var gstRate = 0;
    };
    if ($('#id_hst_rate').val() != undefined){
      var hstRate = $('#id_hst_rate').val();
    } else {
      var hstRate = 0;
    };
    if ($('#id_qst_rate').val() != undefined) {
      var qstRate = $('#id_qst_rate').val();
    } else {
      var qstRate = 0;
    };
    var totalTax = (preTaxPrice * gstRate) + (preTaxPrice * hstRate) + (preTaxPrice * (1 + gstRate)) * qstRate
    var taxAsCurrency = '$' + totalTax.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    var totalInvoice = +(preTaxPrice) + totalTax;
    var totalAsCurrency = '$' + totalInvoice.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    $('#total-tax').text(taxAsCurrency);
    $('#total-invoice').text(totalAsCurrency);
  };


  // Update tax and invoice total on changes to relevant fields
  $('body').on('keyup change', '.cost-field', function(){
    updateTaxAndInvoice();
  });


  // toggles whether company name is editable & change icon
  $('body').on('click', '#toggle-company-edit', function(){
    if ($(this).hasClass('glyphicon-chevron-down')){
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#company-details').toggle();
      $('#id_company_name').removeAttr('readonly');
    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $('#company-details').toggle();
      $('#id_company_name').prop('readonly', true);
    };
  });


  // Toggle display of assistant panel if choose to send to assistant
  $('body').on('change', '#id_contact_option', function(){
    var contactOption = $('#id_contact_option').val();
    if (contactOption == 'C' || contactOption == 'A') {
      if (!$('#assistant-details').hasClass('collapse in')){
        $('#assistant-details').collapse('show');
        $('#toggle-assistant-details').removeClass('glyphicon-chevron-down');
        $('#toggle-assistant-details').addClass('glyphicon-chevron-up');
      };
    };
  });


  // Toggle display of assistant panel manually
  $('body').on('click', '#toggle-assistant-details', function(){
    if ($('#assistant-details').hasClass('collapse in')) {
      $(this).removeClass('glyphicon-chevron-up');
      if (!$(this).hasClass('glyphicon-chevron-down')) {
        $(this).addClass('glyphicon-chevron-down')
      }
    } else {
      $(this).removeClass('glyphicon-chevron-down');
      if (!$(this).hasClass('glyphicon-chevron-up')){
        $(this).addClass('glyphicon-chevron-up');
      }
    }
    $('#assistant-details').collapse('toggle');
  });


  // Called when attempting to process registration
  $('body').on('click', '#process-registration-button', function(){
    var crmMatchId = $('#crm-match-value').val();
    var companyMatchId = $('#company-match-value').val();
    var companyName = $('#id_company_name').val();
    var address1 = $('#id_address1').val();
    var address2 = $('#id_address2').val();
    var city = $('#id_city').val();
    var stateProv = $('#id_state_prov').val();
    var postalCode = $('#id_postal_code').val();
    var firstName = $('#id_first_name').val();
    var lastName = $('#id_last_name').val();
    var title = $('#id_title').val();
    var email = $('#id_email1').val();
    if (crmMatchId=='' || companyMatchId == '') {
      $.ajax({
        url: '/delegate/company_crm_modal/',
        type: 'POST',
        data: {
          'company_id': companyMatchId,
          'crm_id': crmMatchId,
          'company_name': companyName,
          'address1': address1,
          'address2': address2,
          'city': city,
          'state_prov': stateProv,
          'postal_code': postalCode,
          'first_name': firstName,
          'last_name': lastName,
          'title': title,
          'email': email,
        },
        success: function(data){
          $('#company-crm-modal').html(data);
          $('#companyCrmModal').modal('show');
        }
      });
    } else {
      $('#registration-form').submit();
    }
  });


  // Submit registration for processing from modal
  $('body').on('click', '#register-from-crm-modal', function(){
    var crmId = $('#crm-match-value').val();
    if (crmId == '') {
      crmId = $('input[name=crm-select]:checked').val();
      $('#crm-match-value').val(crmId);
    };
    var companyId = $('#company-match-value').val();
    if (companyId == '') {
      companyId = $('input[name=company-select]:checked').val();
      $('#company-match-value').val(companyId);
    };
    $('#registration-form').submit();
  })


  // Trigger modal to look for matching company
  $('body').on('click', '#search-for-company', function(){
    $('#companyMatchModal').modal('show');
  })

});
