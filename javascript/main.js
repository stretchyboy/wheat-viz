jQuery(document).ready(function ($) {

    var iStep = 0;
    var iTimer = 0;
    
    var aAngles = [];
    
    function getFrameClassName(iS) {
      return  "price-"+(iS % 6);
    }
    
    var eVideo = $("#main");
    
    //var sCountry = "United Kingdom"
    
    var sCountry = "World"
    var sCountry = $("#country_select").val();
    console.log("sCountry =", sCountry);
    
    $.ajax({
        url:"data/"+(sCountry.toLowerCase().replace(" ","_"))+".json",
        dataType:"json",
        cache:false,
        success: function(data){
          $("#country").text(sCountry);
          //console.log("data =", data);
          var iMax = data.reduce(function(previousValue, currentValue, index, array) {
            return Math.max(previousValue, currentValue.import_price);
          }, 0);
          
          console.log("iMax =", iMax);
          
          aAngles = data.map(function(oYear){
             oYear.angle = Math.round(270*(oYear.import_price / iMax));
             return oYear;
          });
          
          var iAngles = aAngles.length;
          //console.log("aAngles =", aAngles);
          
          eVideo.on("play",function(){
            iTimer = setInterval(function(){
                var oYear = aAngles[iStep % iAngles];
              eVideo.css("filter","hue-rotate("+oYear.angle+"deg)");
              
              $("#price").text(oYear.import_price);
              $("#year").text(oYear.year);
              
              iStep ++;
              
            }, Math.round(54 *1000/iAngles));
            
          }).on("pause",function(){
            clearInterval(iTimer);
          });
      },
      error: console.log
    });
});

