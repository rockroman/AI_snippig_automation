from google.oauth2.service_account import Credentials
from datetime import datetime 
from datetime import timedelta 
import gspread
import sys
import os


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    
    ]

# Determine the base path for the executable
if getattr(sys, 'frozen', False):
    # Running in a bundled environment
    base_path = sys._MEIPASS
else:
    # Running in a normal environment
    base_path = os.path.dirname(__file__)


class Worksheet:
    """
    google sheet class that handles updates
    based on passed values from other 2 classes
    """
    def __init__(self, SCOPE: list, credentials_path: str, sheet_name: str) -> None:
        self.CREDS = Credentials.from_service_account_file(credentials_path)
        self.SCOPED_CREDS = self.CREDS.with_scopes(SCOPE)
        self.GSPREAD_CLIENT = gspread.authorize(self.SCOPED_CREDS)
        self.SHEET = self.GSPREAD_CLIENT.open(sheet_name)
        self.worksheet = self.SHEET.sheet1
        
        
    def find_empty_cells_and_write_values(self,sheet, column_letters, values):
        """
        Finds empty cells in specified columns and writes values to them.
        """
        # Check if there are more columns than values
        print("length of column letters ",column_letters)
        print("length of values ",values)
        if len(column_letters) > len(values):
            raise ValueError("More columns than values provided. Please provide enough values for each column.")

        for i, column_letter in enumerate(column_letters):
            # Determine the column index (1-based index for gspread)
            col_index = ord(column_letter) - ord('A') + 1

            # Get all values in the column
            column_values = sheet.col_values(col_index)


            # Find the first empty cell
            empty_cell_index = len(column_values) + 1  # Default to the next row if all cells are filled

            # Update the first empty cell with the corresponding value
            cell_address = f'{column_letter}{empty_cell_index}'

            
            # Update cell with the value
            sheet.update(cell_address, [[values[i]]])

            print(f'Updated {cell_address} with value: {values[i]}')


    def update_date(self):
        """
        setting the date one week in advance
        (requirements of specific use case)
         
        """
        column_values = self.worksheet.col_values(1)

        last_filled_cell = len(column_values)
        
        first_empty_cell = len(column_values) + 1 
        print(first_empty_cell)
        current = self.worksheet.acell(f"A{last_filled_cell}").value
        date_format = '%d/%m/%Y'
        
        # Parse the date from the sheet
        current_sheet_date = datetime.strptime(current, date_format)
        
        new_date = current_sheet_date + timedelta(days=7)
        
        # Convert back to 'DD/MM/YYYY' format
        formatted_new_date = new_date.strftime(date_format)
        
        # update sheet with new date
        self.worksheet.update(range_name=f"A{first_empty_cell}",values=[[formatted_new_date]] )