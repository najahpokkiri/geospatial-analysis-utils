library(sf)
library(sp)
library(rgdal)
library(raster)

# Load your raster

raster <- raster("/Users/najah/work/internships/meghna/LT05_L1TP_145044_20090425_20161026_01_T1/LT05_L1TP_145044_20090425_20161026_01_T1_B4.TIF")
plot(raster)

# Determine raster's edge to make sure points are within raster's study extent
edge_line <- rasterToContour(raster)

# st_union to dissolve geometries
pol <- as(st_union(st_polygonize(st_as_sf(edge_line))), 'Spatial')

# Perform the random point sampling, generate 100 points, and save .csv
random700 <- spsample(pol[1,], 700, type = 'random', iter = 1000)

xy700ran <- data.frame(random700)
names(xy700ran) <- c('x','y')
random700pts <- cbind(extract(raster, xy700ran, df = T),xy700ran)

write.csv(random700pts, file = '/Users/najah/work/internships/meghna/LT05_L1TP_145044_20090425_20161026_01_T1/145044_20090425_random_points_.csv')
