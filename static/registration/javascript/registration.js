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
      }
    });
  });


  function disableDataExport(){
    var docFormat = $('input[name="report_format"]:checked').val();
    if (docFormat != 'pdf') {
      $('input[name="report_format"][value="pdf"]').prop('checked', true);
    };
    $('input[name="report_format"]').attr('disabled', true);
  }

  function disableSort(sortVal='name'){
    var currentSortVal = $('input[name="sort"]:checked').val();
    if (currentSortVal != sortVal) {
      $('input[name="sort"][value="' + sortVal + ']').prop('checked', true);
    };
    $('input[name="sort"]').attr('disabled', true);
  }

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
    } else {
      console.log('not ok');
    };

  });
});
