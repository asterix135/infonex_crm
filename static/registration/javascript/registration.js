$(document).ready(function(){
  var activePanel = '';

  // Load ajax panels
  $('body').on('click', '.ajax-load', function(){
    var ajaxPayload = $(this).attr('ajax-target');
    $.ajax({
      url: '/registration/index_panel/',
      type: 'GET',
      data: {
        'panel': ajaxPayload,
      },
      success: function(data) {
        $('#ajax-content').html(data);
        activePanel = ajaxPayload;
        if (ajaxPayload == 'reg-search') {
          startTypeAhead()
        };
      }
    });
  });

  // Load invoice search ajax panel
  function invoiceQuickSearch(){
    var invoiceNumber = $('#invoice-search-box').val();
    $.ajax({
      url: '/registration/index_panel',
      type: 'GET',
      data: {
        'panel': 'invoice-quick-search',
        'invoice_number': invoiceNumber,
      },
      success: function(data){
        $('#ajax-content').html(data);
      }
    });
  };
  $('body').on('click', '#invoice-search-btn', function(){
    invoiceQuickSearch();
  });
  $('body').on('keypress', '#invoice-search-box', function(e){
    var key = e.which;
    if (key == 13){
      invoiceQuickSearch();
    }
  })

  //////////////////////////
  // Next section of code is related to manipulation of admin reports search panel
  //////////////////////////
  function disableDataExport(){
    var docFormat = $('input[name="report_format"]:checked').val();
    if (docFormat != 'pdf') {
      $('input[name="report_format"][value="pdf"]').prop('checked', true);
    };
    $('input[name="report_format"]').attr('disabled', true);
  }

  function disablePdf(){
    var docFormat = $('input[name="report_format"]:checked').val();
    if (docFormat == 'pdf') {
      $('input[name="report_format"][value="csv"]').prop('checked', true);
    };
    $('input[name="report_format"]').attr('disabled', true);
  }

  function disableSort(sortVal){
    if (sortVal === undefined){
      sortVal='name';
    }
    var currentSortVal = $('input[name="sort"]:checked').val();
    if (currentSortVal != sortVal) {
      $('input[name="sort"][value="' + sortVal + ']').prop('checked', true);
    };
    $('input[name="sort"]').attr('disabled', true);
  };

  function enableAllRadios(){
    $('input[type="radio"]').attr('disabled', false);
  }

  // Logic to hide/disable radio buttons based on other selections
  $('body').on('change', 'input[name="report"]', function(){
    var newReport = $(this).val();
      switch (newReport) {
        case 'Delegate':
        case 'Registration':
        case 'Phone':
          enableAllRadios();
          break;
        case 'NoName':
          enableAllRadios();
          var currentSortVal = $('input[name="sort"]:checked').val();
          if (currentSortVal == 'name') {
            $('input[name="sort"][value="company"]').prop('checked', true);
          }
          $('input[name="sort"][value="name"]').attr('disabled', true);
          break;
        case 'Unpaid':
          enableAllRadios();
          disableDataExport();
          var currentSortVal = $('input[name="sort"]:checked').val();
          if (currentSortVal == 'title') {
            $('input[name="sort"][value="name"]').prop('checked', true);
          }
          $('input[name="sort"][value="title"]').attr('disabled', true);
          break;
        case 'Onsite':
        case 'CE':
        case 'Badges':
        case 'Counts':
          enableAllRadios();
          disableSort();
          disableDataExport();
          break;
        case "Speaker":
          enableAllRadios();
          disablePdf();
          break;
      }
  });

  // Submit form generation request (admin)
  $('body').on('click', '#submit-admin-reports', function(){
    var confId = $('#id_event').val();
    var reportType = $('input[name=report]:checked').val();
    var sort = $('input[name=sort]:checked').val();
    var destination = $('input[name=destination]:checked').val();
    var docFormat = $('input[name=report_format]:checked').val();
    if (confId && reportType && sort && destination && docFormat) {
      var url = '/registration/get_admin_reports?event=' + confId;
      url += '&sort=' + sort;
      url += '&destination=' + destination;
      url += '&doc_format=' + docFormat;
      url += '&report=' + reportType;
      window.open(url, '_blank');
    };
  });


  ////////////////////////
  // Code related to mass mailings
  ////////////////////////
  $('body').on('change', 'input[name="mass_mail_message"], #mass-mail-conf-select > #id_event', function(){
    var confId = $('#id_event').val();
    var selectedMail = $('input[name="mass_mail_message"]:checked').val();
    if (confId && selectedMail) {
      $.ajax({
        url: '/registration/mass_mail_details/',
        type: 'GET',
        data: {
          'message': selectedMail,
          'event': confId,
        },
        success: function(data) {
          $('#merge-field-details').html(data);
          if (!$('#merge-submit-button').hasClass('in')) {
            $('#merge-submit-button').addClass('in');
          }
        }
      })
    }
  });


  ////////////////////////
  // Code related to sales reports
  ////////////////////////
  $('body').on('click', '#submit-sales-reports', function(){
    var reportDateMonth = $('#id_report_date_month').val();
    var reportDateYear = $('#id_report_date_year').val();
    if (reportDateMonth && reportDateYear) {
      var url = '/registration/get_sales_reports?report_date_month=';
      url += reportDateMonth + '&report_date_year=' + reportDateYear;
      window.open(url, '_blank');
    };
  });


  ////////////////////////
  // Code related to event revenue report
  ////////////////////////
  $('body').on('click', '#submit-event-revenue', function(){
    var confId = $('#id_event').val();
    var destination = $('input[name=destination]:checked').val();
    var docFormat = $('input[name=report_format]:checked').val();
    if (confId && destination && docFormat){
      var url = '/registration/event_revenue?event=' + confId;
      url += '&destination=' + destination;
      url += '&doc_format=' + docFormat;
      window.open(url, '_blank');
    };
  });


  ///////////////////////
  // Next section of code is related to invoice/registration search
  ///////////////////////
  function findRegistration(){
    var invoiceNumber = $('#invoice_number').val();
    var confId = $('#id_event').val();
    var firstName = $('#id_first_name').val();
    var lastName = $('#id_last_name').val();
    var company = $('#id_company').val();
    if (invoiceNumber || confId || firstName || lastName || company) {
      $.ajax({
        url: '/registration/find_reg/',
        type: 'POST',
        data: {
          'invoice_number': invoiceNumber,
          'conf_id': confId,
          'first_name': firstName,
          'last_name': lastName,
          'company': company
        },
        success: function(data, status, xhr){
          var ct = xhr.getResponseHeader('content-type') || '';
          // Check whether response is html or json
          if (ct.indexOf('html') > -1){
            $('#reg-results').html(data);
          }
          if (ct.indexOf('json') > -1){
            $(location).attr('href', '/delegate?reg_id=' + data.reg_id)
          }
        }
      });
    }
  };

  $('body').on('click', '#submit-reg-search', function(){
    findRegistration();
  });
  $('body').on('keypress', '#invoice_number', function(e){
    var key = e.which;
    if (key == 13) {
      findRegistration();
    }
  });


  ////////////////////////////
  // Code from here to end is related to typeahead for first_name, last_name and company
  ////////////////////////////
  var firstNameSuggestionClass = new Bloodhound({
    limit: 20,
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '/registration/suggest_first_name/',
      replace: function(url, query){
        return url + '?q=' + query;
      },
      filter: function(my_Suggestion_class) {
        return $.map(my_Suggestion_class, function(data){
          return {value: data.identifier};
        });
      }
    }
  });
  firstNameSuggestionClass.initialize();


  var lastNameSuggestionClass = new Bloodhound({
    limit: 20,
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '/registration/suggest_last_name/',
      replace: function(url, query){
        return url + '?q=' + query;
      },
      filter: function(my_Suggestion_class) {
        return $.map(my_Suggestion_class, function(data){
          return {value: data.identifier};
        });
      }
    }
  });
  lastNameSuggestionClass.initialize();


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


  function startTypeAhead(){
    $('#id_first_name').typeahead({
      hint: true,
      highlight: true,
      minLength: 2
    },
    {
      name: 'value',
      displayKey: 'value',
      source: firstNameSuggestionClass.ttAdapter(),
      templates: {
          empty: [
              '<div class="tt-suggestion">',
              'No Items Found',
              '</div>'
          ].join('\n')
      }
    });

    $('#id_last_name').typeahead({
      hint: true,
      highlight: true,
      minLength: 2
    },
    {
      name: 'value',
      displayKey: 'value',
      source: lastNameSuggestionClass.ttAdapter(),
      templates: {
          empty: [
              '<div class="tt-suggestion">',
              'No Items Found',
              '</div>'
          ].join('\n')
      }
    });

    $('#id_company').typeahead({
      hint: true,
      highlight: true,
      minLength: 2
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
  };

});
