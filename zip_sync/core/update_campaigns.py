import time
from zip_sync.utils.chunker import chunk_list
from zip_sync.ads_api.campaign_fetcher import CampaignFetcher
from zip_sync.ads_api.campaign_criterion_mutator import CampaignCriterionMutator
from zip_sync.ads_api.campaign_criterion_id_fetcher import CampaignCriterionIdFetcher
from zip_sync.ads_api.google_ads_client import GoogleAdsClient
from zip_sync.environment.folder_paths import get_google_ads_api_yaml_path
from zip_sync.environment.environment_service import EnvironmentService
from zip_sync.slack.send_admin_slack import send_admin_slack


def update_campaigns(api_criteria_ids: list[str]) -> None:
    if not EnvironmentService().get_api_active():
        print("API is not active. Skipping campaign zip code sync. See API_ACTIVE environment variable.")
        send_admin_slack("API is not active. Skipping campaign zip code sync. See API_ACTIVE environment variable.")
        return
    
    campaign_ids = _get_campaign_ids()
    campaign_criterion_ids_map = _get_campaign_criterion_ids_map(campaign_ids)
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

def _get_criteria_to_add(api_criteria_ids: list[str], existing_criteria_ids: set[str]) -> list[str]:
    """
    Return criteria IDs that need to be added.
    """
    return list(set(api_criteria_ids) - existing_criteria_ids)


def _get_criteria_to_remove(api_criteria_ids: list[str], existing_criteria_ids: set[str]) -> list[str]:
    """
    Return criteria IDs that need to be removed.
    """
    return list(existing_criteria_ids - set(api_criteria_ids))


def _get_resource_names_to_remove(criteria_to_remove_ids: list[str], existing_criteria: dict[str, str]) -> list[str]:
    """
    Map criteria IDs to resource names for removal.
    """
    return [existing_criteria[crit_id] for crit_id in criteria_to_remove_ids]


def _apply_campaign_criteria_changes(campaign_criterion_mutator, campaign_id: str, criteria_to_add: list[str], resource_names_to_remove: list[str], chunk_size: int) -> None:
    """
    Apply adds and removes to a campaign using the mutator.
    """
    if criteria_to_add:
        for chunk in chunk_list(criteria_to_add, chunk_size):
            campaign_criterion_mutator.add_location_criteria_to_campaign(campaign_id, chunk)
            time.sleep(1)
    if resource_names_to_remove:
        for chunk in chunk_list(resource_names_to_remove, chunk_size):
            campaign_criterion_mutator.remove_location_criteria_from_campaign(campaign_id, chunk)
            time.sleep(1)


def _sync_campaign_criteria(campaign_ids: list[str], api_criteria_ids: list[str], campaign_criterion_ids_map: dict[str, dict[str, str]]) -> None:
    """
    Sync the campaign criteria.
    """
    google_ads_client = _get_google_ads_client()
    google_ads_account_id = EnvironmentService().get_google_ads_account_id()
    campaign_criterion_mutator = CampaignCriterionMutator(google_ads_client, google_ads_account_id)

    for campaign_id in campaign_ids:
        existing_criteria = campaign_criterion_ids_map.get(str(campaign_id), {})
        existing_criteria_ids = set(existing_criteria.keys())

        criteria_to_add = _get_criteria_to_add(api_criteria_ids, existing_criteria_ids)
        criteria_to_remove_ids = _get_criteria_to_remove(api_criteria_ids, existing_criteria_ids)
        resource_names_to_remove = _get_resource_names_to_remove(criteria_to_remove_ids, existing_criteria)

        if EnvironmentService().get_test_mode():
            print(f"Test mode is enabled. Only the first criteria will be added to the campaign.")
            criteria_to_add = criteria_to_add[0:1]
        chunk_size = EnvironmentService().get_chunk_size()
        if EnvironmentService().get_test_mode():
            print(f"Test mode is enabled. Only the first criteria will be removed from the campaign.")
            resource_names_to_remove = resource_names_to_remove[0:1]

        _apply_campaign_criteria_changes(
            campaign_criterion_mutator,
            campaign_id,
            criteria_to_add,
            resource_names_to_remove,
            chunk_size
        )
    
def _get_google_ads_client() -> GoogleAdsClient:
    """
    Get the Google Ads client.
    """
    google_ads_client = GoogleAdsClient()
    client = google_ads_client.get(get_google_ads_api_yaml_path())
    return client