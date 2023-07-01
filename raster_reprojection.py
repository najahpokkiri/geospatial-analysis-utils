import rasterio

# Specify the paths of the first and second raster files
#desired crs
input_file_1 = "./alos_periyar_clipped_4326_corrected_to_egm_08_25.tif"
#crs to be converted
input_file_2 = "/LE8-9_2020.tif"
output_file = "./LE8-9_2020_converted.tif"

# Open the first raster file to get the CRS, transform, and shape
with rasterio.open(input_file_1) as src1:
    src_crs = src1.crs
    transform = src1.transform
    shape = src1.shape

# Open the second raster file
with rasterio.open(input_file_2) as src2:
    # Read the data
    data = src2.read()

    # Create the profile for the output raster, matching the CRS, transform, and shape of the first raster
    profile = src2.profile.copy()
    profile.update({
        'crs': src_crs,
        'transform': transform,
        'height': shape[0],
        'width': shape[1]
    })

    # Write the data to the output raster file
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(data)
