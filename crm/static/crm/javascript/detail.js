// Javascript for detail.html page
$(document).ready(function() {

  // load original values for form resets
  var originalName = $('#id_name').val();
  var originalTitle = $('#id_title').val();
  var originalDept = $('#person-edit-form-fields #id_dept').val();
  var originalCompany = $('#id_company').val();
  var originalCity = $('#id_city').val();
  var originalPhone = $('#id_phone').val();
  var originalPhoneMain = $('#id_phone_main').val();
  var originalDoNotCall = $('#id_do_not_call').prop('checked');
  var originalEmail = $('#id_email').val();
  var originalDoNotEmail = $('#id_do_not_email').prop('checked');
  var originalLinkedIn = $('#id_linkedin').val();
  var originalUrl = $('#id_url').val();
  var originalIndustry = $('id_industry').val();
  // for category form
  var originalCatDept = $('#person-category-form-fields #id_dept').val();
  var originalCatGeo = $('#id_geo').val();
  var originalCatCat1 = $('#id_main_category').val();
  var originalCatCat2 = $('#id_main_category2').val();
  var originalCatDiv1 = $('#id_division1').val();
  var originalCagDiv2 = $('#id_division2').val();


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
    $('#person-edit-form-fields #id_dept').val(originalDept);
    $('#id_company').val(originalCompany);
    $('#id_city').val(originalCity);
    $('#id_phone').val(originalPhone);
    $('#id_phone_main').val(originalPhoneMain);
    $('#id_do_not_call').prop('checked', originalDoNotCall);
    $('#id_email').val(originalEmail);
    $('#id_do_not_email').prop('checked', originalDoNotEmail);
    $('#id_linkedin').val(originalLinkedIn);
    $('#id_url').val(originalUrl);
    $('#id_industry').val(originalIndustry);
  });


  // submit changes to person details and update that portion of page
  $('body').on('click', '#save-person-details-form', function(){
    var personId = $('#person_id').val();
    var name = $('#id_name').val();
    var title = $('#id_title').val();
    var dept = $('#person-edit-form-fields #id_dept').val();
    var company = $('#id_company').val();
    var city = $('#id_city').val();
    var phone = $('#id_phone').val();
    var phoneMain = $('#id_phone_main').val();
    var doNotCall = $('#id_do_not_call').prop('checked');
    var email = $('#id_email').val();
    var doNotEmail = $('#id_do_not_email').prop('checked');
    var linkedIn = $('#id_linkedin').val();
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
        'linkedin': linkedIn,
        'url': url,
        'industry': industry,
      },
      success: function(data){
        $('#person-detail-section').html(data);
        successFlag = $('#updated-details-success', data).val();
        if (successFlag == 'True') {
          originalName = $('#id_name', data).val();
          originalTitle = $('#id_title', data).val();
          originalDept = $('#id_dept', data).val();
          originalCompany = $('#id_company', data).val();
          originalCity = $('#id_city', data).val();
          originalPhone = $('#id_phone', data).val();
          originalPhoneMain = $('#id_phone_main', data).val();
          originalDoNotCall = $('#id_do_not_call', data).prop('checked');
          originalEmail = $('#id_email', data).val();
          originalDoNotEmail = $('#id_do_not_email', data).prop('checked');
          originalLinkedIn = $('#id_linkedin', data).val();
          originalUrl = $('#id_url', data).val();
          originalIndustry = $('id_industry', data).val();
        };
      }
    });
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


  // Toggle Reg History Panel
  $('body').on('click', '#hide-reg-history', function(){
    if ($(this).hasClass('glyphicon-chevron-down')){
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#reg-history-detail').collapse('show');
    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $('#reg-history-detail').collapse('hide');
    };
  });


  // Toggle Category panel
  $('body').on('click', '#btn-toggle-category', function(){
    if ($(this).hasClass('glyphicon-chevron-down')){
      $(this).removeClass('glyphicon-chevron-down');
      $(this).addClass('glyphicon-chevron-up');
      $('#person-category-form-fields').collapse('show');
    } else {
      $(this).removeClass('glyphicon-chevron-up');
      $(this).addClass('glyphicon-chevron-down');
      $('#person-category-form-fields').collapse('hide');
    };
  });


  // reset Contact History Form Values
  $('body').on('click', '#reset-contact-history-form', function(){
    $('#id_event').val('');
    $('#id_method').val('Pitch');
    $('#id_notes').val('');
  });


  // submit new contact history and update contact history panel
  $('body').on('click', '#save-contact-history-form', function(){
    var personId = $('#person_id').val();
    var contactEvent = $('#id_event').val();
    var contactMethod = $('#id_method').val();
    var contactNotes = $('#id_notes').val();
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


  // Reset catgory panel
  $('body').on('click', '#reset-person-categories', function(){
    $('#person-category-form-fields #id_dept').val(originalCatDept);
    $('#id_geo').val(originalCatGeo);
    $('#id_main_category').val(originalCatCat1);
    $('#id_main_category2').val(originalCatCat2);
    $('#id_division1').val(originalCatDiv1);
    $('#id_division2').val(originalCagDiv2);
  });


  // Submit category changes and update
  $('body').on('click', '#save-person-categories', function(){
    var personId = $('#person_id').val();
    var dept = $('#person-category-form-fields #id_dept').val();
    var geo = $('#id_geo').val();
    var mainCategory = $('#id_main_category').val();
    var mainCategory2 = $('id_main_category2').val();
    var division1 = $('id_division1').val();
    var division2 = $('id_division2').val();
    $.ajax({
      url: '/crm/save_category_changes/',
      type: 'POST',
      data: {
        'dept': dept,
        'geo': geo,
        'main_category': mainCategory,
        'main_category2': mainCategory2,
        'division1': division1,
        'division2': division2,
      },
      success: function(data){
        $('#person-category-panel').html(data);
        successFlag = $('#updated-category-success', data).val();
        if (successFlag == 'True'){
          originalCatDept = $('#id_dept', data).val();
          originalCatGeo = $('#id_geo', data).val();
          originalCatCat1 = $('#id_main_category', data).val();
          originalCatCat2 = $('#id_main_category2', data).val();
          originalCatDiv1 = $('#id_division1', data).val();
          originalCagDiv2 = $('#id_division2', data).val();
        }
      }
    });
  });

});
