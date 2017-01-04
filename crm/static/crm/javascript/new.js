// Javascript for new.html page
$(document).ready(function() {

  // Add * to indicate required fields
  $('input,textarea,select').filter('[required]').parent().parent().find("label").append('<span class="required-label"> *</span>');

  // Need to add code for autocomplete
  // User Bootstrap typeahead: need to understand this better
  // See http://twitter.github.io/typeahead.js/examples/
  // https://twitter.github.io/typeahead.js/
  http://stackoverflow.com/questions/28015290/twitter-typeahead-js-autocomplete-remote-not-working
  var companySuggestions = new Bloodhound(

  );

});
