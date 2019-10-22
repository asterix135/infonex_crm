 export function updateTaxAndInvoice() {
  var preTaxPrice = $('#id_pre_tax_price').val();
  if ($.inArray($('#id_gst_rate').val(), [undefined, '']) == -1){
    var gstRate = parseFloat($('#id_gst_rate').val());
  } else {
    var gstRate = 0;
  };
  if ($.inArray($('#id_hst_rate').val(), [undefined, '']) == -1){
    var hstRate = parseFloat($('#id_hst_rate').val());
  } else {
    var hstRate = 0;
  };
  if ($.inArray($('#id_qst_rate').val(), [undefined, '']) == -1) {
    var qstRate = parseFloat($('#id_qst_rate').val());
  } else {
    var qstRate = 0;
  };
  var totalTax = (preTaxPrice * gstRate) + (preTaxPrice * hstRate) + (preTaxPrice * (1 + gstRate)) * qstRate
  var taxAsCurrency = '$' + totalTax.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
  var totalInvoice = +(preTaxPrice) + totalTax;
  var totalAsCurrency = '$' + totalInvoice.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
  $('#total-tax').text(taxAsCurrency);
  $('#total-invoice').text(totalAsCurrency);
};
