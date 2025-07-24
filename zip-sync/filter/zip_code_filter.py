from typing import List, Dict

def filter_zip_codes(data: List[Dict]) -> List[str]:
    result = []
    for entry in data:
        try:
            max_call_price = float(entry.get('max_call_price', 0))
            if max_call_price > 20:
                result.append(str(entry.get('zip_code')))
        except (TypeError, ValueError):
            continue
    return result
