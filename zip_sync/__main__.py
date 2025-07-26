from zip_code_service import get_zip_codes
from constants.zips_dict import zips_dict
from environment.load_environment_variables import load_environment_variables
from slack.send_admin_slack import send_admin_slack

def main():
    load_environment_variables()
    send_admin_slack("Starting campaign zip code sync")
    zip_codes = get_zip_codes()
    criteria_ids = [zips_dict[zip_code] for zip_code in zip_codes if zip_code in zips_dict]
    print(criteria_ids)
    
    # update the campaigns with the criteria_ids
    # send slack notifications
    send_admin_slack("Successfully updated campaigns with zip codes")

if __name__ == "__main__":
    main()