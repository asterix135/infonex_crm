// Javascript for manage_territory.html page
$(document).ready(function() {

  //Drag and drop employees into category boxes
  // See: http://www.w3schools.com/html/html5_draganddrop.asp (not so much)
  // See: https://johnny.github.io/jquery-sortable/

  // $("body .staff-entry").draggable();
  // $(".sort-box").droppable();

  $(".connectedSortable").sortable({
    connectWith: ".connectedSortable"
  }).disableSelection();


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
        $('.connectedSortable').sortable({
          connectWith: '.connectedSortable',
          update: function(){console.log('updated');}
        }).disableSelection();
      }
    });
  });

});
