"""
Phase 3b — Download Sentinel-1 scenes from Copernicus Data Space
"""
import requests, json, os
from tqdm import tqdm

with open(os.path.expanduser("~/project_EMSR850/cdse_credentials.json")) as f:
    creds = json.load(f)

token = requests.post(
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    data={"grant_type":"password","username":creds["username"],
          "password":creds["password"],"client_id":"cdse-public"}
).json()["access_token"]
print("Token obtained ✓")

with open(os.path.expanduser("~/project_EMSR850/sentinel1_ids.json")) as f:
    ids = json.load(f)

OUT_DIR = os.path.expanduser("~/project_EMSR850/data/sentinel1/")
os.makedirs(OUT_DIR, exist_ok=True)

def download(product_id, name, token, out_dir):
    path = os.path.join(out_dir, f"{name}.zip")
    if os.path.exists(path):
        print(f"Already exists: {name}"); return
    url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    r = session.get(url, stream=True, allow_redirects=True)
    total = int(r.headers.get("content-length",0))
    print(f"\nDownloading: {name}  ({total/1024/1024:.0f} MB)")
    with open(path,"wb") as f, tqdm(total=total,unit="B",unit_scale=True) as bar:
        for chunk in r.iter_content(8192):
            f.write(chunk); bar.update(len(chunk))
    actual = os.path.getsize(path)
    print(f"Expected: {total/1024/1024:.0f} MB  Actual: {actual/1024/1024:.0f} MB")
    print(f"Saved: {path}")

download(ids["pre_id"],  ids["pre_name"],  token, OUT_DIR)
download(ids["post_id"], ids["post_name"], token, OUT_DIR)
print("\nBoth scenes downloaded.")
