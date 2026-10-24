# Automated Unit Testing Solution: TinyDB

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14%20%7C%203.15-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-351%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)]()

> **Assignment 3: Build Unit Test Automation Solution**  
> **Course**: Software Quality Engineering / Automated Software Testing  
> **Target Project**: [TinyDB](https://github.com/msiemens/tinydb) (v4.9.0)  

---

## 👥 Contributors & Ownership Matrix

| Contributor | GitHub Username | Email | Primary Responsibilities |
|---|---|---|---|
| **Mohammad Ahmed** | `mahmed379` | `mohammadahmed41235@gmail.com` | - Environment setup & Task 1 documentation<br>- `tinydb.table` (insert, get, search, update, truncate, query cache)<br>- `tinydb.queries` (comparison operators, numeric threshold BVA, exists, boolean algebra)<br>- `tinydb.storages` (`MemoryStorage` lifecycle, empty states, isolation)<br>- CSV data-driven tests (`test_data_table_mahmed.csv`, `test_data_queries_mahmed.csv`)<br>- Excel test cases (TC_M01 – TC_M09) |
| **Wabil Rehman** | `Wabil-Rehman` | `Wabilrehman2626@gmail.com` | - `tinydb.table` (insert_multiple, remove, upsert, count, contains, clear_cache)<br>- `tinydb.queries` (regex matches, search, any, all, one_of, test, nested paths)<br>- `tinydb.storages` (`JSONStorage` 0-byte files, file truncation, closed handles, read-only)<br>- CSV data-driven tests (`test_data_table_wabil.csv`, `test_data_queries_wabil.csv`)<br>- Excel test cases (TC_W01 – TC_W10) |

---

## 📁 Repository Structure

```text
Unit_test_automation/
├── docs/
│   ├── setup/
│   │   ├── environment_setup.md         # Step-by-step local development setup guide
│   │   ├── video_checklist.md           # Setup video recording script & checklist
│   │   └── SETUP_VIDEO.md               # Link and information for setup demonstration video
│   ├── test_design/
│   │   ├── ECP_BVA_table.md             # ECP & BVA specifications for tinydb.table
│   │   ├── ECP_BVA_queries.md           # ECP & BVA specifications for tinydb.queries
│   │   └── ECP_BVA_storages.md          # ECP & BVA specifications for tinydb.storages
│   └── summary_report.md                # Comprehensive project summary & metrics report
├── tests/
│   ├── conftest.py                      # Global fixtures and CSV data loading utilities
│   ├── data/
│   │   ├── test_data_table_mahmed.csv   # External CSV data for Table (mahmed379)
│   │   ├── test_data_queries_mahmed.csv # External CSV data for Queries (mahmed379)
│   │   ├── test_data_table_wabil.csv    # External CSV data for Table (Wabil-Rehman)
│   │   └── test_data_queries_wabil.csv  # External CSV data for Queries (Wabil-Rehman)
│   ├── excel/
│   │   └── test_cases.xlsx              # 19 formal test cases with ECP/BVA classifications
│   ├── queries/
│   │   ├── test_queries_mahmed.py       # 25 unit tests by Mohammad Ahmed
│   │   └── test_queries_wabil.py        # 23 unit tests by Wabil Rehman
│   ├── storages/
│   │   ├── test_storages_mahmed.py      # 9 unit tests by Mohammad Ahmed
│   │   └── test_storages_wabil.py       # 8 unit tests by Wabil Rehman
│   └── table/
│       ├── test_table_mahmed.py         # 32 unit tests by Mohammad Ahmed
│       └── test_table_wabil.py          # 27 unit tests by Wabil Rehman
├── tinydb/                              # Untouched upstream TinyDB source code
├── scripts/
│   └── generate_excel.py                # openpyxl generator for test_cases.xlsx
├── requirements-dev.txt                 # Test automation & runner dependencies
├── pytest.ini                           # Pytest configuration, markers, and coverage options
├── .gitignore                           # Git ignore rules for venv, cache, and reports
└── README.md                            # Main project documentation
```

---

## ⚙️ Environment Setup

### 1. Prerequisites
- **Python**: Version 3.10+ (Tested with Python 3.15.0 on Windows).
- **Git**: Version 2.40+.

### 2. Quick Setup Commands
```powershell
# Clone the repository
git clone <repository-url>
cd Unit_test_automation

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # On Linux/macOS: source .venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

For detailed setup instructions, troubleshooting, and verification steps, refer to [`docs/setup/environment_setup.md`](docs/setup/environment_setup.md).  
For the setup video recording script and submission link, refer to [`docs/setup/SETUP_VIDEO.md`](docs/setup/SETUP_VIDEO.md).

---

## 🚀 How to Run the Tests

### 1. Run Everything
Execute all newly built unit tests across all 3 modules:
```powershell
pytest tests/table tests/queries tests/storages
```

Execute the entire repository (124 new tests + 227 upstream tests = 351 tests):
```powershell
pytest
```

---

### 2. Parallel Test Execution (`pytest-xdist`)
Run tests in parallel across all available CPU cores:
```powershell
pytest -n auto tests/table tests/queries tests/storages
```
Or specify the exact number of worker processes (e.g. 4 workers):
```powershell
pytest -n 4 tests/table tests/queries tests/storages
```

---

### 3. Run Specific Test Suites / Groups (Pytest Markers)
The test suite utilizes custom markers registered in [`pytest.ini`](pytest.ini):

| Suite / Marker | Purpose | Command |
|---|---|---|
| **Smoke Suite** | Fast sanity checks for critical core paths | `pytest -m smoke` |
| **Regression Suite** | Full comprehensive regression testing | `pytest -m regression` |
| **Boundary (BVA)** | Boundary Value Analysis test cases | `pytest -m boundary` |
| **Equivalence (ECP)** | Equivalence Class Partitioning test cases | `pytest -m ecp` |
| **CSV Data-Driven** | Tests consuming external CSV data files | `pytest -m csv_data` |
| **Table Module** | Tests targeting `tinydb.table` | `pytest -m table` |
| **Queries Module** | Tests targeting `tinydb.queries` | `pytest -m queries` |
| **Storages Module** | Tests targeting `tinydb.storages` | `pytest -m storages` |

*Combining markers:*
```powershell
# Run smoke tests for the table module only
pytest -m "smoke and table"

# Run all boundary tests for queries
pytest -m "boundary and queries"
```

---

### 4. Run Tests by Individual Contributor
Each contributor's work is organized in isolated test files:
```powershell
# Run all tests authored by Mohammad Ahmed (mahmed379)
pytest tests/*/*_mahmed.py

# Run all tests authored by Wabil Rehman (Wabil-Rehman)
pytest tests/*/*_wabil.py
```

---

### 5. Explicit Test Execution Ordering (`pytest-order`)
Tests carry `@pytest.mark.order(n)` decorators to guarantee predictable, dependency-free execution:
- **Order 1 – 22 & 100 – 120**: `Table` module tests
- **Order 30 – 43 & 130 – 143**: `Queries` module tests
- **Order 50 – 58 & 160 – 167**: `Storages` module tests

To run in enforced sequential order:
```powershell
pytest tests/table tests/queries tests/storages
```

---

### 6. Generate Code Coverage Report (`pytest-cov`)
Generate terminal and HTML test coverage reports:
```powershell
# Terminal coverage report
pytest --cov=tinydb tests/table tests/queries tests/storages

# Generate HTML coverage report in htmlcov/
pytest --cov=tinydb --cov-report=html tests/table tests/queries tests/storages
```

Current test suite coverage: **93% line and branch coverage** on the core `tinydb` codebase.

---

## 📊 Summary of Test Metrics

- **Total New Group Tests**: **124 automated tests** (100% passing)
  - **Mohammad Ahmed (`mahmed379`)**: 66 tests
  - **Wabil Rehman (`Wabil-Rehman`)**: 58 tests
- **Total Repository Tests**: **351 automated tests** (100% passing)
- **Excel Test Cases**: 19 formal test cases in [`tests/excel/test_cases.xlsx`](tests/excel/test_cases.xlsx)
- **External CSV Data Sets**: 4 distinct CSV files in [`tests/data/`](tests/data/)
