// Javascript for manage_territory.html page
$(document).ready(function() {

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
      }
    });
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
        }
      });
    };
  });


  // Delete general list selection and update relevant parts of page
  $('body').on('click', '#master #btn-delete-select', function(){
    var confId = $('#id_event').val();
    var selectId = $(this).attr('select-value');
    $.ajax({
      url: '/crm/delete_master_list_select/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'select_id': selectId,
      },
      success: function(data){
        $('#master').html(data);
      }
    });
  });

});
