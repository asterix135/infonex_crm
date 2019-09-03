$(document).ready(function() {
  // startTypeAhead();

  // typeahead autocomplete for dept, industry & company fields
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
  var companySuggestionClass = new Bloodhound({
      limit: 20,
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
  companySuggestionClass.initialize();
  // var industrySuggestionClass = new Bloodhound({
  //     limit: 20,
  //     datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  //     queryTokenizer: Bloodhound.tokenizers.whitespace,
  //     remote: {
  //       url: '/crm/suggest_industry/',
  //       replace: function(url, query){
  //         return url + "?q=" + query;
  //       },
  //       filter: function(my_Suggestion_class) {
  //         return $.map(my_Suggestion_class, function(data){
  //           return {value: data.identifier};
  //         });
  //       }
  //     }
  // });
  // industrySuggestionClass.initialize();


  // function that will start the typeahead (needs to be called after each ajax)
  function startTypeAhead(){
    $('#id_dept').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'value',
        displayKey: 'value',
        source: deptSuggestionClass.ttAdapter(),
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

    // $('#master #id_industry, #person-select-options #id_industry').typeahead({
    //     hint: true,
    //     highlight: true,
    //     minLength: 2
    // },
    // {
    //     name: 'value',
    //     displayKey: 'value',
    //     source: industrySuggestionClass.ttAdapter(),
    //     templates: {
    //         empty: [
    //             '<div class="tt-suggestion">',
    //             'No Items Found',
    //             '</div>'
    //         ].join('\n')
    //     }
    // });
  };

  // $('body').on('click', '#id_company', function(){
  //   startTypeAhead();
  // });
  startTypeAhead();

});
