# Part of SkyOps Agent system – see README for architecture

"""
This module provides helper functions to interact with Google Sheets.
It is used by the SkyOps Agent as a persistent state store.

Responsibilities:
- Authenticate using a service account
- Read a sheet into a pandas DataFrame
- Write updates back to a sheet

Do NOT include any business logic here.
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
from typing import Optional


# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_sheets_service():
    """
    Authenticate and return a Google Sheets API service instance.
    
    Returns:
        Resource: Google Sheets API service object
    """
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if not os.path.exists(creds_file):
        raise FileNotFoundError(f"Credentials file not found: {creds_file}")
    
    credentials = Credentials.from_service_account_file(
        creds_file, 
        scopes=SCOPES
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    return service


def get_sheet_as_df(spreadsheet_id: str, range_name: str) -> pd.DataFrame:
    """
    Read a Google Sheet and return it as a pandas DataFrame.
    
    Args:
        spreadsheet_id: The ID of the Google Spreadsheet
        range_name: The A1 notation of the range to retrieve (e.g., 'Sheet1!A1:Z')
    
    Returns:
        pd.DataFrame: The sheet data as a DataFrame
    """
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    
    if not values:
        return pd.DataFrame()
    
    # First row is header
    headers = values[0]
    data = values[1:]
    
    df = pd.DataFrame(data, columns=headers)
    return df


def update_sheet_from_df(
    spreadsheet_id: str, 
    range_name: str, 
    df: pd.DataFrame,
    include_header: bool = True
) -> dict:
    """
    Write a pandas DataFrame back to a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the Google Spreadsheet
        range_name: The A1 notation of the range to update (e.g., 'Sheet1!A1')
        df: The DataFrame to write
        include_header: Whether to include column headers in the update
    
    Returns:
        dict: The API response containing update details
    """
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    # Convert DataFrame to list of lists
    if include_header:
        values = [df.columns.tolist()] + df.values.tolist()
    else:
        values = df.values.tolist()
    
    body = {
        'values': values
    }
    
    result = sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return result


def append_to_sheet(
    spreadsheet_id: str,
    range_name: str,
    df: pd.DataFrame
) -> dict:
    """
    Append rows from a DataFrame to a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the Google Spreadsheet
        range_name: The A1 notation of the range to append to (e.g., 'Sheet1!A:Z')
        df: The DataFrame with rows to append
    
    Returns:
        dict: The API response containing append details
    """
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    values = df.values.tolist()
    
    body = {
        'values': values
    }
    
    result = sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
    return result
