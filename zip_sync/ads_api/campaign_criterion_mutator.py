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
        """
        operations = []
        for location_id in location_criteria_ids:
            campaign_criterion_operation = self._client.get_type("CampaignCriterionOperation")
            create_op = campaign_criterion_operation.create
            create_op.campaign = f"customers/{self._customer_id}/campaigns/{campaign_id}"
            create_op.location.geo_target_constant = f"geoTargetConstants/{location_id}"
            operations.append(campaign_criterion_operation)

        return self._mutate_criteria(campaign_id, operations, "add")
    
    def remove_location_criteria_from_campaign(self, campaign_id: str, resource_names: list[str]) -> bool:
        """
        Removes multiple location criteria from a specific campaign.
        """
        operations = []
        for resource_name in resource_names:
            campaign_criterion_operation = self._client.get_type("CampaignCriterionOperation")
            campaign_criterion_operation.remove = resource_name
            operations.append(campaign_criterion_operation)

        return self._mutate_criteria(campaign_id, operations, "remove")

    def _mutate_criteria(self, campaign_id: str, operations: list, operation_type: str) -> bool:
        """
        Sends a mutate request to the Google Ads API for the given operations.
        """
        if not operations:
            logger.info(f"No criteria to {operation_type} for campaign ID {campaign_id}. Skipping mutation.")
            return True

        try:
            logger.info(f"Attempting to {operation_type} {len(operations)} criteria for campaign ID: {campaign_id}")
            response = self._campaign_criterion_service.mutate_campaign_criteria(
                customer_id=self._customer_id, operations=operations
            )
            for result in response.results:
                logger.info(
                    f"Successfully {operation_type}d campaign criterion: {result.resource_name}"
                )
            return True
        except GoogleAdsException as ex:
            logger.error(
                f"Request with ID '{ex.request_id}' failed when {operation_type}ing criteria for campaign {campaign_id} "
                f"with status '{ex.error.code().name}' and includes the following errors:"
            )
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while mutating campaign criteria for campaign {campaign_id}: {e}")
            return False

