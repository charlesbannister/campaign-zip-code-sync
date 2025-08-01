import logging
from typing import Optional
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.errors.types import GoogleAdsFailure

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
        """Main entry point for criteria mutations."""
        if not operations:
            logger.info(f"No criteria to {operation_type} for campaign ID {campaign_id}. Skipping mutation.")
            return True
        
        logger.info(f"Attempting to {operation_type} {len(operations)} criteria for campaign ID: {campaign_id}")
        
        try:
            result = self._execute_criteria_mutation(operations)
            self._log_mutation_result(result, campaign_id, operation_type)
            return result["success"]
        
        except GoogleAdsException as ex:
            self._handle_ads_exception(ex, campaign_id, operation_type)
            return False
        
        except Exception as ex:
            self._handle_unexpected_exception(ex, campaign_id)
            return False


    def _execute_criteria_mutation(self, operations: list) -> dict:
        """Executes the mutation request and returns structured results."""
        request = self._build_criteria_mutation_request(operations)
        response = self._campaign_criterion_service.mutate_campaign_criteria(request=request)
        
        successful_count = len(response.results)
        total_count = len(operations)
        failed_count = total_count - successful_count
        
        # Log partial failures if any
        self._log_partial_failures(response)
        
        return {
            "success": True,
            "successful_count": successful_count,
            "failed_count": failed_count,
            "total_count": total_count
        }


    def _build_criteria_mutation_request(self, operations: list):
        """Constructs the mutation request with partial failure enabled."""
        request = self._client.get_type("MutateCampaignCriteriaRequest")
        request.customer_id = self._customer_id
        request.operations = operations
        request.partial_failure = True
        return request


    def _log_mutation_result(self, result: dict, campaign_id: str, operation_type: str) -> None:
        """Logs mutation results in a clean, readable format."""
        if result["failed_count"] == 0:
            logger.info(f"Successfully {operation_type}d all {result['successful_count']} criteria for campaign {campaign_id}")
        else:
            logger.info(f"Successfully {operation_type}d {result['successful_count']} criteria for campaign {campaign_id}")
            logger.warning(f"{result['failed_count']} operations failed out of {result['total_count']} total")


    def _log_partial_failures(self, response) -> None:
        """Logs partial failure details in a readable format."""
        if not response.partial_failure_error:
            return
        
        try:
            failure = GoogleAdsFailure.deserialize(response.partial_failure_error.details)
            for error in failure.errors:
                operation_index = self._extract_operation_index(error)
                
                if operation_index is not None:
                    logger.error(f"Operation {operation_index} failed: {error.message}")
                else:
                    logger.error(f"Operation failed: {error.message}")
        
        except Exception:
            logger.warning(f"Could not parse failure details: {response.partial_failure_error.message}")


    def _extract_operation_index(self, error) -> Optional[int]:
        """Extracts the operation index from error location details."""
        if not error.location or not error.location.field_path_elements:
            return None
        
        for element in error.location.field_path_elements:
            if element.field_name == "operations" and element.index is not None:
                return element.index
        
        return None


    def _handle_ads_exception(self, ex: GoogleAdsException, campaign_id: str, operation_type: str) -> None:
        """Handles Google Ads API exceptions with detailed logging."""
        logger.error(
            f"Request '{ex.request_id}' failed when {operation_type}ing criteria for campaign {campaign_id} "
            f"with status '{ex.error.code().name}'"
        )
        
        for error in ex.failure.errors:
            logger.error(f"Error: {error.message}")
            if error.location:
                for field_path in error.location.field_path_elements:
                    logger.error(f"  Field: {field_path.field_name}")


    def _handle_unexpected_exception(self, ex: Exception, campaign_id: str) -> None:
        """Handles unexpected exceptions."""
        logger.error(f"Unexpected error mutating criteria for campaign {campaign_id}: {ex}")