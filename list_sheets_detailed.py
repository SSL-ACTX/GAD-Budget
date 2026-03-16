import zipfile
import xml.etree.ElementTree as ET

def list_sheets_detailed(filename):
    try:
        with zipfile.ZipFile(filename) as z:
            with z.open("xl/workbook.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {
                    'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                }
                sheets = root.find("main:sheets", ns)
                if sheets is not None:
                    print("Sheet details:")
                    for sheet in sheets:
                        name = sheet.get("name")
                        sheet_id = sheet.get("sheetId")
                        r_id = sheet.get(f"{{{ns['r']}}}id")
                        print(f"Name: {name}, sheetId: {sheet_id}, rId: {r_id}")
                else:
                    print("Could not find sheets in workbook.xml")
            
            # Also list files in xl/worksheets/ to match rId
            print("\nFiles in xl/worksheets/:")
            for name in z.namelist():
                if name.startswith("xl/worksheets/"):
                    print(f"- {name}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sheets_detailed("GAD BUDGET MONITORING 2026.xlsx")
