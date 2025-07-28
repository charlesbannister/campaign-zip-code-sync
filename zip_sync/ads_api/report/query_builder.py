

import datetime

GLOBAL_FILTERS = [
	{ "field": 'campaign.experiment_type', "operator": '=', "value": 'BASE' },
	{ "field": 'campaign.status', "operator": '=', "value": 'ENABLED' },
	{ "field": 'campaign.advertising_channel_sub_type', "operator": 'NOT IN', "value": "(SEARCH_EXPRESS, SEARCH_MOBILE_APP)" },
	{ "field": 'campaign.name', "operator": 'NOT REGEXP_MATCH', "value": '"^z-.*"' },
	{ "field": 'campaign.serving_status', "operator": '=', "value": '"SERVING"' },
]

DEFAULT_REPORT_LIMIT = 1000

class QueryBuilder:
    
    def __init__(self, report_name: str):
        """
        Args:
            report_name (str): Google Ads API report name
        """
        self.report_name = report_name
        self.query = "SELECT "

    def with_fields(self, fields: list[str]):
        self.query += ", ".join(fields)
        self.query += f" FROM {self.report_name}"
        return self

    def with_filters(self, filters: list[dict]):
        for filter_dict in filters:  # Assuming 'filters' is a list of dicts
            operator = "AND" if "WHERE" in self.query else "WHERE"
            if not isinstance(filter_dict["value"], str):
                raise ValueError(f"Filter value {filter_dict['value']} must be a string, got {type(filter_dict['value'])}")
            self.query += f" {operator} {filter_dict['field']} {filter_dict['operator']} {filter_dict['value']}"
        return self

    def with_global_filters(self):
        self.with_filters(GLOBAL_FILTERS)
        return self

    def with_limit(self, limit = None):
        limit = limit if limit else DEFAULT_REPORT_LIMIT
        self.query += f" LIMIT {limit}"
        return self

    def during_days(self, days):
        from_date = self._get_date_range(days)
        to_date = self._get_date_range(1)
        operator = "AND" if "WHERE" in self.query else "WHERE"
        self.query += f" {operator} segments.date BETWEEN '{from_date}' AND '{to_date}'"
        return self

    def _get_date_range(self, days):
        date = datetime.date.today() - datetime.timedelta(days=days)
        return date.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD

    def get(self):
        return self.query
