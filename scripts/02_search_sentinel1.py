"""
Phase 3a — Search Sentinel-1 scenes via Copernicus Data Space API
"""
import requests, json, os

with open(os.path.expanduser("~/project_EMSR850/cdse_credentials.json")) as f:
    creds = json.load(f)

# Get access token — client_id must be 'cdse-public'
token = requests.post(
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    data={"grant_type":"password","username":creds["username"],
          "password":creds["password"],"client_id":"cdse-public"}
).json()["access_token"]
print("Token obtained ✓")

WEST, SOUTH, EAST, NORTH = 19.357007, 39.928600, 20.339175, 41.962882

def search_s1(date_start, date_end, label):
    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    filter_str = (
        f"Collection/Name eq 'SENTINEL-1' "
        f"and Attributes/OData.CSC.StringAttribute/any("
        f"att:att/Name eq 'productType' and "
        f"att/OData.CSC.StringAttribute/Value eq 'IW_GRDH_1S') "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(("
        f"{WEST} {SOUTH},{EAST} {SOUTH},{EAST} {NORTH},"
        f"{WEST} {NORTH},{WEST} {SOUTH}))') "
        f"and ContentDate/Start gt {date_start}T00:00:00.000Z "
        f"and ContentDate/Start lt {date_end}T23:59:59.000Z"
    )
    resp = requests.get(url, params={"$filter":filter_str,
                                     "$orderby":"ContentDate/Start desc","$top":"5"})
    products = resp.json().get("value",[])
    print(f"\n{label} — {len(products)} products found:")
    for p in products:
        mb = int(p.get("ContentLength",0))/1024/1024
        print(f"  {p['Name']}")
        print(f"    Date: {p['ContentDate']['Start']}  Size: {mb:.0f} MB")
        print(f"    ID  : {p['Id']}")
    return products

pre  = search_s1("2025-10-01","2025-11-17","PRE-EVENT")
post = search_s1("2025-11-19","2025-11-30","POST-EVENT")

ids = {
    "pre_id"   : pre[0]["Id"],   "pre_name" : pre[0]["Name"],
    "post_id"  : post[0]["Id"],  "post_name": post[0]["Name"],
}
id_path = os.path.expanduser("~/project_EMSR850/sentinel1_ids.json")
with open(id_path,"w") as f:
    json.dump(ids,f,indent=2)
print(f"\nIDs saved: {id_path}")
print(json.dumps(ids,indent=2))
