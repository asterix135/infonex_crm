// Javascript for new.html page
$(document).ready(function() {

  // Add * to indicate required fields
  $('input,textarea,select').filter('[required]').parent().parent().find("label").append('<span class="required-label"> *</span>');


  // typeahead autocomplete for company field
  var my_Suggestion_class = new Bloodhound({
      limit: 10,
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/crm/suggest_company/',
        replace: function(url, query){
          return url + "?q=" + query;
        },
        filter: function(my_Suggestion_class) {
          return $.map(my_Suggestion_class, function(data){
            return {value: data.identifier};
          });
        }
      }
  });
  my_Suggestion_class.initialize();
  $('#id_company').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
  },
  {
      name: 'value',
      displayKey: 'value',
      source: my_Suggestion_class.ttAdapter(),
      templates: {
          empty: [
              '<div class="tt-suggestion">',
              'No Items Found',
              '</div>'
          ].join('\n')
      }
  });


  // Check for dupes on new record and either display modal or proceed
  $('body').on('click', '#save-new', function(){
    var name = $('#id_name').val();
    var title = $('#id_title').val();
    var company = $('#id_company').val();
    var city = $('#id_city').val();
    var phone = $('#id_phone').val();
    var email = $('#id_email').val();
    // 1. hit d/b to check if the new record is a potential dupe
    $.ajax({
      url: '/crm/check_for_dupes/',
      type: 'POST',
      data: {
        'name': name,
        'title': title,
        'company': company,
        'city': city,
        'phone': phone,
        'email': email,
      },
      success: function(data){
        var dupeListExists = $('#dupe-list-exists', data).val();
        // 2. if dupe - pull up modal with warning and dupes listed
        if (dupeListExists == 'True') {
          $('#dupe-modal-content').html(data);
          $('#possibleDuplicateModal').modal('show');
        } else {
          // 3. else - allow submission to proceed
          $('#new-person-form').submit();
        }
      }
    });
  });

});
