from zip_sync.ads_api.campaign_fetcher import CampaignFetcher
from zip_sync.ads_api.google_ads_client import GoogleAdsClient
from zip_sync.environment.folder_paths import get_google_ads_api_yaml_path
from zip_sync.environment.environment_service import EnvironmentService

def update_campaigns(criteria_ids: list[str]) -> None:
    campaign_ids = _get_campaign_ids()
    print(campaign_ids)
    
def _get_campaign_ids() -> list[str]:
    """
    Get the active campaign IDs from the Google Ads API.
    """
    google_ads_client = _get_google_ads_client()
    google_ads_account_id = EnvironmentService().get_google_ads_account_id()
    campaign_fetcher = CampaignFetcher(google_ads_client, google_ads_account_id)
    campaign_ids = campaign_fetcher.get_active_campaign_ids()
    return campaign_ids
    
def _get_google_ads_client() -> GoogleAdsClient:
    """
    Get the Google Ads client.
    """
    google_ads_client = GoogleAdsClient()
    client = google_ads_client.get(get_google_ads_api_yaml_path())
    return client