// Toggles checkbox status in territory view for all individuals
function checkAll() {
  var masterBoxStatus = document.getElementById('checkAllBoxes').checked
  checkboxes = document.getElementsByName('reflag');
  for(var i=0; i<checkboxes.length; i++) {
    checkboxes[i].checked = masterBoxStatus;
  }
}

// Toggles flag set values for checked Records
function toggleFlags() {
  var e = document.getElementById('masterFlag');
  var masterFlagValue = e.options[e.selectedIndex].value - 1;
  flagDropdowns = document.getElementsByName('personFlag');
  checkboxes = document.getElementsByName('reflag');
  for(var i=0; i<checkboxes.length; i++) {
    if(checkboxes[i].checked) {
      flagDropdowns[i].selectedIndex=masterFlagValue;
    }
  }
}
