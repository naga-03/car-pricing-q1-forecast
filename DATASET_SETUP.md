# Dataset Setup Instructions

## Current Setup (Local Execution)
The notebook is now configured for local execution:
- **Dataset file**: `car_pricing_dataset.csv` (~84 MB)
- **Location**: Same directory as the notebook
- **Path in notebook**: `car_pricing_dataset.csv` (relative path)

## Option 1: Local Setup (Current - Recommended)
The notebook is ready to run locally:
1. **Ensure** `car_pricing_dataset.csv` is in the same directory as the notebook
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run the notebook**: Open `car_pricing_q1_forecast.ipynb` in Jupyter and run all cells

No path changes needed - the notebook is already configured!

## Option 2: Using Google Colab
To run the notebook in Google Colab:

1. **Upload the notebook** to Google Colab
2. **Upload** `car_pricing_dataset.csv` to your Google Drive
3. **Uncomment** the Google Drive mount cell (Cell 1):
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

4. **Update Cell 3** to use your Google Drive path:
   ```python
   data = pd.read_csv('/content/drive/My Drive/datasets/car_pricing_dataset.csv')
   ```

## Option 3: Add Dataset to Git

### Option 3a: Direct Inclusion (Simple)
The dataset is ~84 MB, which is manageable but large. You can add it directly:
```bash
git add car_pricing_dataset.csv
git commit -m "Add car pricing dataset"
```

**Note**: GitHub allows files up to 100 MB. Files between 50-100 MB may cause slower clone times.

### Option 3b: Git LFS (Recommended for Large Files)
For better performance and to follow best practices, use Git LFS:
```bash
# Install Git LFS (if not already installed)
git lfs install

# Track CSV files
git lfs track "*.csv"

# Add the tracking file
git add .gitattributes

# Add the dataset
git add car_pricing_dataset.csv

# Commit
git commit -m "Add car pricing dataset (LFS)"
```

### Option 3c: Exclude from Git
If you prefer not to track the dataset in Git:
1. **Uncomment** the line in `.gitignore`:
   ```
   car_pricing_dataset.csv
   ```
2. **Host the dataset separately** (Google Drive, Dropbox, etc.)
3. **Add download link** in README.md
4. **Update** README.md with download instructions

## Recommended Approach
For GitHub repositories:
- **< 50MB**: Include directly in repository ✅
- **50-100MB**: Use Git LFS (recommended) or include directly ⚠️
- **> 100MB**: Host externally and provide download link ❌

**Current dataset (~84 MB)**: Use Git LFS (Option 3b) for best practice, or include directly (Option 3a) if acceptable.

