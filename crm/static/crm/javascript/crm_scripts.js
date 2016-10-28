// Toggles checkbox status in territory view for all individuals
function checkAll() {
  var masterBoxStatus = document.getElementById('checkAllBoxes').checked
  checkboxes = document.getElementsByName('reflag');
  for(var i=0; i<checkboxes.length; i++) {
    checkboxes[i].checked = masterBoxStatus;
  }
}
