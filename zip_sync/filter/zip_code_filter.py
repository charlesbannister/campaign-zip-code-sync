from typing import List, Dict

def is_max_call_price_above_threshold(entry: dict, threshold: float) -> bool:
    try:
        return float(entry.get('max_call_price', 0)) > threshold
    except (TypeError, ValueError):
        return False

def filter_zip_codes(data: List[Dict]) -> List[str]:
    result = []
    for entry in data:
        if is_max_call_price_above_threshold(entry, 20):
            result.append(str(entry.get('zip_code')))
    return result
