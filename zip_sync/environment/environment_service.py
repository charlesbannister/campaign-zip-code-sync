# coding: utf-8
import os

class EnvironmentService(object):

    """
    * Load data from the master .env file and the environment specific .env file e.g. .env.local
    * Create utility properties for the environment variables
    """

    def __init__(self):
        pass
    
    def get_google_ads_account_id(self):
        account_id = os.getenv("GOOGLE_ADS_ACCOUNT_ID", None)
        if account_id is None:
            raise ValueError("GOOGLE_ADS_ACCOUNT_ID is not set")
        return account_id
    
    def get_chunk_size(self) -> int:
        chunk_size = os.getenv("CHUNK_SIZE", "10")
        return int(chunk_size)
    
    def get_api_active(self) -> bool:
        api_active = os.getenv("API_ACTIVE", "true")
        return api_active.lower() == "true"
    
    def get_test_mode(self) -> bool:
        test_mode = os.getenv("TEST_MODE", "false")
        return test_mode.lower() == "true"
    
    def get_google_sheet_url(self) -> str:
        google_sheet_url = os.getenv("GOOGLE_SHEET_URL", None)
        if google_sheet_url is None:
            raise ValueError("GOOGLE_SHEET_URL is not set")
        return google_sheet_url