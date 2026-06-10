"""
Phase 9 — Flood mask extraction using absolute backscatter threshold
Method: Otsu-guided absolute VV threshold (-13 dB) on POST scene
clipped to EMSR850 AOI polygons
"""
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from skimage.filters import threshold_otsu
import geopandas as gpd
import glob, pandas as pd, os

proc_dir = os.path.expanduser("~/project_EMSR850/processing/")
out_dir  = os.path.expanduser("~/project_EMSR850/output/change_masks/")
ref_dir  = os.path.expanduser("~/project_EMSR850/data/copernicus_ref/")
os.makedirs(out_dir, exist_ok=True)

# Load AOI polygons (exact mapped areas, not bounding box)
aoi_files = sorted(glob.glob(f"{ref_dir}/*DEL*/*areaOfInterestA*.shp"))
aoi_all   = gpd.GeoDataFrame(
    pd.concat([gpd.read_file(f) for f in aoi_files], ignore_index=True),
    crs=gpd.read_file(aoi_files[0]).crs)

post_vv_path = f"{proc_dir}S1_POST_processed.data/Sigma0_VV_db.img"

# Clip POST VV to AOI polygons
with rasterio.open(post_vv_path) as src:
    geoms = [g.__geo_interface__ for g in aoi_all.to_crs(src.crs).geometry]
    clipped, transform = rio_mask(src, geoms, crop=True, nodata=np.nan)
    vv = clipped[0].astype(np.float32)
    profile = src.profile.copy()
    profile.update(height=vv.shape[0], width=vv.shape[1],
                   transform=transform, count=1, dtype="float32", nodata=np.nan)

print(f"Clipped VV shape: {vv.shape}")
print(f"Clipped VV range: {np.nanmin(vv):.2f} to {np.nanmax(vv):.2f} dB")

valid = ~np.isnan(vv)

# Threshold sensitivity analysis
print(f"\n{'Threshold':>10} {'Area (ha)':>12}")
print("-"*25)
for t in [-10,-11,-12,-13,-14,-15,-16,-18]:
    a = np.sum((vv < t) & valid) * 100 / 10000
    marker = " <- near 2860 ha" if 1500 < a < 5000 else ""
    print(f"{t:>10}  {a:>12.1f}{marker}")

# Apply final threshold -13 dB
THRESHOLD = -13.0
flood = (vv < THRESHOLD) & valid
area_ha = np.sum(flood) * 100 / 10000
print(f"\nFinal threshold : {THRESHOLD} dB")
print(f"Flood area      : {area_ha:.1f} ha")
print(f"Reference       : 2860.8 ha")
print(f"Difference      : {area_ha-2860.8:+.1f} ha ({(area_ha/2860.8-1)*100:+.1f}%)")

flood_mask = np.where(valid, flood.astype(np.uint8), 255).astype(np.uint8)
profile.update(dtype=rasterio.uint8, nodata=255)

final_path = f"{out_dir}S1_flood_mask_final.tif"
with rasterio.open(final_path, "w", **profile) as dst:
    dst.write(flood_mask, 1)
print(f"\nFlood mask saved: {final_path}")
