# Check the actual character in current_assignment

from tools.sheets import get_sheet_as_df
import os
from dotenv import load_dotenv

load_dotenv()

spreadsheet_id = os.getenv('SPREADSHEET_ID')
pilots_df = get_sheet_as_df(spreadsheet_id, 'pilot_roster!A:Z')

# Get Arjun's record
arjun = pilots_df[pilots_df['name'] == 'Arjun'].iloc[0]

assignment = arjun['current_assignment']

print(f"Current assignment value: '{assignment}'")
print(f"Type: {type(assignment)}")
print(f"Length: {len(str(assignment))}")
print(f"Repr: {repr(assignment)}")
print(f"Bytes: {assignment.encode('utf-8') if isinstance(assignment, str) else 'N/A'}")
print(f"Ord values: {[ord(c) for c in str(assignment)]}")

# Test the condition
assignment_str = str(assignment).strip()
print(f"\nAfter str().strip(): '{assignment_str}'")
print(f"Is empty?: {not assignment_str}")
print(f"In list?: {assignment_str in ['', '-', '–', 'â€"', 'None', 'none']}")

# Test each character
test_chars = ['', '-', '–', 'â€"', 'None', 'none']
for char in test_chars:
    print(f"  '{char}' == '{assignment_str}': {char == assignment_str}")
