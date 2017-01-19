// Javascript for manage_territory.html page
$(document).ready(function() {

  // Show modal on load if form errors
  var newConferenceFormHasErrors = $('#new-conference-form-has-errors').val();
  if (newConferenceFormHasErrors == 'true'){
    $('#modal-quick-add-event').modal('show');
  };


  // Update assignments after drag/drop of users
  function updateAssignments(userId, receiverId){
    var confId = $('#id_event').val();
    $.ajax({
      url: '/crm/update_user_assignments/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'user_id': userId,
        'role': receiverId,
      }
    });
  };


  // Activate Drag Drop Sortation (called after AJAX load)
  function startDragDrop() {
    $('.connectedSortable').sortable({
      connectWith: '.connectedSortable',
      receive: function(event, ui){
        var movedId = ui.item.attr('user-id');
        var movedItem = ui.item;
        var receiverId = $(this).attr('id');
        var sender = ui.sender;
        var receiver = $(this);
        updateAssignments(movedId, receiverId);
      }
    }).disableSelection();
  };


  // Select conference and load selection widget
  $('body').on('click', '#select-conference', function(){
    var confId = $('#id_event').val();
    $.ajax({
      url: '/crm/create_selection_widget/',
      type: 'POST',
      data: {
        'conf_id': confId,
      },
      success: function(data){
        $('#selection-widget').html(data);
        startDragDrop();
        startTypeAhead();
      }
    });
  });


  // Change staff member's method of list generation (filter vs new)
  $('body').on('click', '#btn-change-filter', function(){
    var filterMaster = $('input[name=filter_master_selects]:checked').val();
    console.log(filterMaster);
  });


  // Add general list selection and update relevant parts of page
  $('body').on('click', '#master #btn-add-new-select', function(){
    var confId = $('#id_event').val();
    var includeExclude = $('#master #id_include_exclude').val();
    var mainCategory = $('#master #id_main_category').val();
    var mainCategory2 = $('#master #id_main_category2').val();
    var geo = $('#master #id_geo').val();
    var industry = $('#master #id_industry').val();
    var company = $('#master #id_company').val();
    var dept = $('#master #id_dept').val();

    if (mainCategory || geo || industry || company || dept) {
      $.ajax({
        url: '/crm/add_master_list_select/',
        type: 'POST',
        data: {
          'conf_id': confId,
          'include_exclude': includeExclude,
          'main_category': mainCategory,
          'main_category2': mainCategory2,
          'geo': geo,
          'industry': industry,
          'company': company,
          'dept': dept,
        },
        success: function(data){
          $('#master').html(data);
          startTypeAhead();
        }
      });
    };
  });


  // Add personal list selection and update relevant parts of page
  $('body').on('click', '#btn-add-new-personal-select', function(){
    var confId = $('#id_event').val();
    var staffId = $('#active-staff-id').val();
    var includeExclude = $('#personal-select-details #id_include_exclude').val();
    var mainCategory = $('#personal-select-details #id_main_category').val();
    var mainCategory2 = $('#personal-select-details #id_main_category2').val();
    var geo = $('#personal-select-details #id_geo').val();
    var industry = $('#personal-select-details #id_industry').val();
    var company = $('#personal-select-details #id_company').val();
    var dept = $('#personal-select-details #id_dept').val();
    var division1 = $('#personal-select-details #id_division1').val();
    var division2 = $('#personal-select-details #id_division2').val();

    if (mainCategory || geo || industry || company || dept || division1 || division2) {
      $.ajax({
        url: '/crm/add_personal_list_select/',
        type: 'POST',
        data: {
          'conf_id': confId,
          'staff_id': staffId,
          'include_exclude': includeExclude,
          'main_category': mainCategory,
          'main_category2': mainCategory2,
          'geo': geo,
          'industry': industry,
          'company': company,
          'dept': dept,
          'division1': division1,
          'division2': division2,
        },
        success: function(data){
          $('#person-select-options').html(data);
          startTypeAhead();
        }
      });
    };
  });


  // Delete general list selection and update relevant parts of page
  $('body').on('click', '.btn-delete-master-select', function(){
    var confId = $('#id_event').val();
    var staffId = $('#active-staff-id').val();
    var selectId = $(this).attr('select-value');
    $.ajax({
      url: '/crm/delete_master_list_select/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'select_id': selectId,
        'staff_id': staffId,
      },
      success: function(data){
        $('#master').html(data);
        startTypeAhead();
      }
    });
  });


  // Delete personal list selection and update relevant parts of page
  $('body').on('click', '.btn-delete-personal-select', function(){
    var confId = $('#id_event').val();
    var selectId = $(this).attr('select-value');
    var staffId = $('#active-staff-id').val();
    $.ajax({
      url: '/crm/delete_personal_list_select/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'select_id': selectId,
        'staff_id': staffId,
      },
      success: function(data){
        $('#person-select-options').html(data);
        startTypeAhead();
      }
    });
  });


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
  var industrySuggestionClass = new Bloodhound({
      limit: 20,
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/crm/suggest_industry/',
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
  industrySuggestionClass.initialize();


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

    $('#id_industry').typeahead({
        hint: true,
        highlight: true,
        minLength: 2
    },
    {
        name: 'value',
        displayKey: 'value',
        source: industrySuggestionClass.ttAdapter(),
        templates: {
            empty: [
                '<div class="tt-suggestion">',
                'No Items Found',
                '</div>'
            ].join('\n')
        }
    });
  };


  // load appropriate staff GROUP content into personal select panel
  $('body').on('click', '.staff-select', function(){
    var sectionChosen = $(this).attr('id');
    var confId = $('#id_event').val();
    $.ajax({
      url: '/crm/load_staff_category_selects/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'section_chosen': sectionChosen,
      },
      success: function(data){
        $('#personal-selects').html(data);
        var numStaff = $('.btn-staff-select', data).length;
        if (numStaff == 1){
          var staffId = $('.btn-staff-select', data).attr('staff-id');
          console.log(staffId);
          // Need to call callStaffMemberTerritoryDetails here
        }
        startTypeAhead();
      }
    })
  });


  // function to do an ajax load of individual staff member select page
  function callStaffMemberTerritoryDetails(staffId){
    var confId = $('#id_event').val();
    $.ajax({
      url: '/crm/load_staff_member_selects/',
      type: 'POST',
      data: {
        'event_id': confId,
        'user_id': staffId,
      },
      success: function(data){
        $('#personal-select-details').html(data);
        startTypeAhead();
      }
    });
  };


  // load appropriate staff MEMBER content into personal select panel
  $('body').on('click', '.btn-staff-select', function(){
    $('.btn-staff-select').not(this).each(function(){
      $(this).removeClass('btn-primary');
      $(this).addClass('btn-default');
    });
    $(this).removeClass('btn-default');
    $(this).addClass('btn-primary');
    var staffId = $(this).attr('staff-id');
    callStaffMemberTerritoryDetails(staffId);
  })

});
