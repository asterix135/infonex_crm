$(document).ready(function() {

  var deptSuggestionClass = new Bloodhound({
      limit: 20,
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/crm/suggest_dept/',
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
  deptSuggestionClass.initialize();


});
