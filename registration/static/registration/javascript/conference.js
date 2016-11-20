$(document).ready(function() {

  function editVenue(venueID) {
    alert(venueID);
    $.ajax({
      url: '/registration/edit_venue/',
      type: 'GET',
      data: {
        id: venueID,
      },
      success: function(data) {
        $('#list-item-' + venueID).html(data);
      }
    })
  };

  $('body').on('click', '.edit-button', function(event){
    event.preventDefault();
    var venueId = $(this).attr('venue-id');
    editVenue(venueId);
  });

});
