import ee 
from ee_plugin import Map



delhi = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq('ADM2_NAME','Delhi')).geometry()


Map.addLayer(delhi)



s2 = ee.ImageCollection("COPERNICUS/S2_SR")



Map.centerObject(delhi)
rgbVis = {
  'min': 0.0,
  'max': 3000,
  'bands': ['B4', 'B3', 'B2'],
}

filtered = s2 \
  .filter(ee.Filter.date('2019-03-01', '2019-05-21')) \
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
  .filter(ee.Filter.bounds(delhi)) \
  .select('B.*')


before = filtered.median().clip(delhi)
# Display the input composite.
Map.addLayer(before, rgbVis, 'before')



def addIndices(image):
  ndvi = image.normalizedDifference(['B8', 'B4']).rename(['ndvi'])
  ndbi = image.normalizedDifference(['B11', 'B8']).rename(['ndbi'])
  mndwi = image.normalizedDifference(['B3', 'B11']).rename(['mndwi'])
  ndwi = image.normalizedDifference(['B3', 'B8']).rename('ndwi')
  return image.addBands(ndvi).addBands(ndbi).addBands(mndwi).addBands(ndwi)

before = addIndices(before)

data = urban.merge(non_urban)

# Add a random column and split the GCPs into training and validation set
data = data.randomColumn()

# This being a simpler classification, we take 60% points
# for validation. Normal recommended ratio is
# 70% training, 30% validation
training = data.filter(ee.Filter.lt('random', 0.7))
validation = data.filter(ee.Filter.gte('random', 0.7))

# Overlay the point on the image to get training data.
training = before.sampleRegions({
  'collection': training,
  'properties': ['landcover'],
   'tileScale': 16,
  'scale': 10
})

# Train a classifier.
classifier = ee.Classifier.smileRandomForest({
       'numberOfTrees': 50,
     } ).train({
  'features': training,
  'classProperty': 'landcover',
  'inputProperties': before.bandNames()
})

# # Classify the image.
classified = before.classify(classifier)
Map.addLayer(classified,
  {'min': 0, 'max': 3, 'palette': ['gray', 'brown', 'blue', 'green']}, 'before_classified')



print(classified)

classfied = classified.clip(delhi)


# # # # exporting images to asset


# Export.image.toAsset({
#   image: classified,
#   description: 'delhi19_classfiedtest',
#   assetId: 'ee-najah',
#   region: delhi,
#   scale: 100,
#   maxPixels: 1e10
# })





# Export.image.toDrive({
#   image: classified,
#   description: 'delhi_s2_30',
#   scale: 30,
#   region: delhi,
#   maxPixels: 1e10
# })



#**************************************************************************
# Accuracy Assessment
#**************************************************************************

# Use classification map to assess accuracy using the validation fraction
# of the overall training set created above.

test = classified.sampleRegions({
  'collection': validation,
  'properties': ['landcover'],
  'tileScale': 16,
  'scale': 10,
})

testConfusionMatrix = test.errorMatrix('landcover', 'classification')
# Printing of confusion matrix may time out. Alternatively, you can export it as CSV
print('Confusion Matrix', testConfusionMatrix)
print('Test Accuracy', testConfusionMatrix.accuracy())



Export.image.toDrive({
  'image': classified,
  'description': 'delhi_s2_100_clipped',
  'scale': 10,
  'region': delhi,
  'maxPixels': 1e10
})

Map