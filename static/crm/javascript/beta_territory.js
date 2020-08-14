// Auto-set beta categories
$(document).ready(function() {
  $('body').on('change', '#id_division1', function(){
    let newDivision = $(this).val();
    // if (newDivision='')
    // console.log(newDivision);
  });

  $('body').on('change', '#id_division2', function(){
    let newDivision2 = $(this).val();
    // console.log(newDivision2);
  });


});
