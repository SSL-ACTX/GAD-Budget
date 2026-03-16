"""
Migration: Drop old budgets table and recreate with the new 20-column schema.
Run once from project root:  python migrate_db.py
"""
import sqlite3
from datetime import datetime

DB = "gad_budget.db"

def iso_now():
    return datetime.utcnow().isoformat(timespec="seconds")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Drop old table
cur.execute("DROP TABLE IF EXISTS budgets")
print("Old table dropped.")

# Create new table
cur.execute("""
CREATE TABLE budgets (
  id                      INTEGER PRIMARY KEY AUTOINCREMENT,
  no                      TEXT,
  date                    TEXT,
  office                  TEXT NOT NULL DEFAULT '',
  status                  TEXT NOT NULL DEFAULT 'Planned',
  particulars             TEXT,
  pow_title               TEXT,
  pow_date_of_activity    TEXT,
  reference_code          TEXT,
  ppa_allotted_budget     REAL NOT NULL DEFAULT 0,
  ppa_description         TEXT,
  accounts                TEXT,
  account_code            TEXT,
  proposed_budget         REAL NOT NULL DEFAULT 0,
  actual_obligation       REAL NOT NULL DEFAULT 0,
  payee                   TEXT,
  caf                     TEXT,
  obligation_number       TEXT,
  venue_food_honorarium   TEXT,
  actual_remaining_budget REAL NOT NULL DEFAULT 0,
  remarks                 TEXT,
  created_at              TEXT NOT NULL
)
""")
print("New table created.")

