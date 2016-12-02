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
    });
    var confCity = $('#conference-edit-panel #id_city').val();
    if (confCity) {
      filterVenueList(confCity);
    }
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
      });
      var cityVal = $('#conference-edit-panel #id_city').val();
      if (cityVal) {
        filterVenueList(cityVal);
      }
    }
  });


  // Ajax call to edit conference or add new
  $('body').on('click', '.btn-choose-venue', function(){
    var confId = $('#conference-select-dropdown #id_event').val();
    var editAction = $(this).attr('btn-action');
    var conferenceStatus = $('#edited-conference-status').val();
    if (conferenceStatus == 'new') {
      var newEventId = $('#edited-event-id').val();
      if (newEventId) {
        abandonUnsavedNewConference(newEventId);
      }
    }
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
          var $response = $(data);
          var cityVal = $response.find('#id_city').val();
          if (cityVal){
            filterVenueList(cityVal);
          }
        }
      });
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
    var conferenceStatus = $('#edited-conference-status').val();
    if (conferenceStatus == 'new') {
      var eventId = $('#edited-event-id').val();
      if (eventId) {  // have a temp conference in database - need to delete it
        abandonUnsavedNewConference(eventId);
      }
    }
    $('#conference-edit-panel').html('');
    unfilterVenueList();
  });


  // helper funtion to deal with unsaved changes to new conference on page
  function abandonUnsavedNewConference(tempEventId) {
    $.ajax({
      url: '/registration/delete_temp_conf/',
      type: 'POST',
      data: {
        event_id: tempEventId,
      },
    })
  }


  // Deal with unsaved changes to new conference on page leave
  $(window).on('beforeunload', function(){
    var editStatus = $('#edited-conference-status').val();
    var eventId = $('#edited-event-id').val();
    if (editStatus == 'new' && eventId != '') {
      abandonUnsavedNewConference(eventId);
    }
  });


  // Save conference changes
  $('body').on('click', '#save-conference-changes', function(){
    var editStatus = $('#edited-conference-status').val(); // new or edit
    var eventId = $('#edited-event-id').val();
    if (eventId == '') {
      eventId = 'new';
    };
    var number = $('#conference-edit-panel #id_number').val();
    var title = $('#conference-edit-panel #id_title').val();
    var dateBegins = $('#conference-edit-panel #id_date_begins').val();
    var city = $('#conference-edit-panel #id_city').val();
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
    $.ajax({
      url: '/registration/save_conference_changes/',
      type: 'POST',
      data: {
        event_id: eventId,
        number: number,
        title: title,
        city: city,
        date_begins: dateBegins,
        state_prov: stateProv,
        hotel: hotel,
        registrar: registrar,
        developer: developer,
        company_brand: companyBrand,
        gst_charged: gstCharged,
        hst_charged: hstCharged,
        qst_charged: qstCharged,
        gst_rate: gstRate,
        hst_rate: hstRate,
        qst_rate: qstRate,
        billing_currency: billingCurrency,
      },
      success: function(data) {
        $('#conference-edit-panel').html(data);
        unfilterVenueList();
      }
    });
  });


  // Change options
  $('body').on('click', '.option-manage-btn', function(){
    // manage cases of add, delete or Change
    var editStatus = $('#edited-conference-status').val(); // new or edit
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


  // helper function to filter Venue list to whatever the city value is
  function filterVenueList(filterText){
    $.ajax({
      url: '/registration/filter_venue/',
      method: 'GET',
      data: {
        city_partial: filterText,
      },
      success: function(data) {
        $('#venue-sidebar').html(data);
      }
    })
  };


  // helper function to reset venue list to all venues
  function unfilterVenueList(){
    $.ajax({
      url: '/registration/unfilter_venue/',
      method: 'GET',
      success: function(data) {
        $('#venue-sidebar').html(data);
      }
    })
  };


  // Filter venue list as city is selected
  $('body').on('keyup', '#conference-edit-panel #id_city', function () {
      var cityPartial = $('#conference-edit-panel #id_city').val();
      filterVenueList(cityPartial);
  });

});
