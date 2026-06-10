"""
Phase 7 — Export GHSL Population and Built-Up layers via Google Earth Engine
"""
import ee
ee.Initialize(project="anujnathani")

aoi = ee.Geometry.Rectangle([19.357007, 39.928600, 20.339175, 41.962882])

exports = [
    (ee.ImageCollection("JRC/GHSL/P2023A/GHS_POP")
        .filterDate("2020","2021").first().clip(aoi), "GHSL_Population", 100),
    (ee.ImageCollection("JRC/GHSL/P2023A/GHS_BUILT_S")
        .filterDate("2020","2021").first().clip(aoi), "GHSL_BuiltUp", 100),
]

for image, name, scale in exports:
    task = ee.batch.Export.image.toDrive(
        image=image.toFloat(),
        description=f"{name}_Albania_EMSR850",
        folder="EMSR850_project", fileNamePrefix=name,
        region=aoi, scale=scale, crs="EPSG:32634", maxPixels=1e10)
    task.start()
    print(f"Started: {name}  task: {task.id}")

print("\nMonitor: https://code.earthengine.google.com/tasks")
