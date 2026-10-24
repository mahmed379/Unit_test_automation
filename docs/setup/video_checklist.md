# Setup Video Recording Script & Checklist

**Assignment 3 - Task 1: Record a short video to demonstrate the setup**  
**Estimated Duration**: 2 - 3 minutes  
**Format**: Screen recording with voiceover (e.g., OBS Studio, Loom, or Windows Xbox Game Bar `Win + G`).

---

## 1. Pre-Recording Checklist
- [ ] Ensure repository is freshly cloned or `.venv` is removed to show fresh setup from scratch.
- [ ] Open terminal in full screen or clear high-resolution window (`1080p`).
- [ ] Font size adjusted to 14pt-16pt for readability.
- [ ] Microphone tested and audio clear.
- [ ] Have the exact commands ready or in a side note.

---

## 2. Step-by-Step Recording Script

### Scene 1: Introduction (15 - 20 seconds)
- **Visual**: Show project root directory in terminal or VS Code.
- **Spoken**:
  > *"Hello, this is Mohammad Ahmed (mahmed379) and Wabil Rehman (Wabil-Rehman). This video demonstrates the local environment setup for Assignment 3 - Unit Test Automation Solution. We selected TinyDB, a lightweight pure-Python document database."*

### Scene 2: Verify Python and Git (15 seconds)
- **Command**:
  ```powershell
  python --version
  git --version
  ```
- **Spoken**:
  > *"First, we verify our Python version (Python 3.15 64-bit) and Git version."*

### Scene 3: Create and Activate Virtual Environment (30 seconds)
- **Command**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Spoken**:
  > *"Next, we create an isolated Python virtual environment inside `.venv` and activate it. The prompt now indicates the active virtual environment."*

### Scene 4: Install Dependencies (45 seconds)
- **Command**:
  ```powershell
  python -m pip install -e .
  python -m pip install -r requirements-dev.txt
  ```
- **Spoken**:
  > *"We now install TinyDB in editable development mode and install our test dependencies: pytest, pytest-xdist for parallel execution, pytest-order for test execution ordering, pytest-cov for coverage, and openpyxl for test case Excel processing."*

### Scene 5: Verify Setup by Running Tests (30 seconds)
- **Command**:
  ```powershell
  pytest tests/
  ```
- **Spoken**:
  > *"Finally, we run the baseline test suite. As seen on screen, all 227 tests pass in under 4 seconds with 93% baseline coverage. Our development environment is completely configured and ready for automated test development."*

---

## 3. Post-Recording Submission
- [ ] Export video as MP4 (or upload unlisted to YouTube / Google Drive / Loom).
- [ ] Add the video file or accessible link into `docs/setup/SETUP_VIDEO.md`.
