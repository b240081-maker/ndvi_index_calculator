import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

def create_ndvi_colormap():
    from matplotlib.colors import LinearSegmentedColormap
    colors = ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837"]
    cmap = LinearSegmentedColormap.from_list("NDVI", colors, N=256)
    return cmap

def plot_ndvi_histogram(ndvi_data):
    flat_ndvi = ndvi_data.flatten()
    flat_ndvi = flat_ndvi[~np.isnan(flat_ndvi)]
    fig = px.histogram(flat_ndvi, nbins=50, title="Spectral Distribution", labels={'value': 'NDVI', 'count': 'Frequency'})
    fig.update_layout(showlegend=False)
    return fig
