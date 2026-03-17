import zipfile
import xml.etree.ElementTree as ET

def get_mapping(filename):
    with zipfile.ZipFile(filename) as z:
        # 1. Map rId to Target (xml file)
        rels_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
        with z.open("xl/_rels/workbook.xml.rels") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            rid_to_target = {}
            for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rid_to_target[rel.get('Id')] = rel.get('Target').split('/')[-1]

        # 2. Map Name to rId
        main_ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                   'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        with z.open("xl/workbook.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            name_to_xml = {}
            for sheet in root.find('main:sheets', main_ns):
                name = sheet.get('name')
                rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                name_to_xml[name] = rid_to_target[rid]
            
            print("Mapping:")
            for name, xml in name_to_xml.items():
                print(f"{name} -> {xml}")
        
        # 3. Peek at MONITORING
        if "MONITORING" in name_to_xml:
            xml_file = name_to_xml["MONITORING"]
            print(f"\nPeeking at {xml_file} (MONITORING):")
            
            strings = []
            try:
                with z.open("xl/sharedStrings.xml") as f:
                    tree = ET.parse(f)
                    s_root = tree.getroot()
                    s_ns = {'ns': s_root.tag.split('}')[0].strip('{')}
                    for si in s_root.findall('ns:si', s_ns):
                        ts = [t.text for t in si.iter(f"{{{s_ns['ns']}}}t")]
                        strings.append("".join(filter(None, ts)))
            except KeyError:
                pass

            with z.open(f"xl/worksheets/{xml_file}") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ns': root.tag.split('}')[0].strip('{')}
                sheetData = root.find("ns:sheetData", ns)
                
                for i, row in enumerate(sheetData.findall("ns:row", ns)):
                    row_data = []
                    for c in row.findall("ns:c", ns):
                        v = c.find("ns:v", ns)
                        if v is not None:
                            val = v.text
                            if c.get("t") == "s":
                                val = strings[int(val)]
                            row_data.append(val)
                        else:
                            row_data.append(None)
                    
                    print(f"Row {i+1}: {row_data}")
                    if i > 20: break

if __name__ == "__main__":
    get_mapping("GAD BUDGET MONITORING 2026.xlsx")
