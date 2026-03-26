# Bitcoin Analysis

## Setup

1. **Create virtual environment:**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Analysis
```powershell
python btc_analysis.py
```

## Adding New Packages
When you install a new package:
```powershell
pip freeze > requirements.txt
```
Then commit `requirements.txt` to GitHub.
