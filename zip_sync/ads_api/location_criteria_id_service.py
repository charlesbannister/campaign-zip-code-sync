import logging
from typing import TYPE_CHECKING, Set

# Use TYPE_CHECKING for type hints to avoid circular imports at runtime
if TYPE_CHECKING:
    from zip_sync.ads_api.google_ads_client import GoogleAdsClientWrapper
    from zip_sync.ads_api.campaign_fetcher import CampaignFetcher
    from zip_sync.ads_api.campaign_criterion_mutator import CampaignCriterionMutator
    from zip_sync.slack.slack_notifier import SlackNotifier

from zip_sync.constants.zips_dict import ZIP_TO_CRITERIA_ID_MAP

# Configure logging for the module
logger = logging.getLogger(__name__)

class LocationCriteriaIdService:
    """
    Manages the synchronization of zip code (location) criteria with Google Ads campaigns.
    This service is designed to receive its dependencies via constructor injection.
    It now handles both adding missing criteria and removing superfluous ones.
    """

    def __init__(
        self,
        google_ads_client_wrapper: 'GoogleAdsClientWrapper',
        campaign_fetcher: 'CampaignFetcher',
        campaign_criterion_mutator: 'CampaignCriterionMutator',
        slack_notifier: 'SlackNotifier'
    ):
        """
        Initializes the LocationCriteriaIdService with its required dependencies.

        Args:
            google_ads_client_wrapper (GoogleAdsClientWrapper): Wrapper for Google Ads API client.
            campaign_fetcher (CampaignFetcher): Service to fetch campaign data.
            campaign_criterion_mutator (CampaignCriterionMutator): Service to mutate campaign criteria.
            slack_notifier (SlackNotifier): Service to send Slack notifications.
        """
        self._google_ads_client_wrapper = google_ads_client_wrapper
        self._customer_id = self._google_ads_client_wrapper.get_login_customer_id()
        self._campaign_fetcher = campaign_fetcher
        self._campaign_criterion_mutator = campaign_criterion_mutator
        self._slack_notifier = slack_notifier
        self._google_ads_client = google_ads_client_wrapper.get_client() # Need client for type generation

    def sync_zip_codes_to_active_campaigns(self):
        """
        Orchestrates the process of adding predefined zip code criteria
        to all active Google Ads campaigns and removing criteria not in the list.
        """
        logger.info("Starting comprehensive zip code synchronization for active campaigns.")

        # Get the set of all desired zip code criteria IDs
        desired_zip_criteria_ids: Set[str] = set(ZIP_TO_CRITERIA_ID_MAP.values())

        if not desired_zip_criteria_ids:
            logger.warning("No desired zip code criteria found in ZIP_TO_CRITERIA_ID_MAP. Skipping operation.")
            self._slack_notifier.send_admin_notification("No desired zip code criteria found in `zips_dict.py`. No changes applied to campaigns.")
            return

        active_campaign_ids = self._campaign_fetcher.get_active_campaign_ids()

        if not active_campaign_ids:
            logger.info("No active campaigns found to update. Exiting.")
            self._slack_notifier.send_admin_notification("No active campaigns found. No zip codes added or removed.")
            return

        updated_campaign_count = 0
        skipped_campaign_count = 0
        errors_during_update = []

        logger.info(
            f"Found {len(active_campaign_ids)} active campaigns. "
            f"Will synchronize with {len(desired_zip_criteria_ids)} desired zip code criteria."
        )

        for campaign_id in active_campaign_ids:
            logger.info(f"Processing campaign ID: {campaign_id}")
            
            existing_criteria_ids: Set[str] = set(
                self._campaign_fetcher.get_campaign_location_criteria_ids(campaign_id)
            )

            # Determine criteria to add
            criteria_to_add = list(desired_zip_criteria_ids - existing_criteria_ids)
            # Determine criteria to remove
            criteria_to_remove = list(existing_criteria_ids - desired_zip_criteria_ids)

            operations = []

            # Create operations for adding new criteria
            for location_id in criteria_to_add:
                logger.debug(f"Adding CREATE operation for location ID {location_id} to campaign {campaign_id}")
                operations.append(self._campaign_criterion_mutator._create_location_criterion_operation(
                    campaign_id, location_id, is_negative=False
                ))

            # Create operations for removing old criteria
            for location_id in criteria_to_remove:
                logger.debug(f"Adding REMOVE operation for location ID {location_id} from campaign {campaign_id}")
                # Note: For removal, the criterion_id in the resource name is the actual GeoTargetConstant ID
                operations.append(self._campaign_criterion_mutator._remove_location_criterion_operation(
                    campaign_id, location_id # Here, location_id is used as criterion_id
                ))

            if not operations:
                logger.info(f"Campaign ID {campaign_id} is already in sync. No mutations needed.")
                skipped_campaign_count += 1
                continue

            logger.info(
                f"Campaign ID {campaign_id}: Preparing to add {len(criteria_to_add)} criteria and "
                f"remove {len(criteria_to_remove)} criteria."
            )

            success = self._campaign_criterion_mutator.mutate_location_criteria(
                campaign_id, operations
            )

            if success:
                updated_campaign_count += 1
                logger.info(f"Successfully synchronized campaign ID: {campaign_id}")
            else:
                errors_during_update.append(campaign_id)
                logger.error(f"Failed to synchronize campaign ID: {campaign_id}")

        notification_message = (
            "Comprehensive Zip code synchronization complete:\n"
            f"- Campaigns successfully updated: {updated_campaign_count}\n"
            f"- Campaigns already in sync (skipped): {skipped_campaign_count}\n"
            f"- Campaigns with errors during update: {len(errors_during_update)} ({', '.join(errors_during_update)})\n"
            f"Total active campaigns processed: {len(active_campaign_ids)}"
        )
        logger.info(notification_message)
        self._slack_notifier.send_admin_notification(notification_message)

