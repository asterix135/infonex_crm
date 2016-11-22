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

  // wrapper to handle click and update venue info
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

  // Save new venue and update sidebar
  $('body').on('click', '#save-new-venue', function(){
    $.ajax({
      url: '/registration/add_venue/',
      type: 'POST',
      data: {
        name: $('#add-venue-toggle #id_name').val(),
        address: $('#add-venue-toggle #id_address').val(),
        city: $('#add-venue-toggle #id_city').val(),
        state_prov: $('#add-venue-toggle #id_state_prov').val(),
        postal_code: $('#add-venue-toggle #id_postal_code').val(),
        phone: $('#add-venue-toggle #id_phone').val(),
        hotel_url: $('#add-venue-toggle #id_hotel_url').val(),
      },
      success: function(data) {
        $('#venue-sidebar').html(data);
      }
    })
  });

  // Ajax call to delete venue

  // Toggle Warning and Delete current venue
  $('body').on('click', '.delete-venue-button', function(){
    var venueId = $(this).attr('venue-id');
    var warningHidden = !$('#delete-venue-warning' + venueId).is(":visible");
    if (warningHidden) {
      $('#delete-venue-warning' + venueId).show();
    } else {
      // ajax delete call
      $.ajax({
        url: '/registration/delete_venue/',
        type: 'POST',
        data: {
          venue_id: venueId,
        },
        success: function(data) {
          $('#venue-sidebar').html(data);
        }
      })
    }
  });

});
