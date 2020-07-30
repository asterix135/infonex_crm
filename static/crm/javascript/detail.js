// Javascript for detail.html page
$(document).ready(function() {

  // load original values for form resets
  var originalName = $('#id_name').val();
  var originalTitle = $('#id_title').val();
  var originalDept = $('#person-edit-form-fields #id_dept').val();
  var originalCompany = $('#id_company').val();
  var originalCity = $('#id_city').val();
  var originalPhone = $('#id_phone').val();
  var originalPhoneAlternate = $('#id_phone_alternate').val();
  var originalPhoneMain = $('#id_phone_main').val();
  var originalDoNotCall = $('#id_do_not_call').prop('checked');
  var originalEmailBlocked = $('#id_email_blocked').prop('checked');
  var originalEmail = $('#id_email').val();
  var originalEmailAlternate = $('#id_email_alternate').val();
  var originalAssistantName = $('#id_assistant_name').val();
  var originalAssistantEmail = $('#id_assistant_email').val();
  var originalDoNotEmail = $('#id_do_not_email').prop('checked');
  var originalLinkedIn = $('#id_linkedin').val();
  var originalUrl = $('#id_url').val();
  var originalIndustry = $('#id_industry').val();
  // for category form
  var originalCatDept = $('#person-category-form-fields #id_dept').val();
  var originalCatGeo = $('#id_geo').val();
  var originalCatCat1 = $('#id_main_category').val();
  var originalCatCat2 = $('#id_main_category2').val();
  var originalCatDiv1 = $('#id_division1').val();
  var originalCatDiv2 = $('#id_division2').val();


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
    $('#id_phone_alternate').val(originalPhoneAlternate);
    $('#id_do_not_call').prop('checked', originalDoNotCall);
    $('#id_email').val(originalEmail);
    $('#id_email_alternate').val(originalEmailAlternate);
    $('#id_do_not_email').prop('checked', originalDoNotEmail);
    $('#id_email_blocked').prop('checked', originalEmailBlocked);
    $('#id_assistant_name').val(originalAssistantName);
    $('#id_assistant_email').val(originalAssistantEmail);
    $('#id_linkedin').val(originalLinkedIn);
    $('#id_url').val(originalUrl);
    $('#id_industry').val(originalIndustry);
  });


  // submit changes to person details and update that portion of page
  function updateHeader(data) {
    const newPhone = $('#id_phone', data).val();
    const newAltPhone = $('#id_phone_alternate', data).val();
    const newEmail = $('#id_email', data).val();
    const newAltEmail = $('#id_email_alternate', data).val();
    const newDoNotCall = $('#id_do_not_call', data).prop('checked');
    const newDoNotEmail = $('#id_do_not_email', data).prop('checked');
    const newEmailBlocked = $('#id_email_blocked', data).prop('checked');
    const newAsstName = $('#id_assistant_name', data).val();
    const newAsstEmail = $('#id_assistant_email', data).val();
    if (newPhone !== originalPhone || newDoNotCall !== originalDoNotCall) {
      let newPhoneHtml;
      if (newPhone) {
        newPhoneHtml = newPhone;
        if (newDoNotCall) {
           newPhoneHtml += '&nbsp;&nbsp;<span style="color:red;">(Do not call)</span>';
        };
      } else {
        newPhoneHtml = '<span style="font-weight:300; font-style:italic;">Unknown</span>';
      };
      $('#display-phone').html(newPhoneHtml);
    };
    if (newAltPhone !== originalPhoneAlternate || newDoNotCall !== originalDoNotCall) {
      let newAltPhoneHtml;
      if (newAltPhone) {
        newAltPhoneHtml = '<h5>Alternate Phone: ' + newAltPhone;
        if (newDoNotCall) {
          newAltPhoneHtml += '&nbsp;&nbsp;<span style="color:red;">(Do Not Call)</span>';
        }
        newAltPhoneHtml += '</h5>'
      } else {
        newAltPhoneHtml = '';
      };
      $('#display-phone-alternate').html(newAltPhoneHtml);
    };
    if (newEmail !== originalEmail || newDoNotEmail !== originalDoNotEmail || newEmailBlocked !== originalEmailBlocked) {
      let newEmailHtml;
      if (newEmail) {
        if (newDoNotEmail || newEmailBlocked) {
          newEmailHtml = newEmail;
          if (newDoNotEmail) {
            newEmailHtml += '&nbsp;&nbsp;<span style="color:red">(Do not email)</span>';
          };
          if (newEmailBlocked) {
            newEmailHtml += '&nbsp;<span style="color:crimson;">(Email Blocked)</span>';
          }
        } else {
          newEmailHtml = '<a href="mailto:' + newEmail + '">' + newEmail + '</a>'
        }
      } else {
        newEmailHtml = '<span style="font-weight: 300; font-style: italic">Unknown</span>';
      };
      $('#display-email').html(newEmailHtml);
    };
    if (newAltEmail !== originalEmailAlternate || newDoNotEmail !== originalDoNotEmail) {
      let newAltEmailHtml;
      if (newAltEmail) {
        newAltEmailHtml = '<h5>Alternate Email: ';
        if (newDoNotEmail) {
          newAltEmailHtml += newAltEmail + '&nbsp;&nbsp;<span style="color:red;">(Do not email)</span>';
        } else {
          newAltEmailHtml += '<a href="mailto:' + newAltEmail + '">' + newAltEmail + '</a>'
        }
        newAltEmailHtml += '</h5>'
      } else {
        newAltEmailHtml = '';
      };
      $('#display-email-alternate').html(newAltEmailHtml);
    };
    if (newAsstName !== originalAssistantName || newAsstEmail !== originalAssistantEmail) {
      let newAsstHtml;
      if (newAsstName || newAsstEmail) {
        newAsstHtml = '<h5>Assistant:&nbsp;&nbsp;';
        if (newAsstName) {
          newAsstHtml += newAsstName + '&nbsp;&nbsp;'
        };
        if (newAsstEmail) {
          newAsstHtml += '<a href="mailto:' + newAsstEmail + '">' + newAsstEmail + '</a>';
        };
        newAsstHtml += '</h5>'
      } else {
        newAsstHtml = ''
      };
      $('#display-assistant').html(newAsstHtml);
    }

  };


  $('body').on('click', '#save-person-details-form', function(){
    var personId = $('#person_id').val();
    var name = $('#id_name').val();
    var title = $('#id_title').val();
    var dept = $('#person-edit-form-fields #id_dept').val();
    var company = $('#id_company').val();
    var city = $('#id_city').val();
    var phone = $('#id_phone').val();
    var phoneAlternate = $('#id_phone_alternate').val();
    var phoneMain = $('#id_phone_main').val();
    var doNotCall = $('#id_do_not_call').prop('checked');
    var emailBlocked = $('#id_email_blocked').prop('checked');
    var email = $('#id_email').val();
    var emailAlternate = $('#id_email_alternate').val();
    var assistantName = $('#id_assistant_name').val();
    var assistantEmail = $('#id_assistant_email').val();
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
        'phone_alternate': phoneAlternate,
        'phone_main': phoneMain,
        'do_not_call': doNotCall,
        'email': email,
        'email_alternate': emailAlternate,
        'do_not_email': doNotEmail,
        'email_blocked': emailBlocked,
        'assistant_name': assistantName,
        'assistant_email': assistantEmail,
        'linkedin': linkedIn,
        'url': url,
        'industry': industry,
      },
      success: function(data){
        $('#person-detail-edit-panel').html(data);
        successFlag = $('#updated-details-success', data).val();
        if (successFlag == 'True') {
          updateHeader(data);
          originalName = $('#id_name', data).val();
          originalTitle = $('#id_title', data).val();
          originalDept = $('#id_dept', data).val();
          originalCompany = $('#id_company', data).val();
          originalCity = $('#id_city', data).val();
          originalPhone = $('#id_phone', data).val();
          originalPhoneAlternate = $('#id_phone_alternate', data).val();
          originalPhoneMain = $('#id_phone_main', data).val();
          originalDoNotCall = $('#id_do_not_call', data).prop('checked');
          originalEmail = $('#id_email', data).val();
          originalEmailAlternate = $('#id_email_alternate', data).val();
          originalDoNotEmail = $('#id_do_not_email', data).prop('checked');
          originalEmailBlocked = $('#id_email_blocked', data).prop('checked');
          originalAssistantName = $('#id_assistant_name', data).val();
          originalAssistantEmail = $('#id_assistant_email', data).val();
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


  // delete contact history entry
  $('body').on('click', '.delete-contact-history', function(){
    var personId = $('#person_id').val();
    var contactId = $(this).attr('contact-id');
    $.ajax({
      url: '/crm/delete_contact_history/',
      type: 'POST',
      data: {
        'person_id': personId,
        'contact_id': contactId,
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
    $('#id_division2').val(originalCatDiv2);
  });


  // Submit category changes and update
  $('body').on('click', '#save-person-categories', function(){
    var personId = $('#person_id').val();
    var dept = $('#person-category-form-fields #id_dept').val();
    var geo = $('#id_geo').val();
    var mainCategory = $('#id_main_category').val();
    var mainCategory2 = $('#id_main_category2').val();
    var division1 = $('#id_division1').val();
    var division2 = $('#id_division2').val();
    $.ajax({
      url: '/crm/save_category_changes/',
      type: 'POST',
      data: {
        'person_id': personId,
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
          originalCatDiv2 = $('#id_division2', data).val();
        }
      }
    });
  });


  // Trigger delete confirm modal and add delete form content
  $('body').on('click', '#delete-person-btn', function(){
    $('#deleteConfirmModal').modal('show');
    $('#delete-person-form').attr('action', '/crm/delete/');
    var personId = $('#person_id').val();
    $('#delete-form-content').html(
      '<input type="hidden" name="person_id" value="' + personId + '"/>'
    )
  });


  // Delete record on user confirmation
  $('body').on('click', '#save-after-dupe-check', function(){
    $('#delete-person-form').submit();
  })


  // Process flag change
  $('body').on('click', '.flag-icon', function(){
    var personId = $('#person_id').val();
    var flagColor = $(this).attr('flag-color');
    var eventAssignmentId = $('#my-event-assignment').val();
    $.ajax({
      url: '/crm/change_flag/',
      type: 'POST',
      data: {
        'person_id': personId,
        'flag_color': flagColor,
        'event_assignment_id': eventAssignmentId,
      },
      success: function(data){
        $('#flag-button').html(data);
      }
    });
  });


  // Toggle whether person in current territory
  $('body').on('click', '.territory-toggle-button', function(){
    var personId = $('#person_id').val();
    var eventAssignmentId = $('#my-event-assignment').val();
    var toggleTo = $(this).attr('toggle-to');
    $.ajax({
      url: '/crm/toggle_person_in_territory/',
      type: 'POST',
      data: {
        'person_id': personId,
        'toggle_to': toggleTo,
        'event_assignment_id': eventAssignmentId,
      },
      success: function(data){
        $('#action-buttons').html(data);
      }
    });
  });


  // Duplicate current person into new record (pre-populated)
  $('body').on('click', '#duplicate-current-person', function(){
    var emailStringArray = originalEmail.split("@");
    var domainStringLocation = emailStringArray.length -1;
    var emailDomain = emailStringArray[domainStringLocation];
    if (emailDomain.length > 0) {emailDomain = '@' + emailDomain};
    // csrf value below comes from ajax_setup.js
    var formHtml = '<form action="/crm/new/" method="post">' +
                   '<input name="csrfmiddlewaretoken" value="' + csrfValue +'" type="hidden"/>' +
                   '<input type="hidden" name="dept" value="' + originalCatDept + '"/>' +
                   '<input type="hidden" name="company" value="' + originalCompany + '"/>' +
                   '<input type="hidden" name="city" value="' + originalCity + '"/>' +
                   '<input type="hidden" name="phone" value="' + originalPhone + '"/>' +
                   '<input type="hidden" name="phone_alternate" value="' + originalPhoneAlternate + '"/>' +
                   '<input type="hidden" name="email" value="' + emailDomain + '"/>' +
                   '<input type="hidden" name="email_alternate" value="' + originalEmailAlternate + '"/>' +
                   '<input type="hidden" name="phone_main" value="' + originalPhoneMain + '"/>' +
                   '<input type="hidden" name="url" value="' + originalUrl + '"/>' +
                   '<input type="hidden" name="industry" value="' + originalIndustry + '"/>' +
                   '<input type="hidden" name="geo" value="' + originalCatGeo + '"/>' +
                   '<input type="hidden" name="main_category" value="' + originalCatCat1 + '"/>' +
                   '<input type="hidden" name="main_category2" value="' + originalCatCat2 + '"/>' +
                   '<input type="hidden" name="division1" value="' + originalCatDiv1 + '"/>' +
                   '<input type="hidden" name="division2" value="' + originalCatDiv2 + '"/>' +
                   '<input type="hidden" name="dupe_creation" value=""/>' +
                   '</form>';
    $(formHtml).appendTo('body').submit();
  });

});
