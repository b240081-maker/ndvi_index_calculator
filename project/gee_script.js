
/**
 * AI-Based Vegetation Health Assessment using NDVI
 * Use this script in the Google Earth Engine Code Editor: https://code.earthexplorer.google.com/
 */

// 1. Define Area of Interest (AOI)
// Replace with your own geometry or upload a shapefile
var aoi = ee.Geometry.Rectangle([75.7, 30.2, 76.5, 31.0]); // Example: Punjab region
Map.centerObject(aoi, 9);

// 2. Load Sentinel-2 Imagery
var s2 = ee.ImageCollection("COPERNICUS/S2_SR")
  .filterBounds(aoi)
  .filterDate('2023-10-01', '2023-11-30')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
  // Calculate Median to remove clouds/shadows
  .median()
  .clip(aoi);

// 3. Compute NDVI
var ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI');

// 4. AI/ML - Unsupervised Clustering (K-Means)
// We need to sample the image to train the clusterer
var training = ndvi.sample({
  region: aoi,
  scale: 10,
  numPixels: 5000
});

// Train the clusterer (e.g., 4 clusters)
var clusterer = ee.Clusterer.wekaKMeans(4).train(training);

// Cluster the input
var result = ndvi.cluster(clusterer);

// 5. Visualization

// NDVI Palette
var ndviParams = {min: -0.2, max: 0.8, palette: ['blue', 'white', 'green']};
Map.addLayer(ndvi, ndviParams, 'NDVI');

// Classification Palette (Random colors for classes)
var clusterParams = {min: 0, max: 3, palette: ['red', 'yellow', 'lightgreen', 'darkgreen']};
Map.addLayer(result, clusterParams, 'AI Classified Vegetation');

// 6. Calculate Area
// (Optional: Print area of each class to Console)
var areaImage = ee.Image.pixelArea().addBands(result);
var areas = areaImage.reduceRegion({
  reducer: ee.Reducer.sum().group({
    groupField: 1,
    groupName: 'class',
  }),
  geometry: aoi,
  scale: 10,
  maxPixels: 1e9
});

print('Class Areas (sq meters):', areas);

// 7. Export (Optional)
Export.image.toDrive({
  image: result,
  description: 'Classified_Vegetation_Map',
  scale: 10,
  region: aoi
});
