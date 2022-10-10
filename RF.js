// Input required----
 points = training data
 geometry = shapefile of AOI
print(points);
// Make a cloud-free Landsat 8 surface reflectance composite.
var image = ee.ImageCollection("LANDSAT/LT05/C01/T1_TOA")
  .filterBounds(geometry)
  .filterDate('2010-04-15', '2010-04-30')
  .filter(ee.Filter.eq('WRS_PATH', 145))
  //.filter(ee.Filter.eq('WRS_ROW', 45))
  .median();
var bai = image.expression(
    '1/((0.02-red)**2+(0.05-nir)**2)', {
      'nir': image.select('B4'),
      'red': image.select('B3'),
  }).rename("bai");
  
var ndwi = image.normalizedDifference(['B2', 'B5']);
var x = (image.select('B5').add(image.select('B3'))).subtract(image.select('B4').add(image.select('B1')));
var y = (image.select('B5').add(image.select('B3'))).add(image.select('B4').add(image.select('B1')));
var bare = x.divide(y);  
var image = image.addBands(bai).addBands(ndwi).addBands(bare);

var ndvi = image.normalizedDifference(['B4','B3']).rename("ndvi");
var image = image.addBands(ndvi);
// Use these bands for prediction.
var bands = ['B1','B2', 'B3', 'B4', 'B5','B7','bai','ndvi'];

var points = ee.FeatureCollection(points);
var train = image.select(bands).sampleRegions({
  collection: points,
  properties: ['Actual'],
  scale: 30
});

var splitData = function(data){
  var dict = {};
  var randomTpixels = data.randomColumn(); 
  var training = randomTpixels.filter(ee.Filter.lt('random', 0.7));
  var valiData = randomTpixels.filter(ee.Filter.gte('random', 0.7));
  
  dict.training = training;
  dict.valid = valiData;
  
  return dict;
};

var Adata = splitData(train);
// Train a CART classifier with default parameters.
var trained = ee.Classifier.smileRandomForest(100).train(Adata.training, 'Actual', bands);

// Classify the image with the same bands used for training.
var classified = image.select(bands).classify(trained);
print(classified)
// Creates error matrix
var createMatrix = function(data){
  var trainAccuracy = data.errorMatrix("Actual", "classification");
  print('Resubstitution error matrix: ', trainAccuracy);
  print('Training overall accuracy: ', trainAccuracy.accuracy());
};

var validation = Adata.valid.classify(trained); // Classifies the validation data

createMatrix(validation);

// Display the classification result and the input image.
Map.addLayer(image,
             {bands: ['B5', 'B4', 'B3'], min: 0, max: 0.4, gamma: 1.2},'image');

             
Map.addLayer(points, {color: 'yellow'}, 'training polygons');
Map.addLayer(classified,
             {min: 0, max: 1, palette: ['green', 'yellow']},
             'Fire');
             
Export.image.toDrive({
  image: classified,
  description: 'RF_kanha',
  region : geometry,
  scale: 30,
  maxPixels: 1e9
});                                     