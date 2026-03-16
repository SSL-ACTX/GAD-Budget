import zipfile
import xml.etree.ElementTree as ET

def read_xlsx(filename):
    try:
        with zipfile.ZipFile(filename) as z:
            strings = []
            try:
                with z.open("xl/sharedStrings.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    for si in root.findall('ns:si', ns):
                        ts = [t.text for t in si.iter(f"{{{ns['ns']}}}t")]
                        strings.append("".join(filter(None, ts)))
            except KeyError:
                pass

            with z.open("xl/worksheets/sheet1.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheetData = root.find("ns:sheetData", ns)
                
                for i, row in enumerate(sheetData.findall("ns:row", ns)):
                    row_data = []
                    for c in row.findall("ns:c", ns):
                        v = c.find("ns:v", ns)
                        val = v.text if v is not None else ""
                        if c.get("t") == "s" and val.isdigit():
                            val = strings[int(val)]
                        row_data.append(val)
                    if any(row_data):
                        print(f"Row {i}: {row_data}")
                    if i > 50:
                        break
    except Exception as e:
        print("Error:", e)

read_xlsx("GAD BUDGET MONITORING 2026.xlsx")
