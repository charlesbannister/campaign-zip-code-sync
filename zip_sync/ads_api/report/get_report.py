import time
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient 
from zip_sync.ads_api.report.stream_handler import StreamHandler
from zip_sync.ads_api.report.options_enums_mapper import enum_map
from zip_sync.environment.environment_service import EnvironmentService

class GetReport:

    def __init__(self, query, fields, customer_id, google_ads_client: GoogleAdsClient):
        self.query = query
        self.fields = fields
        self.customer_id = customer_id
        self.google_ads_client = google_ads_client

    def get_df(self) -> pd.DataFrame:
        results = self._get_results()
        df = pd.DataFrame.from_records(results)
        df = self._convert_enums_from_integer_to_name(df)
        return df
    
    def _get_results(self, ) -> list[dict]:
        ga_service = self.google_ads_client.get_service("GoogleAdsService")
        customer_id = self.customer_id
        stream = ga_service.search_stream(customer_id=customer_id.replace('-', ''), query=self.query)
        results = []
        for batch in stream:
            fields = batch.field_mask.paths
            for row in batch.results:
                results.append(StreamHandler().row_to_dict(row, fields))
        return results
    
    def _convert_enums_from_integer_to_name(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        for field_name in data_frame.columns[data_frame.columns.isin(enum_map.keys())]:
            data_frame[field_name] = data_frame[field_name].map(enum_map[field_name])
        return data_frame