import numpy as np
import rasterio

def load_band(file_path):
    with rasterio.open(file_path) as src:
        band = src.read(1).astype(float)
        meta = src.meta
    return band, meta

def calculate_ndvi(red_band, nir_band):
    np.seterr(divide='ignore', invalid='ignore')
    numerator = nir_band - red_band
    denominator = nir_band + red_band
    ndvi = numerator / denominator
    ndvi = np.nan_to_num(ndvi, nan=np.nan, posinf=1.0, neginf=-1.0)
    ndvi = np.clip(ndvi, -1.0, 1.0)
    return ndvi

def save_raster(data, meta, output_path):
    meta.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(data.astype(rasterio.float32), 1)
