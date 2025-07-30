import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

class SheetsService:
    def __init__(self, credentials_path: str, spreadsheet_url: str):
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url

    def authorize(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        return gspread.authorize(credentials)
    
    def get_spreadsheet(self,):
        """
        Gets and returns a spreadsheet instance based on a spreadsheet url
        """
        def method():
            gc = self.authorize()
            ss = gc.open_by_url(self.spreadsheet_url)

            return ss
        
        ss = self._try_spreadsheet_method(method)

        return ss
    
    def _try_spreadsheet_method(self, method):

        """
        * We may hit spreadsheet errors in which case we want to try again
        * The error will be either a quota error or a temporary API issue
        * We'll raise the error if the method can't run after N tries or if it's not a spreadsheet error we'd expect
        * Utilising "exponential backoff" as per Google's recommendation
        """

        tries = 10
        for i in range(tries):
            try:
                return method()

            except Exception as e:
                if i==tries-1:
                    raise e
                if self._is_spreadsheet_error(e):
                    print("Spreadsheet error. Waiting and trying again.")
                    time.sleep((int(i)+1)*3)
                else:
                    print(str(e))
                    raise e
                
    #catch certain spreadsheet errors as we may want to try again
    def _is_spreadsheet_error(self, e):
        e = str(e)
        if str(e).find("RESOURCE_EXHAUSTED")>-1:
            return True
        if str(e).find("UNAVAILABLE")>-1:
            return True
        if str(e).find("APIError")>-1:
            return True
            
        #for this error: AttributeError: 'NoneType' object has no attribute 'open_by_url'
        #it's where a connection couldn't be made, so we want to try again
        if str(e).find("open_by_url")>-1:
            return True

        return False
    
    def is_valid_google_sheet_url(self, url):
        return url.find('https://docs.google.com/spreadsheets/') > -1

    def update_column(self, worksheet_name: str, values: list, column: int = 1, start_row: int = 2):
        """
        Updates a column in the specified worksheet with the provided values, starting from start_row.
        Args:
            worksheet_name (str): The name of the worksheet/tab.
            values (list): List of values to write (one per row).
            column (int): Column number (1 = A, 2 = B, ...).
            start_row (int): Row number to start writing (default 2).
        """
        def method():
            ss = self.get_spreadsheet()
            worksheet = ss.worksheet(worksheet_name)
            col_letter = chr(ord('A') + column - 1)
            end_row = start_row + len(values) - 1
            cell_range = f"{col_letter}{start_row}:{col_letter}{end_row}"
            # gspread expects a list of lists for update
            value_matrix = [[v] for v in values]
            worksheet.update(cell_range, value_matrix)
        self._try_spreadsheet_method(method)

    def get_worksheet_names(self):
        """
        Returns a list of all worksheet/tab names in the spreadsheet.
        """
        def method():
            ss = self.get_spreadsheet()
            return [ws.title for ws in ss.worksheets()]
        return self._try_spreadsheet_method(method)
