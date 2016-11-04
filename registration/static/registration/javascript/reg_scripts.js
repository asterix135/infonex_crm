function clearSearchBoxesNewReg() {
  var eventBox = document.getElementById('id_event');
  var firstNameBox = document.getElementById('id_first_name');
  var lastNameBox = document.getElementById('id_last_name');
  var companyBox = document.getElementById('id_company');
  var postalCodeBox = document.getElementById('id_postal_code');
  eventBox.value='';
  firstNameBox.value='';
  lastNameBox.value='';
  companyBox.value='';
  postalCodeBox.value='';
}

function showCrmProspectDetails(button_id) {
  var thisButton = document.getElementById(button_id);
  if (thisButton.firstChild.data == 'Show Details') {
    thisButton.firstChild.data = "Hide Details";
  } else {
    thisButton.firstChild.data = "Show Details";
  }
  var detailsSection = document.getElementById("details".concat(button_id));
  if (detailsSection.style.display == 'none') {
    detailsSection.style.display = 'inline';
  } else {
    detailsSection.style.display = 'none';
  }
}
