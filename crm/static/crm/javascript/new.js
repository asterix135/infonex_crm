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

});
