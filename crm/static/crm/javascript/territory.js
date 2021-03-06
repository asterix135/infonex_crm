// Javascript for territory.html page

// Force page to reload on back button
if(performance.navigation.type == 2){
   location.reload(true);
}

$(document).ready(function() {

  var eventAssignmentId = $('#my-event-assignment').val();
  var blankFormSubmitOK = true;

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
    $('.personal-flag-select').each(function(){
      $(this).prop('checked', checkedStatus);
    });
  });


  // process batch flag changes
  $('body').on('click', '.master-flag-icon', function(){
    var flagColor = $(this).attr('flag-color');
    var checkedPeople = []
    var page = $('#active-page-box').attr('page-val');
    $('.personal-flag-select').each(function(){
      if ($(this).is(':checked')){
        checkedPeople.push($(this).attr('select-person'));
      };
    });
    $.ajax({
      url: '/crm/group_flag_update/',
      type: 'POST',
      data: {
        'checked_people': checkedPeople,
        'event_assignment_id': eventAssignmentId,
        'flag_color': flagColor,
        'page': page,
      },
      success: function(data){
        $('#my-territory-list-panel').html(data);
      }
    });
  });


  // toggle territory filter and set cookie on server-side
  $('body').on('click', '#btn-toggle-filter-options', function(){
    if ($(this).hasClass('glyphicon-chevron-down')) {
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#filter-panel').collapse('show');
      var hideFilter = false;
    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $('#filter-panel').collapse('hide');
      var hideFilter = true;
    };
    $.ajax({
      url: '/crm/toggle_territory_filter/',
      type: 'GET',
      data: {
        'hide': hideFilter,
      }
    });
  });

  // Respond to flag choice in filter box
  $('body').on('click', '.flag-filter-choice', function(){
    var flagColor = $(this).attr('flag-color');
    $('#id_flag').val(flagColor);
    switch (flagColor) {
      case 'any':
        buttonHtml = 'Select Flag <span class="caret"></span>';
        break;
      case 'red':
        buttonHtml = '<span class="glyphicon glyphicon-flag red-flag filter-flag-icon"></span>Red <span class="caret"></span>';
        break;
      case 'green':
        buttonHtml = '<span class="glyphicon glyphicon-flag green-flag filter-flag-icon"></span>Green <span class="caret"></span>';
        break;
      case 'blue':
        buttonHtml = '<span class="glyphicon glyphicon-flag blue-flag filter-flag-icon"></span>Blue <span class="caret"></span>';
        break;
      case 'black':
        buttonHtml = '<span class="glyphicon glyphicon-flag black-flag filter-flag-icon"></span>Black <span class="caret"></span>';
        break;
      case 'yellow':
        buttonHtml = '<span class="glyphicon glyphicon-flag yellow-flag filter-flag-icon"></span>Yellow <span class="caret"></span>';
        break;
      case 'purple':
        buttonHtml = '<span class="glyphicon glyphicon-flag purple-flag filter-flag-icon"></span>Purple <span class="caret"></span>';
        break;
      case 'none':
        buttonHtml = '<span class="glyphicon glyphicon-ban-circle no-flag filter-flag-icon"></span>None <span class="caret"></span>';
    };
    $('#btn-flag-filter-select').html(buttonHtml);
  });


  function clearFilterForm(){
    $('#id_name').val('');
    $('#id_title').val('');
    $('#id_company').val('');
    $('#id_state_province').val('');
    $('#id_past_customer').val('');
    $('#id_dept').val('');
    $('#id_area_code').val('');
    $('#id_flag').val('any');
  };


  // button action to clear filter form
  $('body').on('click', '#btn-clear-filter', function(){
    clearFilterForm();
    $('#btn-flag-filter-select').html('Select Flag <span class="caret"></span>');
  });


  // check if at least one field is filled in and if so submit filter form
  function submitFilter(){
    var okToSubmit = false;
    if (
      $('#id_name').val() != '' ||
      $('#id_title').val() != '' ||
      $('#id_company').val() != '' ||
      $('#id_state_province').val() != '' ||
      $('#id_dept').val() != '' ||
      $('#id_past_customer').val() != '' ||
      $('#id_flag').val() != 'any' ||
      $('#id_area_code').val() != ''
    ) {
      okToSubmit = true;
    };
    if (okToSubmit){
      $('#filter-form').submit();
    };
  };
  $('#btn-submit-filter').click(function(){
    submitFilter();
  });
  $('body').on('keyup', '.search-field', function(e){
    if (e.which == 13) {
      submitFilter();
    }
  })


  // reset filter details and submit blank form
  $('#btn-see-all-contacts').click(function(){
    clearFilterForm();
    blankFormSubmitOK = true
    $('#filter-form').submit();
  });


  // Toggle company view
  $('body').on('click', '#toggle-company-view', function(){
    let targetUrl = window.location.href;
    const idxOfQuestionMark = targetUrl.indexOf('?');
    if (idxOfQuestionMark > -1) {
      if (targetUrl.includes('view=company')) {
        targetUrl = targetUrl.slice(0, idxOfQuestionMark);
      } else {
        targetUrl = targetUrl.slice(0, idxOfQuestionMark) + '?view=company';
      }
    } else {
      targetUrl = targetUrl.slice(0, idxOfQuestionMark) + '?view=company';
    }
    window.location.href = targetUrl;
  });

  // Select company from company view
  $('body').on('click', '.company-name-as-link', function(){
    const companyName = $(this).text();
    clearFilterForm();
    $('#id_company').val(companyName);
    $('#filter-form').submit();
  })


});
