// Javascript for detail.html page
$(document).ready(function() {

  // load original values for form resets
  var originalName = $('#id_name').val();
  var originalTitle = $('#id_title').val();
  var originalDept = $('#id_dept').val();
  var originalCompany = $('#id_company').val();
  var originalCity = $('#id_city').val();
  var originalPhone = $('#id_phone').val();
  var originalPhoneMain = $('#id_phone_main').val();
  var originalDoNotCall = $('#id_do_not_call').prop('checked');
  var originalEmail = $('#id_email').val();
  var originalDoNotEmail = $('#id_do_not_email').prop('checked');
  var originalUrl = $('#id_url').val();
  var originalIndustry = $('id_industry').val();
  // for contact history form
  var originalContactEvent = '';
  var originalContactMethod = 'Pitch';
  var originalContactNotes = '';


  // open person's website in new page
  $('body').on('click', '#open-contact-website', function(){
    var url=$('#id_url').val();
    if (url.slice(0,8).toLowerCase() != 'http://'){
      url = 'http://'.concat(url);
    };
    window.open(url, '_blank');
  });


  // reset Person Details Form Values
  $('body').on('click', '#reset-person-details-form', function(){
    $('#id_name').val(originalName);
    $('#id_title').val(originalTitle);
    $('#id_dept').val(originalDept);
    $('#id_company').val(originalCompany);
    $('#id_city').val(originalCity);
    $('#id_phone').val(originalPhone);
    $('#id_phone_main').val(originalPhoneMain);
    $('#id_do_not_call').prop('checked', originalDoNotCall);
    $('#id_email').val(originalEmail);
    $('#id_do_not_email').prop('checked', originalDoNotEmail);
    $('#id_url').val(originalUrl);
    $('#id_industry').val(originalIndustry);
  });


  // submit changes to person details and update that portion of page
  $('body').on('click', '#save-person-details-form', function(){
    var personId = $('#person_id').val();
    var name = $('#id_name').val();
    var title = $('#id_title').val();
    var dept = $('#id_dept').val();
    var company = $('#id_company').val();
    var city = $('#id_city').val();
    var phone = $('#id_phone').val();
    var phoneMain = $('#id_phone_main').val();
    var doNotCall = $('#id_do_not_call').prop('checked');
    var email = $('#id_email').val();
    var doNotEmail = $('#id_do_not_email').prop('checked');
    var url = $('#id_url').val();
    var industry = $('#id_industry').val();
    $.ajax({
      url: '/crm/save_person_details/',
      type: 'POST',
      data: {
        'person_id': personId,
        'name': name,
        'title': title,
        'dept': dept,
        'company': company,
        'city': city,
        'phone': phone,
        'phone_main': phoneMain,
        'do_not_call': doNotCall,
        'email': email,
        'do_not_email': doNotEmail,
        'url': url,
        'industry': industry,
      },
      success: function(data){
        $('#person-detail-section').html(data);
      }
    })
  });


  // Toggle Add Contact Pane
  $('body').on('click', '#add-contact-history', function(){
    if ($('#add-contact-history-form').hasClass('collapse in')){
      $('#add-contact-history').removeClass('glyphicon-chevron-up');
      $('#add-contact-history').addClass('glyphicon-plus');
      $('#add-contact-history-form').collapse('hide');
    } else {
      $('#add-contact-history').removeClass('glyphicon-plus');
      $('#add-contact-history').addClass('glyphicon-chevron-up');
      $('#add-contact-history-form').collapse('show');
    };
  });


  // Toggle Edit Person Details panel
  $('body').on('click', '#btn-toggle-edit-person', function(){
    if ($(this).hasClass('glyphicon-chevron-down')){
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#person-edit-form-fields').collapse('show');
    } else {
      $(this).removeClass('glpyhicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $('#person-edit-form-fields').collapse('hide');
    };
  });

  // reset Contact History Form Values
  $('body').on('click', '#reset-contact-history-form', function(){
    $('#id_event').val(originalContactEvent);
    $('#id_method').val(originalContactMethod);
    $('#id_notes').val(originalContactNotes);
  });


  // submit new contact history and update contact history panel
  $('body').on('click', '#save-contact-history-form', function(){
    var personId = $('#person_id').val();
    var contactEvent = $('#id_event').val();
    var contactMethod = $('#id_method').val();
    var contactNotes = $('#id_notes').val();
    originalContactEvent = contactEvent;
    originalContactMethod = contactMethod;
    originalContactNotes = contactNotes;
    $.ajax({
      url: '/crm/add_contact_history/',
      type: 'POST',
      data: {
        'person_id': personId,
        'event': contactEvent,
        'method': contactMethod,
        'notes': contactNotes,
      },
      success: function(data){
        $('#person-contact-history-panel').html(data);
        var foo = $(data).find('#id_event').val();
      }
    });
  });

  // Toggle display of more than 5 contact history entries
  $('body').on('click', '#show-entire-contact-history', function(){
    var buttonText = $(this).text().trim();
    if (buttonText == 'Show All'){
      $(this).text('Show 5');
      $('#contact-history-panel-text').text('Contact History (All)');
    } else {
      var contactCount = $('.contact-history-entry').length;
      $(this).text('Show All');
      $('#contact-history-panel-text').text('Contact History (5 of ' + contactCount + ')');
    };
    $('.overflow-contact').toggle();
  });

});
