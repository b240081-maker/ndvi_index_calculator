# Vegetation Health Assessment and Land Cover Analysis

Submitted as part of the **Winter Training Program** at the **Indian Space Academy (ISA)**.

## Overview
This platform provides tools for the analysis of multi-spectral satellite imagery (Sentinel-2 and Landsat-8). It utilizes spectral indices (NDVI) and unsupervised classification algorithms to map vegetation density and assess environmental health.

### Student Details
- **Name:** Rakshit
- **Roll No:** B240081
- **Institute:** NIT Sikkim

## Features
- Multi-spectral band processing
- NDVI (Normalized Difference Vegetation Index) calculation
- Spectral clustering for land cover classification
- Quantitative area statistics
- High-resolution visualization

## Usage
1. Launch the dashboard:
   ```bash
   python3 -m streamlit run app.py
   ```
2. Navigate to the **Dashboard** via the sidebar.
3. Upload the **Red** and **NIR** spectral bands in GeoTIFF format.
4. Review the generated maps and area statistics.
