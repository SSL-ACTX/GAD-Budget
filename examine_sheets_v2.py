import zipfile
import xml.etree.ElementTree as ET

def examine_sheet(z, strings, sheet_xml, sheet_name, out_f):
    out_f.write(f"\n--- Examining {sheet_name} ({sheet_xml}) ---\n")
    try:
        with z.open(f"xl/worksheets/{sheet_xml}") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            sheetData = root.find("ns:sheetData", ns)
            
            rows_shown = 0
            for i, row in enumerate(sheetData.findall("ns:row", ns)):
                row_data = []
                for c in row.findall("ns:c", ns):
                    v = c.find("ns:v", ns)
                    val = v.text if v is not None else ""
                    if c.get("t") == "s" and val.isdigit():
                        val = strings[int(val)]
                    row_data.append(val)
                if any(row_data):
                    out_f.write(f"Row {i}: {row_data}\n")
                    rows_shown += 1
                if rows_shown > 20: # Show more rows to be safe
                    break
    except Exception as e:
        out_f.write(f"Error reading {sheet_name}: {e}\n")

if __name__ == "__main__":
    xl_file = "GAD BUDGET MONITORING 2026.xlsx"
    with open("sheet_analysis.txt", "w", encoding="utf-8") as out_f:
        try:
            with zipfile.ZipFile(xl_file) as z:
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

                examine_sheet(z, strings, "sheet4.xml", "SUMMARY", out_f)
                examine_sheet(z, strings, "sheet5.xml", "LBP2-Accounts", out_f)
                examine_sheet(z, strings, "sheet6.xml", "LBP4-AIP-Obligated", out_f)
        except Exception as e:
            out_f.write(f"Global Error: {e}\n")
