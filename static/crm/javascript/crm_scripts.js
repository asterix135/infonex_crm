function clearTerritorySearchBoxes() {
  var nameBox = document.getElementById('id_name');
  var titleBox = document.getElementById('id_title');
  var companyBox = document.getElementById('id_company');
  var flagBox = document.getElementById('id_flag');
  var stateBox = document.getElementById('id_state_province');
  var pastCustomerBox = document.getElementById('id_past_customer');
  nameBox.value='';
  titleBox.value='';
  companyBox.value='';
  flagBox.value='';
  stateBox.value='';
  pastCustomerBox.checked=false;
}
