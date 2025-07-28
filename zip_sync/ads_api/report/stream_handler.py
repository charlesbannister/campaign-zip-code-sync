import inspect
from google.ads.googleads.v20.services.types.google_ads_service import GoogleAdsRow


class StreamHandler:

    def row_to_dict(self, row: GoogleAdsRow, fields: dict[str, list]):
        """tbd"""
        split_fields_dict = self._split_fields(fields)
        output = {}
        for field, split_field in split_fields_dict.items():
            value = row
            for attribute in split_field:
                value = self._get_attribute(value, attribute)
                if value is None:
                    break
            if value is not None and hasattr(value, "value"):
                value = value.value
            output[field] = value
        return output
    
    def _get_attribute(self, value, attribute):
        if attribute != 'type':
            return getattr(value, attribute, None)
        if hasattr(value, 'type_'):
            return getattr(value, 'type_', None)
        return getattr(value, 'type', None)
        
    def _split_fields(self, fields: list) -> dict[str, list]:
        return {field: field.split(".") for field in fields}