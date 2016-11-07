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

function toggleSearchText(button_id) {
  var thisButton = document.getElementById(button_id);
  if (thisButton.innerHTML.trim() == 'Show Details') {
    thisButton.innerHTML = "Hide Details";
  } else {
    thisButton.innerHTML = "Show Details";
  }
}
