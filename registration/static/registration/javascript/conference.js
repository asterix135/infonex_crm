$(document).ready(function() {

  function editVenue(venueID) {
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

  function saveVenueChanges(venueID) {
    $.ajax({
      url: '/registration/edit_venue/',
      type: 'POST',
      data: {
        id: venueID,
        name: $('#list-item-' + venueID + ' #id_name').val(),
        address: $('#list-item-' + venueID + ' #id_address').val(),
        city: $('#list-item-' + venueID + ' #id_city').val(),
        state_prov: $('#list-item-' + venueID + ' #id_state_prov').val(),
        postal_code: $('#list-item-' + venueID + ' #id_postal_code').val(),
        phone: $('#list-item-' + venueID + ' #id_phone').val(),
        hotel_url: $('#list-item-' + venueID + ' #id_hotel_url').val(),
      },
      success: function(data) {
        $('#list-item-' + venueID).html(data);
      }
    })
  };

  $('body').on('click', '.edit-button', function(event){
    event.preventDefault();
    var venueId = $(this).attr('venue-id');
    var editAction = $(this).attr('venue-action');
    if (editAction == 'edit') {
      editVenue(venueId);
    } else {
      saveVenueChanges(venueId)
    }
  });
});
