from zip_code_service import get_zip_codes
from constants.zips_dict import zips_dict

def main():
    zip_codes = get_zip_codes()
    criteria_ids = [zips_dict[zip_code] for zip_code in zip_codes if zip_code in zips_dict]
    print(criteria_ids)
    
    # update the campaigns with the criteria_ids
    # send slack notifications

if __name__ == "__main__":
    main()