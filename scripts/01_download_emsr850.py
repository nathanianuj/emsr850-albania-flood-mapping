"""
Phase 1 — Download and merge EMSR850 reference products
Copernicus EMS EMSR850 Albania Flood, 18-19 November 2025
"""
import geopandas as gpd
import pandas as pd
import glob, os

ref_dir = os.path.expanduser("~/project_EMSR850/data/copernicus_ref/")

# Load ONLY observedEventA from DEL products
obs_files = sorted(glob.glob(f"{ref_dir}/*DEL*/*observedEventA*.shp"))
print(f"Found {len(obs_files)} observedEventA files:")
for f in obs_files:
    print(f"  {os.path.basename(f)}")

gdfs = []
for f in obs_files:
    gdf = gpd.read_file(f)
    aoi_tag = os.path.basename(f).split("_")[1]
    gdf["source_aoi"] = aoi_tag
    gdfs.append(gdf)
    print(f"{aoi_tag}: {len(gdf)} features")

all_flood = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
print(f"\nTotal merged features: {len(all_flood)}")

# Save merged file
out = f"{ref_dir}EMSR850_ALL_DEL_observedEvent_merged.gpkg"
all_flood.to_file(out, driver="GPKG")
print(f"Saved: {out}")

# Area stats
all_utm = all_flood.to_crs(epsg=32634)
total_ha = all_utm.geometry.area.sum() / 10000
print(f"Total flood area: {total_ha:.1f} ha")

# Bounding box
all_wgs = all_flood.to_crs(epsg=4326)
minx, miny, maxx, maxy = all_wgs.total_bounds
print(f"\nBounding box:")
print(f"  West : {minx:.6f}")
print(f"  South: {miny:.6f}")
print(f"  East : {maxx:.6f}")
print(f"  North: {maxy:.6f}")

# Save AOI GeoJSON
aoi_gdf = gpd.GeoDataFrame(geometry=all_wgs.dissolve().envelope, crs="EPSG:4326")
aoi_gdf.to_file(os.path.expanduser("~/project_EMSR850/aoi_EMSR850.geojson"), driver="GeoJSON")
print("AOI GeoJSON saved.")