# Insert seed data
now = iso_now()
seed = [
    ("1","1/7/2026","MGADO","Completed","SALARY & INCENTIVES",None,None,"1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Salaries & Wages-Regular","5-01-01-010",0.00,87592.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-015","SALARY",6899501.24,None,now),
    ("2","1/7/2026","MGADO","Completed","SALARY & INCENTIVES",None,None,"1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Personal Economic Relief Allowance (PERA)","5-01-02-010",0.00,10000.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-015","SALARY",6899501.24,None,now),
    ("3","1/7/2026","MGADO","Completed","SALARY & INCENTIVES",None,None,"1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Retirement and Life Insurance Premiums","5-01-03-010",0.00,21022.08,"PHILIPPINE VETERANS BANK",None,"101-26-01-015","SALARY",6899501.24,None,now),
    ("4","1/7/2026","MGADO","Completed","SALARY & INCENTIVES",None,None,"1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Pag-ibig Contributions","5-01-03-020",0.00,1000.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-015","SALARY",6899501.24,None,now),
    ("5","1/7/2026","MGADO","Completed","SALARY & INCENTIVES",None,None,"1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Employees Compensation Insurance Premiums","5-01-03-040",0.00,500.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-015","SALARY",6899501.24,None,now),
    ("6","1/15/2026","MSWDO","Completed","INCENTIVES FOR THE CHILD DEVELOPMENT WORKERS (CDWs)","INCENTIVES FOR THE CHILD DEVELOPMENT WORKERS (CDWs)","JANUARY","1000-001-3-9-99-001-003-013-001",7200000.00,"Provision of Honoraria for 90 Child Development Center Workers","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",4675000.00,425000.00,"JENIFER EVANGELISTA",None,"101-26-01-75","Honorarium",1675000.00,None,now),
    ("7","1/21/2026","MGADO","Completed","CASH ADVANCE","BARANGAY GAD FOCAL POINT SYSTEM (BGFPS) 1ST MONTHLY MEETING FOR THE YEAR 2026","January 23, 2026","1000-001-3-9-99-001-002-002-001",300000.00,"Barangay GAD Focals","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,24000.00,"REYNAN PARADERO",None,"101-26-01-109","Cash Advance",246750.00,None,now),
    ("8","1/20/2026","MGADO","Completed","MEALS","PROTECT, RESPOND, EMPOWER: RA11313 (SAFE SPACES ACT) & VAWC AWARENESS","February 10, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,83700.00,"MOST HOLY ROSARY MULTI-PURPOSE COOPERATIVE",None,"101-26-02-385","Food",139318.00,"FROM BUDGET (ELLA)",now),
    ("9","1/20/2026","MGADO","Completed","TARPAULIN 1PC - 4X8, 1PC 6X4","PROTECT, RESPOND, EMPOWER: RA11313 (SAFE SPACES ACT) & VAWC AWARENESS","February 10, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Printing and Publication Expenses","5-02-99-020",0.00,1400.00,"MERCEDITA CEBALLOS TRADING",None,None,"Tarpaulin",139318.00,"FROM BUDGET (ELLA)",now),
    ("10","1/20/2026","MGADO","Completed","GLASS FRAME CERTIFICATE (2PC)","PROTECT, RESPOND, EMPOWER: RA11313 (SAFE SPACES ACT) & VAWC AWARENESS","February 10, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Office Supplies Expenses","5-02-03-010",0.00,360.00,"MERCEDITA CEBALLOS TRADING",None,None,"Materials",139318.00,"FROM BUDGET (ELLA)",now),
    ("11","1/20/2026","MGADO","Completed","HANDHELD FAN (150PCS)","PROTECT, RESPOND, EMPOWER: RA11313 (SAFE SPACES ACT) & VAWC AWARENESS","February 10, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Other Supplies and Materials Expenses","5-02-03-990",0.00,115500.00,"MERCEDITA CEBALLOS TRADING",None,None,"Materials",139318.00,"FROM BUDGET (ELLA)",now),
    ("12","1/20/2026","MGADO","Completed","1 GROCERY PACK","PROTECT, RESPOND, EMPOWER: RA11313 (SAFE SPACES ACT) & VAWC AWARENESS","February 10, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,2000.00,"MERCEDITA CEBALLOS TRADING",None,None,"Honorarium",139318.00,"FROM BUDGET (ELLA)",now),
    ("13","1/20/2026","MGADO","Completed","MEALS","SAFE RIDES, SAFE WOMEN: ORIENTATION ON THE SAFE SPACES ACT AND VIOLENCE AGAINST WOMEN FOR TODA DRIVERS","February 12, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,67200.00,"PIONEER BY JAY-EL CATERING SERVICES","-","101-26-02-508","Food",139318.00,"FROM BUDGET (ELLA)",now),
    ("14","1/20/2026","MGADO","Completed","TARPAULIN 1PC - 4X8, 1PC 6X4","SAFE RIDES, SAFE WOMEN: ORIENTATION ON THE SAFE SPACES ACT AND VIOLENCE AGAINST WOMEN FOR TODA DRIVERS","February 12, 2026","1000-001-3-9-99-001-003-004-011",600000.00,"Other Related Trainings","MOOE-Printing and Publication Expenses","5-02-99-020",0.00,1400.00,"MERCEDITA CEBALLOS TRADING",None,None,"Tarpaulin",139318.00,"FROM BUDGET (ELLA)",now),
    ("17","1/13/2026","MGADO","Completed","JOB ORDER SALARY (TECH & LIVELIHOOD)","-","JANUARY 1 - 10, 2026","1000-001-3-9-99-001-001-003-001",1604373.56,"Provision of JO for Women's Crisis and Therapy Facility","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,6500.00,"JENIFER EVANGELISTA",None,"101-26-01-48","SALARY",1373851.14,"FROM BUDGET (ELLA) (TALLY)",now),
    ("18","1/13/2026","MGADO","Completed","JOB ORDER SALARY (GAD)","-","JANUARY 1 - 10, 2026","1000-001-3-9-99-001-001-002-001",1154350.14,"Provision of Salary and incentives for Job Order Personnel","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,10082.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-55","SALARY",1049833.04,"FROM BUDGET (ELLA) (TALLY)",now),
    ("19","1/14/2026","MSWDO","Completed","JOB ORDER SALARY (HOUSEPARENT) (MSWDO)","-","JANUARY 1 - 10, 2026","1000-001-3-9-99-001-001-004-001",1296000.00,"Provision of JO for Bahay Aruga","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,34469.22,"PHILIPPINE VETERANS BANK",None,"101-26-01-56","SALARY",959566.78,"FROM BUDGET (ELLA) (TALLY)",now),
    ("20","1/13/2026","MGADO","Completed","JOB ORDER SALARY (TECH & LIVELIHOOD)","-","JANUARY 1 - 10, 2026","1000-001-3-9-99-001-001-003-001",1604373.56,"Provision of JO for Women's Crisis and Therapy Facility","MOOE-Other Maintenance and Operating Expenses","5-02-99-990",0.00,19527.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-58","SALARY",1373851.14,"FROM BUDGET (ELLA) (TALLY)",now),
    ("21","1/21/2026","MGADO","Completed","SALARY & INCENTIVES","-","JANUARY 16 - 31, 2026","1000-001-3-9-99-001-001-001-001",7769794.00,"Provision of Permanent","PS-Salaries & Wages-Regular","5-01-01-010",0.00,87592.00,"PHILIPPINE VETERANS BANK",None,"101-26-01-138","SALARY",6899501.24,None,now),
    ("23","1/13/2026","MSWDO","Completed","JOB ORDER SALARY (PSYCHIATRIST) (HRMO)","-","JANUARY 1 - 10, 2026","1000-001-3-9-99-001-001-005-001",360000.00,"Provision of Honoraria for Psychologist/Psychiatrist","MOOE-Other Professional Services","5-02-11-990",0.00,10000.00,"JENIFER EVANGELISTA",None,"101-26-01-46","SALARY",270000.00,"FROM BUDGET (ELLA) (TALLY)",now),
]

cur.executemany("""
INSERT INTO budgets (
  no, date, office, status, particulars,
  pow_title, pow_date_of_activity, reference_code,
  ppa_allotted_budget, ppa_description,
  accounts, account_code,
  proposed_budget, actual_obligation,
  payee, caf, obligation_number,
  venue_food_honorarium, actual_remaining_budget,
  remarks, created_at
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", seed)

conn.commit()
conn.close()
print(f"Migration complete. {len(seed)} seed records inserted.")
