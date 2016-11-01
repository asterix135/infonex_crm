$(document).ready(function() {
  // alert('hello');

  $("#checkAllBoxes").click(function(){
    var checked_status = this.checked;
    $("input[name='reflag'").each(function(){
      this.checked = checked_status;
    });
  });

});
