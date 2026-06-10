"""
Phase 6 — Export GPM IMERG rainfall (15-19 Nov 2025) via Google Earth Engine
"""
import ee
ee.Initialize(project="anujnathani")

aoi = ee.Geometry.Rectangle([19.357007, 39.928600, 20.339175, 41.962882])

rainfall = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
    .filterBounds(aoi)
    .filterDate("2025-11-15","2025-11-19")
    .select("precipitation")
    .sum()
    .clip(aoi))

task = ee.batch.Export.image.toDrive(
    image=rainfall.toFloat(),
    description="GPM_Rainfall_EMSR850",
    folder="EMSR850_project",
    fileNamePrefix="GPM_rainfall_Nov2025",
    region=aoi, scale=1000, crs="EPSG:32634", maxPixels=1e10)
task.start()
print(f"Rainfall export started — task: {task.id}")
print("Monitor: https://code.earthengine.google.com/tasks")
