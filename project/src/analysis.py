import numpy as np
from sklearn.cluster import KMeans

def perform_kmeans_clustering(ndvi_data, n_clusters=4):
    valid_mask = ~np.isnan(ndvi_data)
    valid_data = ndvi_data[valid_mask].reshape(-1, 1)
    
    if valid_data.size == 0:
        return np.full(ndvi_data.shape, -1), []

    unique_vals = np.unique(valid_data)
    actual_clusters = min(n_clusters, len(unique_vals))

    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    kmeans.fit(valid_data)
    
    sorted_indices = np.argsort(kmeans.cluster_centers_.flatten())
    mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted_indices)}
    
    labels = kmeans.labels_
    remapped_labels = np.array([mapping[l] for l in labels])
    
    classified_map = np.full(ndvi_data.shape, -1, dtype=int)
    classified_map[valid_mask] = remapped_labels
    
    return classified_map, kmeans.cluster_centers_[sorted_indices]

def calculate_area_statistics(classified_map, pixel_size_x, pixel_size_y):
    unique, counts = np.unique(classified_map, return_counts=True)
    is_geographic = abs(pixel_size_x) < 0.1 
    
    if is_geographic:
        pixel_area_km2 = abs(pixel_size_x * 111) * abs(pixel_size_y * 111)
    else:
        pixel_area_m2 = abs(pixel_size_x * pixel_size_y)
        pixel_area_km2 = pixel_area_m2 / 1_000_000
    
    stats = {}
    for label, count in zip(unique, counts):
        if label == -1: continue 
        area_km2 = count * pixel_area_km2
        stats[int(label)] = round(float(area_km2), 4)
        
    return stats
