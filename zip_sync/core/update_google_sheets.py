from zip_sync.sheets.sheets_service import SheetsService
from zip_sync.environment.folder_paths import get_google_credentials_path
from zip_sync.environment.environment_service import EnvironmentService

def update_google_sheets(criteria_ids: list[str]) -> None:
    spreadsheet_url = EnvironmentService().get_google_sheet_url()
    sheets_service = SheetsService(get_google_credentials_path(), spreadsheet_url)
    sheets_service.authorize()

    worksheet_names = sheets_service.get_worksheet_names()
    for worksheet_name in worksheet_names:
        sheets_service.update_column(worksheet_name, criteria_ids, column=1, start_row=2)
    
    