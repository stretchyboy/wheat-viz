var basicCSV = require("basic-csv");
require('core-js');

var fs = require("fs"),
    path = require("path");

/*
[ 'Domain Code',
  'Domain',
  'AreaCode',
  'AreaName',
  'ElementCode',
  'ElementName',
  'ItemCode',
  'ItemName',
  'Year',
  'Value',
  'Flag',
  'FlagD' ]
*/
  
var aCountries = [];

basicCSV.readCSV("data/wheat-FAOSTAT.csv", {
  dropHeader: true
}, function (error, rows) {
  
  rows.forEach(function(oRow){
     //console.log("oLink =", oLink);
     var iCountry = aCountries.findIndex(function(oCountry){
       return oRow[3] === oCountry.country;
     });
     
     if (iCountry === -1) {
       iCountry = aCountries.length;
       aCountries.push({
           country:oRow[3],
           years:[]
       });
     } 
     
     var iYear = aCountries[iCountry].years.findIndex(function(oYear){
       return oRow[8] === oYear.year;
     });
     
     if (iYear === -1) {
       iYear = aCountries[iCountry].years.length;
       aCountries[iCountry].years.push({
           year:oRow[8]
       });
     }
     var iVal = parseInt(oRow[9]);
     var sElementName = oRow[5];
     if (typeof sElementName !== "undefined" && sElementName.length > 0) {
       var sKey = sElementName.toLowerCase().replace(" ","_");
       aCountries[iCountry].years[iYear][sKey] = iVal;
     }
  });
  //console.dir(aCountries[0]);
  
  aCountries.forEach(function(oCountry){
    if(typeof oCountry.years !== "undefined") {
      var aYears = oCountry.years.map(function(oYear){
        oYear.import_price = 0;
        oYear.import_value = 1000 * oYear.import_value;
        if(oYear.import_quantity) {
          oYear.import_price = Math.round(oYear.import_value / oYear.import_quantity);
        }
        oYear.export_price = 0;
        oYear.export_value = 1000 * oYear.export_value;
        if(oYear.export_quantity) {
          oYear.export_price = Math.round(oYear.export_value / oYear.export_quantity);
        } 
        return oYear;
      });
    
      if(typeof oCountry.country !== "undefined") {
        var sFileName =  oCountry.country.toLowerCase().replace(/[^a-z]/g,"_")+".json"
        fs.writeFileSync( "data/"+sFileName, JSON.stringify(aYears, null, 4));
      }
    }
  });
  
});

