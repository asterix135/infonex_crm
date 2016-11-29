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


  // Ajax call to edit conference or add new
  $('body').on('click', '.btn-choose-venue', function(){
    var confId = $('#conference-select-dropdown #id_event').val();
    var editAction = $(this).attr('btn-action');
    if (editAction == 'edit') {
      if (confId == '') {
        editAction = 'blank';
      };
      $.ajax({
        url: '/registration/select_conference/',
        type: 'POST',
        data: {
          conf_id: confId,
          edit_action: editAction,
        },
        success: function(data) {
          $('#conference-edit-panel').html(data);
        }
      })
    } else if (editAction == 'new') {
      $.ajax({
        url: '/registration/select_conference/',
        type: 'GET',
        success: function(data) {
          $('#conference-edit-panel').html(data);
        }
      })
    }
  });


  // Abandon conference changes
  $('body').on('click', '#abandon-conference-changes', function(){
    var conferenceStatus = $('#edited-event-id').val();
    if (conferenceStatus == 'new') {
      alert('need to implement logic to remove added options etc');
    } else {
      $('#conference-edit-panel').html('');
    }
  });


  // Save conference changes
  $('body').on('click', '#save-conference-changes', function(){
    var eventId = $('#edited-event-id').val();
    var number = $('#conference-edit-panel #id_number').val();
    var title = $('#conference-edit-panel #id_title').val();
    var dateBegins = $('#conference-edit-panel #id_date_begins').val();
    var stateProv = $('#conference-edit-panel #id_state_prov').val();
    var hotel = $('#conference-edit-panel #id_hotel').val();
    var registrar = $('#conference-edit-panel #id_registrar').val();
    var developer = $('#conference-edit-panel #id_developer').val();
    var companyBrand = $('#conference-edit-panel #id_company_brand').val();
    var gstCharged = $('#conference-edit-panel #id_gst_charged').val();
    var hstCharged = $('#conference-edit-panel #id_hst_charged').val();
    var qstCharged = $('#conference-edit-panel #id_qst_charged').val();
    var gstRate = $('#conference-edit-panel #id_gst_rate').val();
    var hstRate = $('#conference-edit-panel #id_hst_rate').val();
    var qstRate = $('#conference-edit-panel #id_qst_rate').val();
    var billingCurrency = $('#conference-edit-panel #id_billing_currency').val();
    // Need to capture options info here

  });


  // Change options
  $('body').on('click', '.option-manage-btn', function(){
    // manage cases of add, delete or Change
    var editStatus = $('#edited-conference-status').val(); // new or existing conf
    var editAction = $(this).attr('name'); // add or delete or rehide
    var eventId = $('#edited-event-id').val();
    var primary = $('#new-option-row #id_primary').prop('checked');
    var name = $('#new-option-row #id_name').val();
    var startdate = $('#new-option-row #id_startdate').val();
    var enddate = $('#new-option-row #id_enddate').val();
    if (editAction == 'add') {
      $.ajax({
        url: '/registration/add_event_option/',
        type: 'POST',
        data: {
          name: name,
          primary: primary,
          startdate: startdate,
          enddate: enddate,
          event_id: eventId,
        },
        success: function(data) {
          $('#event-options-panel').html(data);
        }
      })
    } else if (editAction == 'delete'){  // delete
      var optionId = $(this).attr('option-val');
      var warningHidden = !$('#delete-option-warning' + optionId).is(":visible");
      if (warningHidden) {
        $('#delete-option-warning' + optionId).show();
      } else {
        $.ajax({
          url: '/registration/delete_event_option/',
          type: 'POST',
          data: {
            option_id: optionId,
            event_id: eventId,
          },
          success: function(data) {
            $('#event-options-panel').html(data);
          }
        })
      }
    } else {  //rehide
      var optionId = $(this).attr('option-val');
      $('#delete-option-warning' + optionId).hide();
    }
  });

});
