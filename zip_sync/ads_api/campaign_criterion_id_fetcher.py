import logging
from google.ads.googleads.errors import GoogleAdsException
from zip_sync.ads_api.report.get_report import GetReport

# Configure logging for the module
logger = logging.getLogger(__name__)

class CampaignCriterionIdFetcher:
    """
    Fetches campaign criterion data, specifically location (geo-target) IDs,
    for a given list of campaign IDs using the Google Ads API reports.
    """

    def __init__(self, google_ads_client, customer_id: str):
        """
        Initializes the CampaignCriterionIdFetcher.

        Args:
            google_ads_client: An initialized GoogleAdsClient instance.
            customer_id (str): The Google Ads customer ID (without dashes).
        """
        self._client = google_ads_client
        self._customer_id = customer_id

    def get_campaign_location_criteria_for_campaigns(self, campaign_ids: list[str]) -> dict[str, dict[str, str]]:
        """
        Retrieves the location (geo-target) criteria for a list of campaigns.
        These are the locations which are being targeted by the campaigns.

        Args:
            campaign_ids (list[str]): A list of campaign IDs for which to fetch criteria.

        Returns:
            dict[str, dict[str, str]]: A dictionary where keys are campaign IDs (str)
                                      and values are dictionaries mapping location criteria IDs (str)
                                      to their full resource names (str).
        """
        if not campaign_ids:
            logger.info("No campaign IDs provided. Returning an empty dictionary.")
            return {}

        # Format campaign IDs for the IN clause in GAQL
        formatted_campaign_ids = ", ".join([f"'{cid}'" for cid in campaign_ids])

        query = f"""
            SELECT
                campaign.id,
                campaign_criterion.resource_name,
                campaign_criterion.location.geo_target_constant
            FROM
                campaign_criterion
            WHERE
                campaign_criterion.type = 'LOCATION'
                AND campaign.id IN ({formatted_campaign_ids})
        """
        fields = [
            "campaign.id",
            "campaign_criterion.resource_name",
            "campaign_criterion.location.geo_target_constant"
        ]
        campaign_criteria_map: dict[str, dict[str, str]] = {str(cid): {} for cid in campaign_ids}

        logger.info(f"Fetching location criteria for {len(campaign_ids)} campaigns.")
        try:
            get_report_service = GetReport(query, fields, self._customer_id, self._client)
            df = get_report_service.get_df()

            if df.empty:
                logger.info("No location criteria found for the specified campaigns.")
                return campaign_criteria_map

            for _, row in df.iterrows():
                campaign_id = str(row["campaign.id"])
                resource_name = row["campaign_criterion.resource_name"]
                geo_target_constant_resource_name = row["campaign_criterion.location.geo_target_constant"]
                if geo_target_constant_resource_name:
                    location_id = geo_target_constant_resource_name.split('/')[-1]
                    if campaign_id in campaign_criteria_map:
                        campaign_criteria_map[campaign_id][location_id] = resource_name
                    else:
                        campaign_criteria_map[campaign_id] = {location_id: resource_name}
                    logger.debug(f"Found location criterion '{resource_name}' for campaign ID '{campaign_id}'")

            logger.info(f"Finished fetching location criteria for campaigns. Populated map for {len(campaign_criteria_map)} campaigns.")

        except GoogleAdsException as ex:
            logger.error(
                f"Request with ID '{ex.request_id}' failed when fetching campaign criteria "
                f"with status '{ex.error.code().name}' and includes the following errors:"
            )
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return {}
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching campaign criteria: {e}")
            return {}

        return campaign_criteria_map

