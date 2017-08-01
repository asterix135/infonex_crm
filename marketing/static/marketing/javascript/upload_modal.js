$(function() {

  ///////////////////
  // Following is to process upload modal
  ///////////////////

  // Attach the `fileselect` event to all file inputs on the page
  $(document).on('change', ':file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
  });

  // Watch for our custom `fileselect`
  $(document).ready( function() {
      $(':file').on('fileselect', function(event, numFiles, label) {

          var input = $(this).parents('.input-group').find(':text'),
              log = numFiles > 1 ? numFiles + ' files selected' : label;

          if( input.length ) {
              input.val(log);
          } else {
              if( log ) alert(log);
          }

      });

      // Only activate submit button if file has correct extension
      $('INPUT[type="file"]').change(function () {
        var ext = this.value.match(/\.(.+)$/)[1];
        switch (ext) {
          case 'csv':
          case 'xlsx':
            $('#submit-button').attr('disabled', false);
            break;
          default:
            alert('This is not an allowed file type.');
            this.value = '';
        }
      });
  });

});
