$(document).ready(function(){
    $("#sel-torah").change(function(){
    var tBook = $(this).children("option:selected").val();
      if(tBook == "Genesis") {
          $("#num-chap").attr({
         "max" : 50,
         "placeholder" : "1 - 50"
      });
      }
      else if(tBook == "Exodus") {
          $("#num-chap").attr({
         "max" : 40,
         "placeholder" : "1 - 40"
      });
      }
      else if(tBook == "Leviticus") {
          $("#num-chap").attr({
         "max" : 27,
         "placeholder" : "1 - 27"
      });
      }
      else if(tBook == "Numbers") {
          $("#num-chap").attr({
         "max" : 36,
         "placeholder" : "1 - 36"
      });
      }
      else if(tBook == "Deuteronomy") {
          $("#num-chap").attr({
         "max" : 34,
         "placeholder" : "1 - 34"
      });
      }
    });
});