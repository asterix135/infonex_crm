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


  // Need logic to hide/disable radio buttons based on other selections
  $('body').on('change', 'input[name=report]', function(){
    var newReport = $(this).val();
      switch (newReport) {
        case 'Delegate':
          console.log('you chose delegate');
          $('input[name=sort][value=name]').attr('disabled', true)
          break;
        case 'NoName':
          console.log('you chose noname');
          $('input[name=sort][value=name]').attr('disabled', false);
          break;
        case 'Registration':
          console.log('you chose registration');
          break;
        case 'Phone':
          console.log('you chose phone');
          break;
        case 'Onsite':
          console.log('you chose onsite');
          break;
        case 'Unpaid':
          console.log('you chose unpaid');
          break;
        case 'CE':
          console.log('you chose CE');
          break;
        case 'Badges':
          console.log('you chose badges');
          break;
        case 'Counts':
          console.log('you chose counts');
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
