import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src import processing, analysis, utils
import tempfile
import os

# Console print for student details on load
print("--------------------------------------------------")
print("Project: Vegetation Health Assessment and Land Cover Analysis")
print("Student: Rakshit")
print("Roll No: B240081")
print("Institute: NIT Sikkim")
print("Organization: Indian Space Academy (ISA)")
print("Description: This system performs multi-spectral analysis of satellite imagery")
print("to quantify vegetation health and land cover distribution using NDVI and")
print("spectral clustering techniques.")
print("--------------------------------------------------")

st.set_page_config(
    page_title="ISA - Vegetation Health Assessment", 
    layout="wide"
)

# Professional CSS to hide Streamlit branding and style the horizontal radio
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp [data-testid="stToolbar"] {display: none;}
            
            /* Horizontal Radio Button Styling */
            div.row-widget.stRadio > div {
                flex-direction: row;
                justify-content: center;
                gap: 20px;
            }
            div.row-widget.stRadio > div[role="radiogroup"] > label {
                padding: 10px 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                cursor: pointer;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Application Header
st.title("Vegetation Health Assessment and Land Cover Analysis")
st.write("Indian Space Academy - Winter Training Program 2026")

# Correctly ordered horizontal navbar as requested
page = st.radio(
    "Navigation Bar",
    ["Home [H]", "Analysis [A]", "Print [P]", "About [i]"],
    index=1,
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

if "Home" in page:
    st.subheader("Welcome to the Analytical Platform")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Submission Summary")
        st.write("""
        This platform is developed for the high-precision assessment of vegetation health 
        and categorical land cover classification using multi-spectral satellite imagery. 
        It integrates spectral indexing and unsupervised classification methodology.
        """)
        st.write("Current Status: Optimized for Sentinel-2 and Landsat-8 datasets.")
        
    with col2:
        st.info("Student Information")
        st.write("**Name:** Rakshit")
        st.write("**Roll Number:** B240081")
        st.write("**Institute:** NIT Sikkim")
        st.write("**Affiliation:** Indian Space Academy (ISA)")

elif "Analysis" in page:
    st.subheader("Imagery Acquisition and Processing")
    
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        uploaded_red = st.file_uploader("Red Spectral Band (red.tif / Band 4)", type=['tif', 'tiff'])
    with col_up2:
        uploaded_nir = st.file_uploader("Near-Infrared Spectral Band (nir.tif / Band 8)", type=['tif', 'tiff'])

    st.sidebar.header("Calibration Controls")
    n_clusters = st.sidebar.slider("Spectral Classes", min_value=2, max_value=8, value=4)

    if uploaded_red and uploaded_nir:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_red:
                tmp_red.write(uploaded_red.getvalue())
                red_path = tmp_red.name
                
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_nir:
                tmp_nir.write(uploaded_nir.getvalue())
                nir_path = tmp_nir.name

            with st.spinner("Executing analytical subroutines..."):
                print(f"Loading bands: {red_path}, {nir_path}")
                red_band, meta_red = processing.load_band(red_path)
                nir_band, meta_nir = processing.load_band(nir_path)
                
                print(f"Bands loaded. Shape: {red_band.shape}")
                
                if red_band.shape != nir_band.shape:
                    st.error("Error: Radiomatric mismatch. Band dimensions must be identical.")
                else:
                    print("Calculating NDVI...")
                    ndvi_image = processing.calculate_ndvi(red_band, nir_band)
                    print(f"NDVI calculated. Range: {np.nanmin(ndvi_image)} to {np.nanmax(ndvi_image)}")
                    
                    print(f"Performing clustering with {n_clusters} classes...")
                    classified_map, centers = analysis.perform_kmeans_clustering(ndvi_image, n_clusters=n_clusters)
                    
                    # Extract high-precision pixel dimensions from Affine transform
                    transform = meta_red['transform']
                    pixel_size_x = transform[0]
                    pixel_size_y = transform[4]
                    print(f"Pixel dimensions: {pixel_size_x} x {pixel_size_y}")
                    
                    stats = analysis.calculate_area_statistics(classified_map, pixel_size_x, pixel_size_y)
                    print(f"Statistics calculated: {stats}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("NDVI Spectral Heatmap")
                        fig_ndvi, ax_ndvi = plt.subplots(figsize=(10, 10))
                        cmap = utils.create_ndvi_colormap()
                        im = ax_ndvi.imshow(ndvi_image, cmap=cmap, vmin=-1, vmax=1)
                        plt.colorbar(im, ax=ax_ndvi, label="Normalised Difference Vegetation Index")
                        ax_ndvi.axis('off')
                        st.pyplot(fig_ndvi)
                        
                    with col2:
                        st.subheader("Categorified Spectral Zones")
                        fig_cls, ax_cls = plt.subplots(figsize=(10, 10))
                        masked_cls = np.ma.masked_where(classified_map == -1, classified_map)
                        cmap_cls = plt.get_cmap("RdYlGn", n_clusters)
                        im_cls = ax_cls.imshow(masked_cls, cmap=cmap_cls)
                        plt.colorbar(im_cls, ax=ax_cls, ticks=range(n_clusters), label="Class ID")
                        ax_cls.axis('off')
                        st.pyplot(fig_cls)

                    # Save figures for the Print Report page
                    st.session_state['last_ndvi_fig'] = fig_ndvi
                    st.session_state['last_cls_fig'] = fig_cls

                    st.divider()
                    col3, col4 = st.columns(2)
                    
                    with col3:
                       st.subheader("Quantitative Statistics")
                       if stats:
                           df_stats = pd.DataFrame([
                               {"Zone": f"Spectral Class {k}", "Area (km2)": v} for k, v in stats.items()
                           ])
                           st.dataframe(df_stats, width='stretch', hide_index=True)
                           st.bar_chart(df_stats.set_index("Zone"))
                       else:
                           st.warning("Insufficient valid land data identified for area quantification.")

                    with col4:
                        st.subheader("Spectral Intensity Distribution")
                        hist_fig = utils.plot_ndvi_histogram(ndvi_image)
                        st.plotly_chart(hist_fig, width='stretch')

                    st.success("Analysis finalized successfully.")
                    
                    st.session_state['last_stats'] = stats
                    st.session_state['last_ndvi_range'] = (float(np.nanmin(ndvi_image)), float(np.nanmax(ndvi_image)))
                    
        except Exception as e:
            st.error(f"System Operational Error: {e}")
        finally:
            if 'red_path' in locals(): os.remove(red_path)
            if 'nir_path' in locals(): os.remove(nir_path)
    else:
        st.info("Awaiting multi-spectral band upload to initialize processing.")

elif "Print" in page:
    st.title("Formal Assessment Report")
    st.write("Indian Space Academy - Winter Training Program 2026")

    if 'last_stats' in st.session_state:
        import io
        import base64

        ndvi_min, ndvi_max = st.session_state['last_ndvi_range']
        stats = st.session_state['last_stats']
        n_classes = len(stats)

        # Encode NDVI figure to base64
        ndvi_b64 = ""
        cls_b64 = ""
        if 'last_ndvi_fig' in st.session_state:
            buf = io.BytesIO()
            st.session_state['last_ndvi_fig'].savefig(buf, format='png', bbox_inches='tight')
            ndvi_b64 = base64.b64encode(buf.getvalue()).decode()
        if 'last_cls_fig' in st.session_state:
            buf = io.BytesIO()
            st.session_state['last_cls_fig'].savefig(buf, format='png', bbox_inches='tight')
            cls_b64 = base64.b64encode(buf.getvalue()).decode()

        # Build table rows
        table_rows = "".join([
            f"<tr><td>Class {k}</td><td>{v} sq. km</td></tr>"
            for k, v in stats.items()
        ])

        # Build maps HTML
        maps_html = ""
        if ndvi_b64:
            maps_html += f'<div class="map-block"><p><strong>NDVI Spectral Heatmap</strong></p><img src="data:image/png;base64,{ndvi_b64}" /></div>'
        if cls_b64:
            maps_html += f'<div class="map-block"><p><strong>Categorised Land Cover Map</strong></p><img src="data:image/png;base64,{cls_b64}" /></div>'

        html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ISA Report - Rakshit B240081</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
    h1 {{ text-align: center; color: #1a4a7a; border-bottom: 2px solid #1a4a7a; padding-bottom: 10px; }}
    h2 {{ color: #1a4a7a; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 30px; }}
    .header-sub {{ text-align: center; color: #555; margin-bottom: 30px; }}
    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0; }}
    .info-grid p {{ margin: 4px 0; }}
    table {{ border-collapse: collapse; width: 60%; margin: 16px 0; }}
    th, td {{ border: 1px solid #aaa; padding: 8px 14px; text-align: left; }}
    th {{ background: #1a4a7a; color: white; }}
    tr:nth-child(even) {{ background: #f4f4f4; }}
    .maps {{ display: flex; gap: 20px; flex-wrap: wrap; margin-top: 16px; }}
    .map-block {{ flex: 1; min-width: 300px; text-align: center; }}
    .map-block img {{ width: 100%; border: 1px solid #ccc; border-radius: 4px; }}
    @media print {{
      button {{ display: none; }}
    }}
  </style>
</head>
<body>
  <h1>Vegetation Health Assessment and Land Cover Analysis</h1>
  <p class="header-sub">Indian Space Academy - Winter Training Program 2026 | P2</p>

  <h2>1. Student & Project Information</h2>
  <div class="info-grid">
    <p><strong>Name:</strong> Rakshit</p>
    <p><strong>Programme:</strong> ISA Winter Training Program 2026</p>
    <p><strong>Roll Number:</strong> B240081</p>
    <p><strong>Affiliation:</strong> Indian Space Academy (ISA)</p>
    <p><strong>Institute:</strong> NIT Sikkim</p>
    <p><strong>Submission Date:</strong> 22nd February 2026</p>
  </div>

  <h2>2. Spectral Analysis Summary</h2>
  <p><strong>NDVI Range:</strong> {ndvi_min:.4f} (min) to {ndvi_max:.4f} (max)</p>
  <p><strong>Clustering Method:</strong> Unsupervised K-Means Spectral Classification</p>
  <p><strong>Number of Spectral Classes:</strong> {n_classes}</p>

  <h2>3. Quantified Spatial Area Distribution</h2>
  <table>
    <tr><th>Spectral Zone</th><th>Total Area</th></tr>
    {table_rows}
  </table>

  <h2>4. Generated Analysis Maps</h2>
  <div class="maps">
    {maps_html if maps_html else "<p>No maps available. Please run analysis first.</p>"}
  </div>
</body>
</html>"""

        st.caption("Preview of your report is shown below. Click the button to download and open in a browser, then use Ctrl+P / Cmd+P to save as PDF.")

        st.download_button(
            label="Download Report as HTML (then Print to PDF)",
            data=html_report,
            file_name="Rakshit_P2_Report.html",
            mime="text/html"
        )

        st.divider()

        # On-screen preview
        st.markdown("### Student & Project Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:** Rakshit")
            st.write("**Roll Number:** B240081")
            st.write("**Institute:** National Institute of Technology (NIT) Sikkim")
        with col2:
            st.write("**Programme:** ISA Winter Training Program 2026")
            st.write("**Affiliation:** Indian Space Academy (ISA)")
            st.write("**Date:** 22nd February 2026")

        st.divider()
        st.markdown("### Spectral Analysis Summary")
        st.write(f"**NDVI Range:** {ndvi_min:.4f} to {ndvi_max:.4f}")
        st.write(f"**Clustering Method:** Unsupervised K-Means | **Classes:** {n_classes}")

        st.divider()
        st.markdown("### Quantified Spatial Area Distribution")
        report_df = pd.DataFrame([
            {"Spectral Zone": f"Class {k}", "Total Area (sq. km)": v} for k, v in stats.items()
        ])
        st.table(report_df)

        st.divider()
        st.markdown("### Generated Analysis Maps")
        if 'last_ndvi_fig' in st.session_state and 'last_cls_fig' in st.session_state:
            map_col1, map_col2 = st.columns(2)
            with map_col1:
                st.markdown("**NDVI Spectral Heatmap**")
                st.pyplot(st.session_state['last_ndvi_fig'])
            with map_col2:
                st.markdown("**Categorised Land Cover Map**")
                st.pyplot(st.session_state['last_cls_fig'])

    else:
        st.warning("No analytical data found. Please run the Analysis Dashboard first, then return here.")

elif "About" in page:
    st.title("Technical Specifications and Objective")
    st.markdown("""
    ### Project Methodology
    The system employs multi-spectral radiometry to evaluate biomass health and land cover. 
    By processing infrared and visible red reflectance, it calculates the **Normalised Difference Vegetation Index (NDVI)**.
    
    ### Analytical Framework
    1. **Data Normalisation:** Adjusting raw sensor counts for multi-spectral analysis.
    2. **Spectral Mapping:** Categorising pixels into land cover classes using unsupervised grouping.
    3. **Spatial Quantification:** Calculating area coverage in square kilometers based on sensor resolution.
    
    ### Objectives for ISA Training
    This project is submitted to fulfill the technical requirements of the Winter Training Program at the 
    Indian Space Academy. It provides a robust tool for environmental monitoring and geospatial diagnostics.
    """)
