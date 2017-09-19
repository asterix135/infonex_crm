$(document).ready(function() {

  (function worker() {
    $.ajax({
      url: '/registration/update_queue_count/',
      success: function(data) {
        if (data.count == 0) {
          $('#pending-registrations').text('');
        } else {
          $('#pending-registrations').text(data.count);
        };
      },
      complete: function() {
        // Schedule the next request when the current one's complete
        setTimeout(worker, 60000);
      }
    });
  })();

});
