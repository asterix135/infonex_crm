// // Toggles checkbox status in territory view for all individuals
// function checkAll() {
//   var masterBoxStatus = document.getElementById('checkAllBoxes').checked
//   checkboxes = document.getElementsByName('reflag');
//   for(var i=0; i<checkboxes.length; i++) {
//     checkboxes[i].checked = masterBoxStatus;
//   }
// }
//
// // Toggles flag set values for checked Records
// function toggleFlags() {
//   var e = document.getElementById('masterFlag');
//   var masterFlagValue = e.options[e.selectedIndex].value - 1;
//   flagDropdowns = document.getElementsByName('personFlag');
//   checkboxes = document.getElementsByName('reflag');
//   for(var i=0; i<checkboxes.length; i++) {
//     if(checkboxes[i].checked) {
//       flagDropdowns[i].selectedIndex=masterFlagValue;
//     }
//   }
// }

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
