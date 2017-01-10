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


  // Called when moving somebody back to general sales-staff
  // Activates modal warning that selection details about to be destroyed
  function checkForUserAssignment(userId, receiverId, movedItem, sender, receiver){
    var confId = $('#id_event').val();
    $.ajax({
      url: '/crm/check_for_user_assignment/',
      type: 'POST',
      data: {
        'conf_id': confId,
        'user_id': userId,
      },
      success: function(data, movedItem){
        var isAssigned = $('#assignment-exists', data).val();
        if (isAssigned=='False'){
          $('#modalWarnDeleteSelections').modal('show');
        } else {
          updateAssignments(userId, receiverId);
        }
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
        if (receiverId == 'unassigned-staff') {
          checkForUserAssignment(movedId, receiverId);
        } else {
          updateAssignments(movedId, receiverId);
        };
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
