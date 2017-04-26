$(document).ready(function(){

  // TODO: Format currency to 2 decimals & fx to 3 decimals

  // Global variables
  var defaultGstRate = $('#id_gst_rate').val();
  var defaultHstRate = $('#id_hst_rate').val();
  var defaultQstRate = $('#id_qst_rate').val();
  var companyDatabaseValues = {};
  var matchedCompanyId = null;

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
    var crmName = $('#id_crm_company').val();
    if (shortName == ''){
      $('#id_name_for_badges').val(companyName.slice(0,30))
    }
    if (crmName == '') {
      $('#id_crm_company').val(companyName);
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
        $('#cancellation-panel').removeClass('in');
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
        if (newStatus == 'DF'){
          $('#id_pre_tax_price').val(0);
          updateTaxAndInvoice();
        }
      }
    });
  });


  // function to update tax and invoice total on screen
  function updateTaxAndInvoice() {
    var preTaxPrice = $('#id_pre_tax_price').val();
    if ($.inArray($('#id_gst_rate').val(), [undefined, '']) == -1){
      var gstRate = parseFloat($('#id_gst_rate').val());
    } else {
      var gstRate = 0;
    };
    if ($.inArray($('#id_hst_rate').val(), [undefined, '']) == -1){
      var hstRate = parseFloat($('#id_hst_rate').val());
    } else {
      var hstRate = 0;
    };
    if ($.inArray($('#id_qst_rate').val(), [undefined, '']) == -1) {
      var qstRate = parseFloat($('#id_qst_rate').val());
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


  // Update tax rates when exemption box changes
  $('body').on('change', '#id_gst_hst_exempt', function(){
    var isGstExempt = $(this).prop('checked');
    if (isGstExempt){
      $('#id_gst_rate').val(0);
      $('#id_hst_rate').val(0);
    } else {
      $('#id_gst_rate').val(defaultGstRate);
      $('#id_hst_rate').val(defaultHstRate);
    }
    updateTaxAndInvoice();
  });
  $('body').on('change', '#id_qst_exempt', function(){
    var isQstExempt = $(this).prop('checked');
    if (isQstExempt){
      $('#id_qst_rate').val(0);
    } else {
      $('#id_qst_rate').val(defaultQstRate);
    }
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
    var regStatus = $('#id_registration_status').val();
    if (regStatus.slice(-1) != 'X'){
      $('#id_cancellation_date').val('');
    };
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
          var bestGuessCrmId = $('input[name="crm-select"]:checked', data).val();
          if (bestGuessCrmId == 'new') {
            var bestGuessCrmName = companyName;
          } else {
            var bestGuessCrmName = $('#crm_saved_company_name_' + bestGuessCrmId, data).val();
          };
          $('#crm-new-name-label').html('<input id="crm_company_change_to_new" value="change" type="radio" name="crm-name-action" />' + companyName);
          $('#crm-stet-name-label').html('<input id="crm_company_do_not_change" value="stet" type="radio" name="crm-name-action" checked />' + bestGuessCrmName);
          $('#id_crm_company').val(bestGuessCrmName);
          $('#companyCrmModal').modal('show');
        }
      });
    } else {
      $('#registration-form').submit();
    }
  });


  // Update Crm_stet value in modal when a different crm record is selected
  $('body').on('change', 'input[name="crm-select"]', function(){
    var selectedCrmRecordId = $(this).val();
    if (selectedCrmRecordId == 'new'){
      var stetCrmName = $('#id_company_name').val();
    } else {
      var stetCrmName = $('#crm_saved_company_name_' + selectedCrmRecordId).val();
    };
    $('#crm-stet-name-label').html('<input id="crm_company_do_not_change" value="stet" type="radio" name="crm-name-action" checked />' + stetCrmName);
    $('#id_crm_company').val(stetCrmName);
  });


  // function to create field comparison to be inserted into company_field_compare_modal
  function buildComparison(dataPointName, formValue, databaseValue){
    var sectionTitle = dataPointName.replace(/_/g, ' ');
    sectionTitle = sectionTitle.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    return `
    <div class="col-sm-12">
      <div class="row">
        <label>${sectionTitle}</label>
      </div>
      <div class="row errorlist" id="error-message-${dataPointName}">
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="${dataPointName}" value="form" />
          ${formValue}
        </label>
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="${dataPointName}" value="database" />
          ${databaseValue}
        </label>
      </div>
      <hr>
    </div>
    `;
  };

  // Submit registration for processing from company-crm modal
  $('body').on('click', '#register-from-crm-modal', function(){
    var okToSubmit = true;
    var crmId = $('#crm-match-value').val();
    if (crmId == '') {
      crmId = $('input[name=crm-select]:checked').val();
      $('#crm-match-value').val(crmId);
    };
    var companyId = $('#company-match-value').val();
    if (companyId == '') {
      okToSubmit = false;
      // Make sure that values match up - if not send to another modal to choose
      companyId = $('input[name=company-select]:checked').val();
      matchedCompanyId = companyId;
      $.ajax({
        url: '/delegate/get_company_details/',
        type: 'GET',
        data: {
          'company': companyId,
        },
        success: function(data){
          companyDatabaseValues = data;
          comparisonHtml = '';
          $.each(data, function(key,value){
            var dataPointName = key;
            if (dataPointName == 'name'){
              dataPointName = 'company_name';
            }
            if ($('#id_'+dataPointName).is(':checkbox')){
              var formValue = $('#id_'+dataPointName).prop('checked');
            } else {
              var formValue = $('#id_'+dataPointName).val();
            }
            var databaseValue = value;
            // trim whitespace from string values
            if (typeof formValue === 'string'){
              formValue = formValue.trim();
            }
            if (typeof databaseValue === 'string'){
              databaseValue = databaseValue.trim();
            }
            if (formValue != databaseValue && dataPointName != 'id'){
              comparisonHtml += buildComparison(
                dataPointName, formValue, databaseValue
              );
            }
          });
          if (comparisonHtml.length > 0){
            $('#company-field-selectors').html(comparisonHtml);
            $('#companyCrmModal').modal('hide');
            $('#companyFieldCompareModal').modal('show');
          } else {
            $('#company-match-value').val(companyId);
            $('#registration-form').submit();
          }
        },
      });
    };
    if (okToSubmit){
      $('#registration-form').submit();
    };
  });


  // Called from company_field_compare_modal - update form & submit
  $('body').on('click', '#register-from-field-compare-modal', function(){
    var allInputs = $('#company-field-selectors :input');
    var inputNames = new Set();
    allInputs.each(function(index, elm){
      inputNames.add($(elm).prop('name'));
    });
    var okToSubmit = true;
    var name = null;
    for (name of inputNames){
      var currentOption = $('input[name='+name+']:checked').val();
      if (!currentOption){
        okToSubmit = false;
        $('#error-message-'+name).text('You have to choose one of the options');
        if (typeof scrollToError == 'undefined'){
          var scrollToError = name;
        }
      } else {
        $('#error-message-'+name).text('');
        if (currentOption == 'database'){
          $('#id_'+name).val(companyDatabaseValues[name]);
        }
      }
    };
    if (okToSubmit){
      $('#company-match-value').val(matchedCompanyId);
      $('#registration-form').submit();
    } else {
      $('#company-field-compare-modal').animate({
        scrollTop: $('input[name='+scrollToError+']').offset().top
      }, 500);
    }
  });

  //////////////////////
  // Following code deals with matching current company to a d/b record onscreen
  // Used to facilitate data entry/matching
  //////////////////////

  // Trigger modal to look for matching company
  function triggerCompanySearchModal() {
    $('#id-company-name-match').val($('#id_company_name').val());
    $('#id-company-address-match').val($('#id_address1').val());
    $('#id-company-city-match').val($('#id_city').val());
    $('#id-company-postal-code-match').val($('#id_postal_code').val());
    $('#companyMatchModal').modal('show');
  };
  $('body').on('click', '#search-for-company', function(){
    triggerCompanySearchModal();
  });
  $('body').on('keypress', '#id_company_name', function(e){
    var key = e.which;
    var companyMatch = $('#company-match-value').val();
    if (key == 13 && companyMatch == '') {
      triggerCompanySearchModal();
    }
  });


  // Submit search for company match from optional modal
  $('body').on('click', '#btn-search-for-company', function(){
    var companyName = $('#id-company-name-match').val();
    var companyAddress = $('#id-company-address-match').val();
    var companyCity = $('#id-company-city-match').val();
    var companyPostalCode = $('#id-company-postal-code-match').val();
    if (companyName || companyAddress || companyCity || companyPostalCode) {
      $.ajax({
        url: '/delegate/suggest_company_match/',
        type: 'POST',
        data: {
          'company_name': companyName,
          'postal_code': companyPostalCode,
          'city': companyCity,
          'address1': companyAddress,
        },
        success: function(data){
          $('#suggested-match-list').html(data);
        }
      });
    };
  });


  // When company is selected, populate registration fields
  $('body').on('click', '#btn-select-company-match', function(){
    // 1 get value of selected company and make sure it's not 'new'
    var selectedCompanyId = $('input[name="company-match-select"]:checked').val();
    // 2 hit d/b to get values (in json)
    if (selectedCompanyId != 'new') {
      $.ajax({
        url: '/delegate/get_company_details/',
        type: 'GET',
        data: {
          'company': selectedCompanyId,
        },
        success: function(data){
          $('#id_company_name').val(data.name);
          $('#id_name_for_badges').val(data.name_for_badges);
          $('#id_address1').val(data.address1);
          $('#id_address2').val(data.address2);
          $('#id_city').val(data.city);
          $('#id_state_prov').val(data.state_prov);
          $('#id_postal_code').val(data.postal_code);
          $('#id_country').val(data.country);
          $('#id_gst_hst_exemption_number').val(data.gst_hst_exemption_number);
          $('#id_qst_exemption_number').val(data.qst_exemption_number);
          $('#id_gst_hst_exempt').prop('checked', data.gst_hst_exempt);
          $('#id_qst_exempt').prop('checked', data.qst_exempt);
          $('#company-match-value').val(data.id);
          // 3 Update tax rates
          if (data.gst_hst_exempt){
            $('#id_hst_rate').val(0);
            $('#id_gst_rate').val(0);
            updateTaxAndInvoice();
          };
          if (data.qst_exempt){
            $('#id_qst_rate').val(0);
            updateTaxAndInvoice();
          };
        }
      })
    }
    // 4 close modal
    $('#companyMatchModal').modal('hide');
  });


  ////////////////////
  // End previous section
  ///////////////////


  // Autocomplete for company name
  var companySuggestionClass = new Bloodhound({
    limit: 20,
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '/delegate/suggest_company/',
      replace: function(url, query){
        return url + '?q=' + query;
      },
      filter: function(my_Suggestion_class){
        return $.map(my_Suggestion_class, function(data){
          return {value: data.identifier};
        })
      }
    }
  });
  companySuggestionClass.initialize();
  $('#id_company_name').typeahead({
    hint: true,
    highligh: true,
    minLength: 1
  },
  {
    name: 'value',
    displayKey: 'value',
    source: companySuggestionClass.ttAdapter(),
    templates: {
      empty: [
        '<div class="tt-suggestion">',
        'No Items Found',
        '</div>'
      ].join('\n')
    }
  });

  ////////////////////
  // Code for delegate substitution
  ///////////////////

  // submit search from modal
  $('body').on('click', '#btn-search-for-substitute', function(){
    var confId = $('#selected-conference-id').val();
    var firstName = $('#id_substitute_first_name').val();
    var lastName = $('#id_substitute_last_name').val();
    var companyId = $('#company-match-value').val();
    $.ajax({
      url: '/delegate/search_for_substitute/',
      type: 'GET',
      data: {
        'conf_id': confId,
        'first_name': firstName,
        'last_name': lastName,
        'company_id': companyId,
      },
      success: function(data){
        $('#substitute-match-list').html(data);
      }
    });
  });

});
