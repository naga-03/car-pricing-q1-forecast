# Car Pricing Q1 Forecast Analysis

## Project Overview
This project analyzes car pricing data to understand sales trends and develop a predictive model for Q1 (January-March) car sales forecasting. The analysis includes data exploration, visualization, and machine learning modeling.

## Dataset
- **File**: `car_pricing_dataset.csv`
- **Records**: 558,837 initial records (472,325 after cleaning)
- **Columns**: 16 features including year, make, model, condition, odometer, MMR, selling price, etc.
- **Size**: ~84 MB

## Key Features
- Comprehensive data cleaning and preprocessing
- Exploratory Data Analysis (EDA) with visualizations
- Q1 sales trend analysis
- Linear Regression model for price prediction (R² = 0.96)
- Outlier detection and analysis

## Notebook Structure
1. **Data Loading & Cleaning**: Load dataset from local file, clean and preprocess data
2. **Exploratory Analysis**: Visualize sales patterns, top brands, models, colors, states
3. **Q1 Analysis**: Focus on January-March sales trends and patterns
4. **Predictive Modeling**: Linear regression model for price forecasting
5. **Summary**: Comprehensive analysis summary and recommendations

## Model Performance
- **R² Score**: 0.9604 (96.04%)
- **Features**: condition, odometer, mmr, sale_year
- **Performance**: Excellent predictive capability for car price forecasting

## Requirements
Install the required packages using:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

## Usage

### Local Execution (Recommended)
1. **Clone or download** this repository
2. **Ensure** `car_pricing_dataset.csv` is in the same directory as the notebook
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Launch Jupyter**: `jupyter notebook`
5. **Open** `car_pricing_q1_forecast.ipynb` and run all cells

### Google Colab
1. Upload the notebook to Google Colab
2. Upload `car_pricing_dataset.csv` to your Google Drive
3. Uncomment the Google Drive mount cell (Cell 1)
4. Update the dataset path in Cell 3 to your Google Drive path
5. Run all cells

## Key Findings
- MMR (Manheim Market Report) is the strongest predictor of selling price
- Top-selling brands: Ford, Chevrolet, Toyota, BMW
- Most popular colors: White, Black, Silver
- Q1 shows consistent sales patterns across months
- Model achieves 96% accuracy in price prediction

## Recommendations
1. Use the regression model for competitive pricing
2. Focus inventory on top-selling brands and models
3. Monitor MMR trends as primary price indicator
4. Consider adding categorical features for model enhancement

## Project Structure
```
q1 analysis/
├── car_pricing_q1_forecast.ipynb  # Main analysis notebook
├── car_pricing_dataset.csv         # Dataset (84 MB, tracked with Git LFS)
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore rules
└── .gitattributes                  # Git LFS configuration
```

## Dataset Note
The dataset file (`car_pricing_dataset.csv`) is ~84 MB and is tracked using Git LFS for efficient version control.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Free to use for personal and commercial projects
- ✅ Can modify and distribute
- ✅ Only requires attribution (copyright notice)
- ✅ No warranty provided

