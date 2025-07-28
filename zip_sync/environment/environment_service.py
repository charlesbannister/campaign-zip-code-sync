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