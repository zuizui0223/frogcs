// JRC monthly water pixel-area extraction, independent of frog outcomes.
// Paste into Google Earth Engine Code Editor after uploading the *verified*
// jrc_month_requests.csv made by scripts/build_extraction_manifest.py.
// This is an extraction recipe, not evidence that Earth Engine was run.
// SOURCE: JRC/GSW1_4/MonthlyHistory; pixels 0=no data,1=land,2=water.

var ASSET = 'projects/YOUR_EE_PROJECT/assets/jrc_month_requests'; // CHANGE to your uploaded table
var YEAR = 2010; // CHANGE to requested calendar year; export separately per year
var requests = ee.FeatureCollection(ASSET);

// Fail closed on known missing/incorrect verification fields.
var props = ee.Feature(requests.first()).propertyNames().getInfo();
if (props.indexOf('verification_source_id') === -1 ||
    props.indexOf('coordinate_qc_status') === -1) {
  throw new Error('Missing independently verified station identity fields');
}
if (requests.filter(ee.Filter.neq('coordinate_qc_status', 'verified_external'))
    .size().getInfo() > 0) {
  throw new Error('Unverified station; do not geospatially overlay');
}
if (requests.filter(ee.Filter.inList('buffer_m', [250,1000]).not())
    .size().getInfo() > 0) {
  throw new Error('Unexpected buffer size');
}

var source = ee.ImageCollection('JRC/GSW1_4/MonthlyHistory');
var months = ee.List.sequence(1, 12);

function monthResult(m) {
  m = ee.Number(m).toInt();
  var selected = requests.filter(ee.Filter.eq('year', YEAR))
                         .filter(ee.Filter.eq('month', m));
  // Each year/month has exactly one JRC image for years in the catalog.
  var raw = ee.Image(source.filter(ee.Filter.eq('year', YEAR))
                           .filter(ee.Filter.eq('month', m)).first())
                 .select('water').unmask(0);
  var pixelArea = ee.Image.pixelArea();
  var area = ee.Image.cat([
    raw.eq(2).multiply(pixelArea).rename('water_area_m2'),
    raw.eq(1).multiply(pixelArea).rename('nonwater_area_m2'),
    raw.eq(0).multiply(pixelArea).rename('nodata_area_m2')
  ]);
  var buffered = selected.map(function(f) {
    f = ee.Feature(f);
    return f.setGeometry(
      ee.Geometry.Point([ee.Number(f.get('longitude')),
                         ee.Number(f.get('latitude'))])
        .buffer(ee.Number(f.get('buffer_m'))));
  });
  return area.reduceRegions({
    collection: buffered, reducer: ee.Reducer.sum(),
    crs: 'EPSG:5070', scale: 30, tileScale: 4
  }).map(function(f) {
    return ee.Feature(f).set({
      source_version: 'JRC_GSW1_4',
      source_image_id: ee.String('JRC/GSW1_4/MonthlyHistory/')
        .cat(ee.Number(YEAR).format('%d')).cat('_').cat(m.format('%02d'))
    });
  });
}

var results = ee.FeatureCollection(months.map(monthResult)).flatten();
print('Rows in requested calendar year', requests.filter(ee.Filter.eq('year',YEAR)).size());
print('JRC extracted image-month geometries', results.size());
// For small pilots inspect result features and valid/no-data pixel area before trusting.
print('Preview',results.limit(5));
Export.table.toDrive({
  collection: results,
  description: 'frog_jrc_monthly_area_' + YEAR,
  fileNamePrefix: 'frog_jrc_monthly_area_' + YEAR,
  fileFormat: 'CSV',
  selectors: ['route_id','site_id','buffer_m','year','month',
    'water_area_m2','nonwater_area_m2','nodata_area_m2',
    'source_image_id','source_version']
});
