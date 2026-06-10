"""
Phase 10 — Validation of SAR flood mask against EMSR850 reference products
Metrics: Precision, Recall, F1, IoU
Output: comparison map (3 panels)
"""
import numpy as np
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import os

out_dir  = os.path.expanduser("~/project_EMSR850/output/")
ref_dir  = os.path.expanduser("~/project_EMSR850/data/copernicus_ref/")
mask_dir = os.path.expanduser("~/project_EMSR850/output/change_masks/")
os.makedirs(out_dir, exist_ok=True)

ref = gpd.read_file(f"{ref_dir}EMSR850_ALL_DEL_observedEvent_merged.gpkg")

with rasterio.open(f"{mask_dir}S1_flood_mask_final.tif") as src:
    flood_mask = src.read(1)
    transform  = src.transform
    crs        = src.crs

ref_r = rasterize(
    [(g,1) for g in ref.to_crs(crs).geometry],
    out_shape=flood_mask.shape, transform=transform, fill=0, dtype=np.uint8)

valid = flood_mask != 255
TP = int(np.sum((flood_mask==1)&(ref_r==1)&valid))
FP = int(np.sum((flood_mask==1)&(ref_r==0)&valid))
FN = int(np.sum((flood_mask==0)&(ref_r==1)&valid))

precision = TP/(TP+FP) if (TP+FP)>0 else 0
recall    = TP/(TP+FN) if (TP+FN)>0 else 0
f1        = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0
iou       = TP/(TP+FP+FN) if (TP+FP+FN)>0 else 0

print(f"\n=== VALIDATION RESULTS ===")
print(f"True Positives : {TP:,}")
print(f"False Positives: {FP:,}")
print(f"False Negatives: {FN:,}")
print(f"Precision      : {precision:.3f}")
print(f"Recall         : {recall:.3f}")
print(f"F1 Score       : {f1:.3f}")
print(f"IoU            : {iou:.3f}")
print(f"\nNOTE: Low F1 reflects 12-day temporal gap (event 18 Nov vs SAR 30 Nov)")

# Comparison map
fig, axes = plt.subplots(1,3,figsize=(18,7))
fig.suptitle("EMSR850 Albania Flood — SAR Flood Mapping Results\n"
             "Event: 18-19 Nov 2025  |  SAR POST: 30 Nov 2025",
             fontsize=13, fontweight="bold")

axes[0].imshow(np.where(ref_r==1,1,0).astype(float), cmap="Blues")
axes[0].set_title("EMSR850 Reference\n(Peak flood, 18-19 Nov)\n2,860.8 ha"); axes[0].axis("off")

axes[1].imshow(np.where(flood_mask==1,1,np.where(flood_mask==255,np.nan,0)).astype(float), cmap="Reds")
axes[1].set_title("SAR Flood Mask\n(Post-event, 30 Nov, -13 dB)\n2,617.8 ha"); axes[1].axis("off")

agree = np.zeros(flood_mask.shape, dtype=np.uint8)
agree[valid&(flood_mask==1)&(ref_r==1)] = 3
agree[valid&(flood_mask==1)&(ref_r==0)] = 2
agree[valid&(flood_mask==0)&(ref_r==1)] = 1
cmap4 = ListedColormap(["#f0f0f0","#2166ac","#f4a582","#00b4d8"])
axes[2].imshow(agree, cmap=cmap4, vmin=0, vmax=3)
axes[2].set_title("Agreement Map\n(SAR vs EMSR850)"); axes[2].axis("off")
patches = [mpatches.Patch(color="#00b4d8",label="True Positive"),
           mpatches.Patch(color="#f4a582",label="False Positive"),
           mpatches.Patch(color="#2166ac",label="False Negative"),
           mpatches.Patch(color="#f0f0f0",label="True Negative")]
axes[2].legend(handles=patches, loc="lower right", fontsize=7)

plt.tight_layout()
map_path = f"{out_dir}final_comparison_map.png"
plt.savefig(map_path, dpi=150, bbox_inches="tight")
print(f"\nMap saved: {map_path}")
