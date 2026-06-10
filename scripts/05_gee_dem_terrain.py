"""
Phase 5 — Export DEM, Slope, Aspect via Google Earth Engine
"""
import ee
ee.Initialize(project="anujnathani")

aoi = ee.Geometry.Rectangle([19.357007, 39.928600, 20.339175, 41.962882])

dem    = ee.Image("USGS/SRTMGL1_003").clip(aoi)
slope  = ee.Terrain.slope(dem)
aspect = ee.Terrain.aspect(dem)

for image, name in [(dem,"DEM_SRTM30"),(slope,"SLOPE"),(aspect,"ASPECT")]:
    task = ee.batch.Export.image.toDrive(
        image=image.toFloat(),
        description=f"{name}_Albania_EMSR850",
        folder="EMSR850_project", fileNamePrefix=name,
        region=aoi, scale=30, crs="EPSG:32634", maxPixels=1e10)
    task.start()
    print(f"Started: {name}  task: {task.id}")

print("\nMonitor: https://code.earthengine.google.com/tasks")
