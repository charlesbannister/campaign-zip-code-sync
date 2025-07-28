from zip_sync.data.zip_code_fetcher import ZipCodeFetcher
from zip_sync.filter.zip_code_filter import filter_zip_codes

API_URL = "https://www.elocal.com/api/call_category_price_list/149.json?api_key=c13b178aca3cd7d642b6b1e4fe22f1bb"

def get_zip_codes():
    fetcher = ZipCodeFetcher(API_URL)
    data = fetcher.fetch()
    return filter_zip_codes(data)
