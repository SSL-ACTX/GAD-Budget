import openpyxl

def list_sheets(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        print(f"Sheets in {file_path}:")
        for sheet in wb.sheetnames:
            print(f"- {sheet}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sheets("GAD BUDGET MONITORING 2026.xlsx")
