"""
Phase 4 — Export Sentinel-2 PRE and POST scenes via Google Earth Engine
"""
import ee, os
ee.Initialize(project="anujnathani")

aoi = ee.Geometry.Rectangle([19.357007, 39.928600, 20.339175, 41.962882])

pre_s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi).filterDate("2025-09-01","2025-11-17")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",10))
    .sort("CLOUDY_PIXEL_PERCENTAGE").first()
    .select(["B2","B3","B4","B8","B11","B12"]))

post_s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi).filterDate("2025-11-19","2025-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",10))
    .sort("CLOUDY_PIXEL_PERCENTAGE").first()
    .select(["B2","B3","B4","B8","B11","B12"]))

pre_date  = pre_s2.date().format("YYYY-MM-dd").getInfo()
post_date = post_s2.date().format("YYYY-MM-dd").getInfo()
print(f"PRE  scene: {pre_s2.getInfo()['id']}  date: {pre_date}")
print(f"POST scene: {post_s2.getInfo()['id']}  date: {post_date}")

for img, desc, prefix in [
    (pre_s2,  "S2_PRE_Albania_EMSR850",  f"S2_PRE_{pre_date}"),
    (post_s2, "S2_POST_Albania_EMSR850", f"S2_POST_{post_date}")]:
    task = ee.batch.Export.image.toDrive(
        image=img.toFloat(), description=desc,
        folder="EMSR850_project", fileNamePrefix=prefix,
        region=aoi, scale=10, crs="EPSG:32634", maxPixels=1e10)
    task.start()
    print(f"Started: {desc}  task: {task.id}")

print("\nMonitor: https://code.earthengine.google.com/tasks")
