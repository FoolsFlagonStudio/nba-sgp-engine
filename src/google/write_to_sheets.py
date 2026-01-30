import gspread


def write_straights_to_sheet(creds, spreadsheet_id, worksheet_name, df):
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(spreadsheet_id)
    ws = sheet.worksheet(worksheet_name)

    # Clear everything except header row
    ws.batch_clear([f"A2:Z1000"])

    # Convert DF to rows (NO headers)
    rows = df.values.tolist()

    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")