import logging
from google.ads.googleads.errors import GoogleAdsException
from zip_sync.ads_api.report.get_report import GetReport # Import your existing GetReport class

# Configure logging for the module
logger = logging.getLogger(__name__)

class CampaignFetcher:
    """
    Fetches campaign data from the Google Ads API using the GetReport class.
    """

    def __init__(self, google_ads_client, customer_id: str):
        """
        Initializes the CampaignFetcher with a Google Ads client and customer ID.

        Args:
            google_ads_client: An initialized GoogleAdsClient instance.
            customer_id (str): The Google Ads customer ID (without dashes).
        """
        self._client = google_ads_client
        self._customer_id = customer_id

    def get_active_campaign_ids(self) -> list[str]:
        """
        Retrieves the IDs of all active campaigns under the configured customer ID
        by utilizing the GetReport service.

        Returns:
            list[str]: A list of active campaign IDs.
        """
        query = """
            SELECT
                campaign.id,
                campaign.name
            FROM
                campaign
            WHERE
                campaign.status = 'ENABLED'
            ORDER BY
                campaign.id
        """
        active_campaign_ids = []

        logger.info(f"Fetching active campaigns for customer ID: {self._customer_id} using GetReport.")
        try:
            fields = ["campaign.id", "campaign.name"]
            get_report_service = GetReport(query, fields, self._customer_id, self._client)
            # Use the GetReport service to execute the query
            df = get_report_service.get_df()

            active_campaign_ids = df["campaign.id"].tolist()
            logger.info(f"Finished fetching active campaigns. Found {len(active_campaign_ids)} active campaigns.")

        except GoogleAdsException as ex:
            logger.error(
                f"Request with ID '{ex.request_id}' failed with status "
                f"'{ex.error.code().name}' and includes the following errors:"
            )
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching campaigns using GetReport: {e}")
            return []

        return active_campaign_ids

