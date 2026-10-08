// Response-blind JRC MonthlyHistory per-image water and no-data extraction.
// Requires jrc_month_requests.csv from a verified-physical-site manifest.
// The script has NOT been executed; it requires authenticated Earth Engine.
var ASSET = 'projects/YOUR_EE_PROJECT/assets/jrc_month_requests';
var YEAR = 2010; // Run one export per requested year.
var requests=ee.FeatureCollection(ASSET);
var fields=ee.Feature(requests.first()).propertyNames().getInfo();
if (fields.indexOf('verification_source_id')===-1 ||
    fields.indexOf('coordinate_qc_status')===-1) {
  throw Error('Independent site verification evidence missing');
}
if (requests.filter(ee.Filter.neq('coordinate_qc_status','verified_external'))
    .size().getInfo()>0) throw Error('Unverified station(s)');
var invalid=ee.Filter.inList('buffer_m',[250,1000]).not();
if (requests.filter(invalid).size().getInfo()>0) throw Error('Bad buffer sizes');

var monthImages=ee.ImageCollection('JRC/GSW1_4/MonthlyHistory');
function processMonth(month) {
  month=ee.Number(month).toInt();
  var subset=requests.filter(ee.Filter.eq('year',YEAR))
                     .filter(ee.Filter.eq('month',month));
  var source=ee.Image(monthImages.filter(ee.Filter.eq('year',YEAR))
                     .filter(ee.Filter.eq('month',month)).first())
                     .select('water').unmask(0);
  var pixelArea=ee.Image.pixelArea();
  var a=ee.Image.cat([
    source.eq(2).multiply(pixelArea).rename('water_area_m2'),
    source.eq(1).multiply(pixelArea).rename('nonwater_area_m2'),
    source.eq(0).multiply(pixelArea).rename('nodata_area_m2')]);
  var circles=subset.map(function(f){
    return ee.Feature(f).setGeometry(
      ee.Geometry.Point([ee.Number(f.get('longitude')),
                         ee.Number(f.get('latitude'))])
                         .buffer(ee.Number(f.get('buffer_m'))));
  });
  return a.reduceRegions({
    collection:circles,reducer:ee.Reducer.sum(),
    crs:'EPSG:5070',scale:30,tileScale:4
  }).map(function(f){
    return ee.Feature(f).set({
      source_version:'JRC_GSW1_4',
      source_image_id:ee.String('JRC/GSW1_4/MonthlyHistory/')
        .cat(ee.Number(YEAR).format('%d')).cat('_').cat(month.format('%02d'))
    });
  });
}
var output=ee.FeatureCollection(ee.List.sequence(1,12).map(processMonth)).flatten();
print('Input requests this year',requests.filter(ee.Filter.eq('year',YEAR)).size());
print('Output site-month-buffer rows',output.size());
print('Preview',output.limit(5));
Export.table.toDrive({
  collection:output,description:'frog_jrc_monthly_area_'+YEAR,
  fileNamePrefix:'frog_jrc_monthly_area_'+YEAR,fileFormat:'CSV',
  selectors:['route_id','site_id','buffer_m','year','month',
     'water_area_m2','nonwater_area_m2','nodata_area_m2',
     'source_image_id','source_version']
});
