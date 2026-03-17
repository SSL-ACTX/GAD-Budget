import zipfile
import xml.etree.ElementTree as ET

def list_sheets(filename):
    try:
        with zipfile.ZipFile(filename) as z:
            with z.open("xl/workbook.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                # Namespaces can vary, let's find the 'sheets' element
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheets = root.find("main:sheets", ns)
                if sheets is not None:
                    print("Sheets in the workbook:")
                    for sheet in sheets:
                        name = sheet.get("name")
                        rId = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                        sheetId = sheet.get("sheetId")
                        print(f"- {name} (rId: {rId}, sheetId: {sheetId})")
                else:
                    print("Could not find sheets in workbook.xml")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sheets("GAD BUDGET MONITORING 2026.xlsx")
