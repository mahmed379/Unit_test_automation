# Local Environment Setup Guide

**Project**: TinyDB (v4.9.0)  
**Course**: Software Quality Engineering / Automated Software Testing  
**Assignment**: Assignment 3 - Build Unit Test Automation Solution  
**Contributors**:
- Mohammad Ahmed (`mahmed379` / `mohammadahmed41235@gmail.com`)
- Wabil Rehman (`Wabil-Rehman` / `Wabilrehman2626@gmail.com`)

---

## 1. Prerequisites

- **Python**: Version 3.10+ (Tested with Python 3.15.0 64-bit on Windows).
- **Git**: Version 2.40+ (Command line tools installed).
- **Terminal / Shell**: PowerShell (Windows) or Bash (Linux / macOS).

Verify current versions:
```powershell
python --version
git --version
```

---

## 2. Step-by-Step Installation

### Step 2.1: Clone the Repository
Clone the group repository and navigate into the project root:
```powershell
git clone <repository-url>
cd Unit_test_automation
```

### Step 2.2: Create Virtual Environment
Create an isolated Python virtual environment inside `.venv`:
```powershell
# Windows
python -m venv .venv

# Linux / macOS
python3 -m venv .venv
```

### Step 2.3: Activate Virtual Environment
Activate the environment:
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.\.venv\Scripts\activate.bat

# Linux / macOS Bash/Zsh
source .venv/bin/activate
```

*Note for Windows users:* If PowerShell displays a script execution policy error, enable local script execution for the current user:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2.4: Upgrade Package Installer (pip)
```powershell
python -m pip install --upgrade pip
```

### Step 2.5: Install Project and Development Dependencies
Install TinyDB in editable development mode along with test runner dependencies:
```powershell
# Install project in editable mode
python -m pip install -e .

# Install test automation dependencies
python -m pip install -r requirements-dev.txt
```

Installed testing dependencies include:
- `pytest`: Unit test execution framework.
- `pytest-xdist`: Parallel test execution engine.
- `pytest-order`: Test and suite ordering controller.
- `pytest-cov`: Code coverage analysis tool.
- `openpyxl`: Excel `.xlsx` generator and reader for test specifications.

---

## 3. Verifying the Setup

Run the upstream baseline unit test suite to verify 100% functionality:
```powershell
pytest tests/
```

Expected output:
```text
======================= 227 passed, 1 skipped in 3.89s ========================
```

To run with coverage summary:
```powershell
pytest --cov=tinydb tests/
```

---

## 4. Troubleshooting

- **Issue**: `ModuleNotFoundError: No module named 'tinydb'`
  - **Resolution**: Ensure the virtual environment is activated and `pip install -e .` was executed from the root directory.
- **Issue**: `pytest: command not found`
  - **Resolution**: Ensure you are running within the activated `.venv` or execute via `.\.venv\Scripts\pytest.exe`.
- **Issue**: PowerShell Execution Policy error on `.venv\Scripts\Activate.ps1`
  - **Resolution**: Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell session.
