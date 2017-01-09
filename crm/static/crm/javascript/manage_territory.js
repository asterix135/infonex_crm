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
        var receiver = $(this).attr('id');
        updateAssignments(movedId, receiver);
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

});
