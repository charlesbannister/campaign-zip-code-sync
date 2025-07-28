import os
from google.ads.googleads.client import GoogleAdsClient as Client

class GoogleAdsClient:

    def get(self, yaml_path) -> Client:
        with open(os.path.join(yaml_path), "r") as f:
            yaml_string = f.read()
            googleads_client = Client.load_from_string(yaml_string, version="v20")
            return googleads_client