from zip_sync.zip_code_service import get_zip_codes
from zip_sync.constants.zips_dict import zips_dict
from zip_sync.environment.load_environment_variables import load_environment_variables
from zip_sync.slack.send_admin_slack import send_admin_slack
from zip_sync.ads_api.google_ads_client import GoogleAdsClient
from zip_sync.environment.folder_paths import get_google_ads_api_yaml_path
from zip_sync.ads_api.report.get_report import GetReport
from zip_sync.core.update_campaigns import update_campaigns

def main():
    load_environment_variables()
    send_admin_slack("Starting campaign zip code sync")
    zip_codes = get_zip_codes()
    criteria_ids = [zips_dict[zip_code] for zip_code in zip_codes if zip_code in zips_dict]
    # print(criteria_ids)
    
    update_campaigns(criteria_ids)
    # update the campaigns with the criteria_ids
    # send slack notifications
    send_admin_slack("Successfully updated campaigns with zip codes")

if __name__ == "__main__":
    main()