
import os
import numpy as np
from src import processing, analysis, utils

def test_workflow():
    try:
        data_dir = "data"
        red_path = os.path.join(data_dir, "sample_red.tif")
        nir_path = os.path.join(data_dir, "sample_nir.tif")
        
        if not os.path.exists(red_path) or not os.path.exists(nir_path):
            print("Sample data not found. Run generate_data.py first.")
            return

        print("Loading bands...")
        red_band, meta_red = processing.load_band(red_path)
        nir_band, meta_nir = processing.load_band(nir_path)
        
        print(f"Red band shape: {red_band.shape}")
        print(f"NIR band shape: {nir_band.shape}")

        print("Calculating NDVI...")
        ndvi_image = processing.calculate_ndvi(red_band, nir_band)
        print(f"NDVI range: {np.nanmin(ndvi_image)} to {np.nanmax(ndvi_image)}")

        print("Performing K-Means Clustering...")
        classified_map, centers = analysis.perform_kmeans_clustering(ndvi_image, n_clusters=4)
        print("Clustering successful.")

        print("Calculating Statistics...")
        pixel_size = meta_red['transform'][0]
        stats = analysis.calculate_area_statistics(classified_map, pixel_size, pixel_size)
        print(f"Statistics: {stats}")

        print("SUCCESS: Full workflow completed.")
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow()
