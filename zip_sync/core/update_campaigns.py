import time
from zip_sync.utils.chunker import chunk_list
from zip_sync.ads_api.campaign_fetcher import CampaignFetcher
from zip_sync.ads_api.campaign_criterion_mutator import CampaignCriterionMutator
from zip_sync.ads_api.campaign_criterion_id_fetcher import CampaignCriterionIdFetcher
from zip_sync.ads_api.google_ads_client import GoogleAdsClient
from zip_sync.environment.folder_paths import get_google_ads_api_yaml_path
from zip_sync.environment.environment_service import EnvironmentService


def update_campaigns(api_criteria_ids: list[str]) -> None:
    if not EnvironmentService().api_active():
        print("API is not active. Skipping campaign zip code sync. See API_ACTIVE environment variable.")
        return
    
    campaign_ids = _get_campaign_ids()
    time.sleep(10)
    campaign_criterion_ids_map = _get_campaign_criterion_ids_map(campaign_ids)
    time.sleep(10)
    _sync_campaign_criteria(campaign_ids, api_criteria_ids, campaign_criterion_ids_map)
    
def _get_campaign_ids() -> list[str]:
    """
    Get the active campaign IDs from the Google Ads API.
    """
    google_ads_client = _get_google_ads_client()
    google_ads_account_id = EnvironmentService().get_google_ads_account_id()
    campaign_fetcher = CampaignFetcher(google_ads_client, google_ads_account_id)
    campaign_ids = campaign_fetcher.get_active_campaign_ids()
    return campaign_ids

def _get_campaign_criterion_ids_map(campaign_ids: list[str]) -> dict[str, dict[str, str]]:
    """
    Get the campaign criterion IDs map.
    """
    google_ads_client = _get_google_ads_client()
    google_ads_account_id = EnvironmentService().get_google_ads_account_id()
    campaign_criterion_id_fetcher = CampaignCriterionIdFetcher(google_ads_client, google_ads_account_id)
    campaign_criterion_ids_map = campaign_criterion_id_fetcher.get_campaign_location_criteria_for_campaigns(campaign_ids)
    return campaign_criterion_ids_map

def _sync_campaign_criteria(campaign_ids: list[str], api_criteria_ids: list[str], campaign_criterion_ids_map: dict[str, dict[str, str]]) -> None:
    """
    Sync the campaign criteria.
    """
    google_ads_client = _get_google_ads_client()
    google_ads_account_id = EnvironmentService().get_google_ads_account_id()
    campaign_criterion_mutator = CampaignCriterionMutator(google_ads_client, google_ads_account_id)
    
    api_criteria_set = set(api_criteria_ids)

    for campaign_id in campaign_ids:
        existing_criteria = campaign_criterion_ids_map.get(campaign_id, {})
        existing_criteria_ids = set(existing_criteria.keys())

        # Determine which criteria to add and remove
        criteria_to_add = list(api_criteria_set - existing_criteria_ids)
        criteria_to_remove_ids = list(existing_criteria_ids - api_criteria_set)
        
        # Get the resource names for the criteria to remove
        resource_names_to_remove = [existing_criteria[crit_id] for crit_id in criteria_to_remove_ids]

        if EnvironmentService().get_test_mode():
            print(f"Test mode is enabled. Only the first criteria will be added to the campaign.")
            criteria_to_add = criteria_to_add[0:1]

        chunk_size = EnvironmentService().get_chunk_size()
        if criteria_to_add:
            for chunk in chunk_list(criteria_to_add, chunk_size):
                campaign_criterion_mutator.add_location_criteria_to_campaign(campaign_id, chunk)
                time.sleep(5)
            
        
        if EnvironmentService().get_test_mode():
            print(f"Test mode is enabled. Only the first criteria will be removed from the campaign.")
            resource_names_to_remove = resource_names_to_remove[0:1]
        
        if resource_names_to_remove:
            for chunk in chunk_list(resource_names_to_remove, chunk_size):
                campaign_criterion_mutator.remove_location_criteria_from_campaign(campaign_id, chunk)
                time.sleep(5)
    
def _get_google_ads_client() -> GoogleAdsClient:
    """
    Get the Google Ads client.
    """
    google_ads_client = GoogleAdsClient()
    client = google_ads_client.get(get_google_ads_api_yaml_path())
    return client