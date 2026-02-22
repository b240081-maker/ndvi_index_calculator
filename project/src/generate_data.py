
import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

def generate_sample_data(output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define image properties
    width, height = 500, 500
    transform = from_origin(75.0, 31.0, 0.0001, 0.0001)  # Approx 10m scale
    crs = {'init': 'epsg:4326'}

    # Generate synthetic Red Band (Band 4)
    # Background (Soil/Urban) = High Red
    # Vegetation = Low Red
    red_band = np.random.randint(500, 1500, (height, width)).astype(np.float32)
    # Add a "vegetation" circle feature
    y, x = np.ogrid[:height, :width]
    mask = (x - 250)**2 + (y - 250)**2 < 100**2
    red_band[mask] = np.random.randint(200, 600, mask.sum()) # Vegetation absorbs Red

    # Generate synthetic NIR Band (Band 8)
    # Background (Soil/Urban) = Moderate NIR
    # Vegetation = High NIR
    nir_band = np.random.randint(600, 1600, (height, width)).astype(np.float32)
    nir_band[mask] = np.random.randint(2000, 4000, mask.sum()) # Vegetation reflects NIR

    # Save Red Band
    red_path = os.path.join(output_dir, "sample_red.tif")
    with rasterio.open(
        red_path, 'w', driver='GTiff',
        height=height, width=width,
        count=1, dtype=rasterio.float32,
        crs=crs, transform=transform
    ) as dst:
        dst.write(red_band, 1)

    # Save NIR Band
    nir_path = os.path.join(output_dir, "sample_nir.tif")
    with rasterio.open(
        nir_path, 'w', driver='GTiff',
        height=height, width=width,
        count=1, dtype=rasterio.float32,
        crs=crs, transform=transform
    ) as dst:
        dst.write(nir_band, 1)

    print(f"Generated sample files in {output_dir}:")
    print(f"- {red_path}")
    print(f"- {nir_path}")

if __name__ == "__main__":
    generate_sample_data()
