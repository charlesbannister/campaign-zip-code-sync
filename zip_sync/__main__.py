import traceback

from zip_sync.constants.zips_dict import zips_dict
from zip_sync.core.update_campaigns import update_campaigns
from zip_sync.core.update_google_sheets import update_google_sheets
from zip_sync.environment.load_environment_variables import \
    load_environment_variables
from zip_sync.slack.send_admin_slack import send_admin_slack
from zip_sync.zip_code_service import get_zip_codes


def main():
    try:
        load_environment_variables()
        send_admin_slack("Starting campaign zip code sync")
        zip_codes = get_zip_codes()
        criteria_ids = [zips_dict[zip_code] for zip_code in zip_codes if zip_code in zips_dict]
        update_google_sheets(criteria_ids)
        update_campaigns(criteria_ids)
    except Exception as e:
        send_admin_slack(f"Error updating campaigns with zip codes: {e}\nFull traceback:\n{traceback.format_exc()}")
        raise e
    finally:
        send_admin_slack("Finished campaign zip code sync")

if __name__ == "__main__":
    main()