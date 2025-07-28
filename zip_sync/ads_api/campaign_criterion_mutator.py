import logging
from google.ads.googleads.errors import GoogleAdsException

# Configure logging for the module
logger = logging.getLogger(__name__)

class CampaignCriterionMutator:
    """
    Handles the mutation of campaign criteria in the Google Ads API.
    """

    def __init__(self, google_ads_client, customer_id: str):
        """
        Initializes the CampaignCriterionMutator with a Google Ads client and customer ID.

        Args:
            google_ads_client: An initialized GoogleAdsClient instance.
            customer_id (str): The Google Ads customer ID (without dashes).
        """
        self._client = google_ads_client
        self._customer_id = customer_id
        self._campaign_criterion_service = self._client.get_service("CampaignCriterionService")

    def add_location_criteria_to_campaign(self, campaign_id: str, location_criteria_ids: list[str]) -> bool:
        """
        Adds multiple location criteria to a specific campaign.

        Args:
            campaign_id (str): The ID of the campaign to which criteria will be added.
            location_criteria_ids (list[str]): A list of GeoTargeting criteria IDs (e.g., zip codes).

        Returns:
            bool: True if the operation was successful for all criteria, False otherwise.
        """
        operations = []
        for location_id in location_criteria_ids:
            campaign_criterion_operation = self._client.get_type("CampaignCriterionOperation")
            campaign_criterion = campaign_criterion_operation.create
            campaign_criterion.campaign = self._client.to_resource_name("campaign", campaign_id)
            campaign_criterion.location.geo_target_constant = self._client.to_resource_name(
                "geoTargetConstant", location_id
            )
            campaign_criterion.negative = False # Set to True if you want to exclude these locations
            operations.append(campaign_criterion_operation)

        if not operations:
            logger.info(f"No location criteria provided for campaign ID {campaign_id}. Skipping mutation.")
            return True

        try:
            logger.info(f"Attempting to add {len(operations)} location criteria to campaign ID: {campaign_id}")
            response = self._campaign_criterion_service.mutate_campaign_criteria(
                customer_id=self._customer_id, operations=operations
            )
            for result in response.results:
                logger.info(
                    f"Successfully added campaign criterion: {result.resource_name}"
                )
            return True
        except GoogleAdsException as ex:
            logger.error(
                f"Request with ID '{ex.request_id}' failed when adding criteria to campaign {campaign_id} "
                f"with status '{ex.error.code().name}' and includes the following errors:"
            )
            for error in ex.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while mutating campaign criteria for campaign {campaign_id}: {e}")
            return False

