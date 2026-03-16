"""
Migration: Recreate all tables with the full schema.
Run once from project root:  python migrate_db.py
"""
import sqlite3
from datetime import datetime

DB = "gad_budget.db"

def iso_now():
    return datetime.utcnow().isoformat(timespec="seconds")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# ───────────────────────────────────────────────
# 1. MONITORING (existing budgets table)
# ───────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS budgets")
print("Old budgets table dropped.")

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
print("budgets table created.")

now = iso_now()
budget_seed = [
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
""", budget_seed)
print(f"  {len(budget_seed)} budget records inserted.")

# ───────────────────────────────────────────────
# 2. OFFICE SUMMARY (from SUMMARY sheet)
# ───────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS office_summary")
print("Old office_summary table dropped.")

cur.execute("""
CREATE TABLE office_summary (
  id                    INTEGER PRIMARY KEY AUTOINCREMENT,
  office                TEXT NOT NULL,
  budget_threshold      REAL NOT NULL DEFAULT 0,
  obligated             REAL NOT NULL DEFAULT 0,
  earnmarked            REAL NOT NULL DEFAULT 0,
  expenses              REAL NOT NULL DEFAULT 0,
  balance               REAL NOT NULL DEFAULT 0,
  utilization_pct       REAL NOT NULL DEFAULT 0
)
""")
print("office_summary table created.")

summary_seed = [
    ("MSWDO",  20904326.88, 1440955.64, 6806629.00, 8247584.64, 12656742.24, 0.394539594),
    ("MTLVESDC", 4035209.48,  240800.00,  649738.00,  890538.00,  3144671.48, 0.2206918883),
    ("MGAD",   35964144.14, 1692993.86, 2243434.75, 3936428.61, 32027715.53, 0.1094542552),
    ("PESO",     925000.00,   18000.00,  214175.00,  232175.00,   692825.00, 0.251),
    ("PDAO",    2500000.00,       0.00,       0.00,       0.00,  2500000.00, 0.0),
    ("MPO",      690000.00,       0.00,  197700.00,  197700.00,   492300.00, 0.2865217391),
    ("BJMP",    1079500.00,       0.00,       0.00,       0.00,  1079500.00, 0.0),
    ("MHO",     9400000.00,    5635.00,  266245.00,  271880.00,  9128120.00, 0.02892340426),
    ("HRMO",    3410000.00,  366000.00,  285486.00,  651486.00,  2758514.00, 0.1910516129),
    ("MAO",     2000000.00,       0.00,  199894.00,  199894.00,  1800106.00, 0.099947),
    ("MEDO",    8700000.00,       0.00,       0.00,       0.00,  8700000.00, 0.0),
    ("LCW",      900000.00,       0.00,       0.00,       0.00,   900000.00, 0.0),
    ("MTO",     2850000.00,       0.00,       0.00,       0.00,  2850000.00, 0.0),
]

cur.executemany("""
INSERT INTO office_summary (
  office, budget_threshold, obligated, earnmarked, expenses, balance, utilization_pct
) VALUES (?,?,?,?,?,?,?)
""", summary_seed)
print(f"  {len(summary_seed)} office_summary records inserted.")

# ───────────────────────────────────────────────
# 3. EXPENDITURES (from LBP2-Accounts sheet)
# ───────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS expenditures")
print("Old expenditures table dropped.")

cur.execute("""
CREATE TABLE expenditures (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  no              TEXT,
  object_name     TEXT NOT NULL,
  account_code    TEXT,
  allotted_budget REAL NOT NULL DEFAULT 0,
  earnmarked      REAL NOT NULL DEFAULT 0,
  actual_obligated REAL NOT NULL DEFAULT 0,
  expenses_total  REAL NOT NULL DEFAULT 0,
  balance_budget  REAL NOT NULL DEFAULT 0
)
""")
print("expenditures table created.")

expenditure_seed = [
    ("1",  "PS-Salaries & Wages-Regular",                                                "5-01-01-010",    4957200.00,       0, 700736,    700736,    4256464),
    ("2",  "PS-Personal Economic Relief Allowance (PERA)",                                "5-01-02-010",     360000.00,       0,  40000,     40000,     320000),
    ("3",  "PS-Representation Allowance (RA)",                                            "5-01-02-020",      91800.00,       0,  11475,     11475,      80325),
    ("4",  "PS-Transportation Allowance (TA)",                                            "5-01-02-030",      91800.00,       0,  11475,     11475,      80325),
    ("5",  "PS-Clothing and Uniform Allowance",                                           "5-01-02-040",     105000.00,       0,      0,         0,     105000),
    ("6",  "PS-Year End Bonus",                                                           "5-01-02-140",     413100.00,       0,      0,         0,     413100),
    ("7",  "PS-Cash Gift",                                                                "5-01-02-150",      75000.00,       0,      0,         0,      75000),
    ("8",  "PS-Other Bonuses and Allowances",                                             "5-01-02-990",     413100.00,       0,      0,         0,     413100),
    ("9",  "PS-Retirement and Life Insurance Premiums",                                   "5-01-03-010",     594864.00,       0, 84088.32, 84088.32,  510775.68),
    ("10", "PS-Pag-ibig Contributions",                                                  "5-01-03-020",      36000.00,       0,   3000,      3000,      33000),
    ("11", "PS-Philhealth Contributions",                                                "5-01-03-030",     123930.00,       0, 17518.44, 17518.44,  106411.56),
    ("12", "PS-Employees Compensation Insurance Premiums",                               "5-01-03-040",      18000.00,       0,   2000,      2000,      16000),
    ("13", "PS-Other Personnel Benefits",                                                "5-01-04-990",     490000.00,       0,      0,         0,     490000),
    ("14", "MOOE-Traveling Expenses-Local",                                              "5-02-01-010",     300000.00,       0,      0,         0,     300000),
    ("15", "MOOE-Training Expenses",                                                     "5-02-02-010",     170000.00,       0,      0,         0,     170000),
    ("16", "MOOE-Office Supplies Expenses",                                              "5-02-03-010",    4985520.41, 444914.67, 133143, 578057.67, 4407462.74),
    ("17", "MOOE-Semi-Expendable Machinery & Equipment Expenses(Office Equipment)",      "5-02-03-210(02)",  316680.00, 66717,       0,     66717,     249963),
    ("18", "MOOE-Semi-Expendable Machinery & Equipment Expenses(ICT)",                   "5-02-03-210(03)",  300000.00,     0,       0,         0,     300000),
    ("19", "MOOE-Semi-Expendable Machinery & Equipment Expenses(Other Machinery and Equipment)", "5-02-03-210(99)", 158016.00, 248391,  0,    248391,    -90375),
    ("20", "MOOE-Printing and Publication Expenses",                                     "5-02-99-020",     200000.00,       0,   2800,      2800,     197200),
    ("21", "MOOE-Representation Expenses",                                               "5-02-99-030",     200000.00,       0,      0,         0,     200000),
    ("22", "MOOE-Rent/Lease Expenses",                                                   "5-02-04-010",     120000.00,       0,      0,         0,     120000),
    ("23", "MOOE-Other Professional Services",                                           "5-02-11-990",     860000.00,       0, 100000,    100000,     760000),
    ("24", "MOOE-Other Maintenance and Operating Expenses",                              "5-02-99-990",   44199890.09, 10337649.11, 2929131.24, 13266780.35, 30933109.74),
    ("25", "MOOE-Other Supplies and Materials Expenses",                                 "5-02-03-990",    5000000.00,       0, 115500,    115500,    4884500),
    ("26", "CO-Machinery and Equipment Outlay",                                          "5-06-05-020",    7140000.00,       0,      0,         0,    7140000),
]

cur.executemany("""
INSERT INTO expenditures (
  no, object_name, account_code, allotted_budget, earnmarked,
  actual_obligated, expenses_total, balance_budget
) VALUES (?,?,?,?,?,?,?,?)
""", expenditure_seed)
print(f"  {len(expenditure_seed)} expenditure records inserted.")

# ───────────────────────────────────────────────
# 4. AIP PROGRAMS (from LBP4-AIP-Obligated sheet)
# ───────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS aip_programs")
print("Old aip_programs table dropped.")

cur.execute("""
CREATE TABLE aip_programs (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  ref_code           TEXT,
  office             TEXT,
  description        TEXT NOT NULL,
  ps_budget          REAL NOT NULL DEFAULT 0,
  mooe_budget        REAL NOT NULL DEFAULT 0,
  co_budget          REAL NOT NULL DEFAULT 0,
  total_budget       REAL NOT NULL DEFAULT 0,
  earnmarked         REAL NOT NULL DEFAULT 0,
  obligated          REAL NOT NULL DEFAULT 0,
  expenses           REAL NOT NULL DEFAULT 0,
  balance            REAL NOT NULL DEFAULT 0,
  status             TEXT,
  utilization_pct    REAL NOT NULL DEFAULT 0,
  quarterly_schedule TEXT,
  is_header          INTEGER NOT NULL DEFAULT 0
)
""")
print("aip_programs table created.")

aip_seed = [
    # Headers / section titles (is_header=1)
    (None, None, "GENDER AND DEVELOPMENT PROGRAM", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001", None, "GENERAL ADMINISTRATIVE SUPPORT", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-001-001-000", None, "Operation of GAD Office Program", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    # Data rows
    ("1000-001-3-9-99-001-001-001-001", "MGAD", "Provision of Permanent", 7769794.00, 0, 0, 7769794.00, 0, 870292.76, 870292.76, 6899501.24, "Under Utilized", 0.1120097598, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-001-002-000", None, "Staff Supervision", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-001-002-001", "MGAD", "Provision of Salary and incentives for Job Order Personnel", 0, 1154350.14, 0, 1154350.14, 0, 104517.10, 104517.10, 1049833.04, "Under Utilized", 0.09054193903, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-001-003-000", None, "Women's Protection Program", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-001-003-001", "MSWDO", "Provision of JO for Women's Crisis and Therapy Facility", 0, 1604373.56, 0, 1604373.56, 0, 230522.42, 230522.42, 1373851.14, "Under Utilized", 0.1436837565, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-001-004-000", None, "Rehabilitation and Protection for Children- Bahay Aruga Facility", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-001-004-001", "MSWDO", "Provision of JO for Bahay Aruga", 0, 1296000.00, 0, 1296000.00, 0, 336433.22, 336433.22, 959566.78, "Under Utilized", 0.259593534, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-001-005-000", None, "Establishment of Mental Crisis Therapy with provision of medicine", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-001-005-001", "HRMO", "Provision of Honoraria for Psychologist/Psychiatrist", 0, 360000.00, 0, 360000.00, 0, 90000, 90000, 270000, "Under Utilized", 0.25, "1Q - 4Q", 0),
    # Client-focused section
    (None, None, "CLIENT-FOCUSED", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    (None, None, "OPERATION SERVICES", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-002-000-000", None, "II. FACILITATION OF GAD MANDATE PROGRAM", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-002-001-000", None, "Establishment of Mental Crisis Therapy with provision of medicine", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-002-001-001", "MGAD", "Provision of Prescribed Medicine for Clientelle", 0, 500000.00, 0, 500000.00, 0, 0, 0, 500000, "Unspent Funds", 0, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-002-002-000", None, "Facilitation of GAD Mandate", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-002-002-001", "MGAD", "Barangay GAD Focals", 0, 300000.00, 0, 300000.00, 0, 24000, 24000, 246750, "Under Utilized", 0.08, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-003-000-000", None, "III. ORGANIZATION FOCUSED PROGRAM", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-003-001-000", None, "Livelihood Development Program", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-003-001-001", "MGAD", "Provision of Livelihood Programs", 0, 1500000.00, 0, 1500000.00, 0, 0, 0, 1500000, "Unspent Funds", 0, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-003-004-000", None, "Advocacy and Awareness", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-003-004-011", "MGAD", "Other Related Trainings", 0, 600000.00, 0, 600000.00, 0, 271560, 271560, 139318, "Under Utilized", 0.4526, "1Q - 4Q", 0),
    ("1000-001-3-9-99-001-003-013-000", None, "CDW Incentives Program", 0, 0, 0, 0, 0, 0, 0, 0, None, 0, None, 1),
    ("1000-001-3-9-99-001-003-013-001", "MSWDO", "Provision of Honoraria for 90 Child Development Center Workers", 0, 7200000.00, 0, 7200000.00, 4675000, 425000, 5100000, 1675000, "Under Utilized", 0.7083333, "1Q - 4Q", 0),
]

cur.executemany("""
INSERT INTO aip_programs (
  ref_code, office, description,
  ps_budget, mooe_budget, co_budget, total_budget,
  earnmarked, obligated, expenses, balance,
  status, utilization_pct, quarterly_schedule, is_header
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", aip_seed)
print(f"  {len(aip_seed)} aip_programs records inserted.")

# ───────────────────────────────────────────────
# 5. GRAND TOTALS (from SUMMARY sheet top section)
# ───────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS grand_totals")
print("Old grand_totals table dropped.")

cur.execute("""
CREATE TABLE grand_totals (
  id                       INTEGER PRIMARY KEY AUTOINCREMENT,
  total_gad_threshold      REAL NOT NULL DEFAULT 0,
  total_obligated          REAL NOT NULL DEFAULT 0,
  total_earnmarked         REAL NOT NULL DEFAULT 0,
  total_expenses           REAL NOT NULL DEFAULT 0,
  utilization_pct          REAL NOT NULL DEFAULT 0,
  ps_expenses              REAL NOT NULL DEFAULT 0,
  ps_balance               REAL NOT NULL DEFAULT 0,
  mooe_expenses            REAL NOT NULL DEFAULT 0,
  mooe_balance             REAL NOT NULL DEFAULT 0,
  co_expenses              REAL NOT NULL DEFAULT 0,
  co_balance               REAL NOT NULL DEFAULT 0
)
""")
print("grand_totals table created.")

cur.execute("""
INSERT INTO grand_totals (
  total_gad_threshold, total_obligated, total_earnmarked, total_expenses,
  utilization_pct,
  ps_expenses, ps_balance,
  mooe_expenses, mooe_balance,
  co_expenses, co_balance
) VALUES (?,?,?,?,?,?,?,?,?,?,?)
""", (93358180.50, 3764384.50, 11097671.78, 14862056.28, 0.1566834976,
      870292.76, 6899501.24, 13991763.52, 64456622.97, 0, 7140000))
print("  1 grand_totals record inserted.")

conn.commit()
conn.close()
print("\nMigration complete!")
