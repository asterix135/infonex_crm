import { updateTaxAndInvoice } from './updateTaxAndInvoice.js';

$(document).ready(function(){
  $('body').on('keyup change', '.cost-field', function(){
    updateTaxAndInvoice();
  });
});
