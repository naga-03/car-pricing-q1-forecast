# Git Setup Instructions

## Step 1: Install Git (if not installed)
1. Download Git from: https://git-scm.com/download/win
2. Install with default settings
3. Restart your terminal/PowerShell after installation

## Step 2: Configure Git (First time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Initialize Repository
```bash
cd "c:\Users\nagal\Downloads\projects\q1 analysis"
git init
```

## Step 4: Add Files
```bash
# Add the notebook
git add car_pricing_q1_forecast.ipynb

# Add the dataset
git add car_pricing_dataset.csv

# Add requirements file
git add requirements.txt

# Add documentation files
git add README.md
git add .gitignore

# Or add all files at once
git add .
```

## Step 5: Commit
```bash
git commit -m "Initial commit: Car pricing Q1 forecast analysis"
```

## Step 6: Create GitHub Repository
1. Go to https://github.com and create a new repository
2. Name it: `car-pricing-q1-forecast` (or your preferred name)
3. **DO NOT** initialize with README, .gitignore, or license (we already have these)

## Step 7: Connect to GitHub
```bash
# Add remote repository (using your GitHub profile: https://github.com/naga-03)
git remote add origin https://github.com/naga-03/car-pricing-q1-forecast.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Or use the automated script:**
```powershell
.\setup_and_push.ps1
```

## Alternative: Using GitHub Desktop
If you prefer a GUI:
1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. File > Add Local Repository
4. Select: `c:\Users\nagal\Downloads\projects\q1 analysis`
5. Commit and push through the GUI

## Notes:
- **Dataset Size**: The dataset (`car_pricing_dataset.csv`) is ~84 MB. Consider using Git LFS for better performance:
  ```bash
  git lfs install
  git lfs track "*.csv"
  git add .gitattributes
  git add car_pricing_dataset.csv
  ```
- **Dataset Location**: The dataset should be in the same directory as the notebook. The notebook is configured to load it locally.
- **Requirements**: Install dependencies with `pip install -r requirements.txt` before running the notebook.

