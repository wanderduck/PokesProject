# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pokémon data analysis portfolio project that scrapes comprehensive data from Bulbapedia, performs multi-stage data processing, and conducts extensive exploratory data analysis with 12+ visualization types. The entire workflow is contained in `pokesproject_main.ipynb` (9.1 MB, 144 cells).

## Environment Setup

```bash
# Activate Python 3.13 virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter Notebook
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## Key Commands

```bash
# Convert notebook to Python script for code review
jupyter nbconvert --to script pokesproject_main.ipynb

# Run notebook non-interactively (execute all cells)
jupyter nbconvert --to notebook --execute pokesproject_main.ipynb

# Clean output from notebook
jupyter nbconvert --clear-output --inplace pokesproject_main.ipynb
```

## Architecture

### Three-Stage Data Pipeline

The notebook implements a complete ETL pipeline with non-sequential cell execution (check execution numbers):

#### Stage 1: Base Stats Scraping
- **Functions**: `get_driver()`, `get_pokemon_table_rows()`, `pokemon_table_rows_parser()`, `pokemon_csv_maker()`
- **Source**: `https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_base_stats_in_Generation_IX`
- **Output**: `pokemon_dataset.csv` (1,220 rows)
- **Columns**: Pokedex Number, Pokemon, Link, HP, Attack, Defense, Speed, Special Attack, Special Defense, Stat Total

#### Stage 2: Variation Detection & Cleaning
- **Process**: Identifies 24+ variation types using complex regex pattern
- **Variations**: Mega, Alolan, Partner, Galarian, Hisuian, Paldean, Primal, Forme, Cloak, Rotom, Mode, Kyurem, Ash, Eternal, Size, Hoopa, Necrozma, Hero, Crowned, Eternamax, Rider, Bloodmoon, Male, Female
- **Cleaning**: Strips variation text from Pokemon names using `.split('(')[0].rstrip()`
- **Output**: `pokemon_dataset_variations.csv` with "Variation" column

#### Stage 3: Supplementary Data & Master Dataset
- **Functions**: `get_more_pokemon_data()`, `get_pokes_rows()`, `pokes_parser1()`, `pokes_parser2()`, `pokes_csv_maker()`
- **Data Added**: Type 1, Type 2, Category, Height (m), Weight (kg), Generation
- **Output**: `pokemon_dataset_MASTER.csv` (17 columns total)

### Selenium Configuration

- **Browser**: Headless Firefox with geckodriver at `.venv/bin/geckodriver`
- **Driver Settings**:
  - Page load strategy: "eager"
  - Timeout: 90 seconds
  - Scroll execution for dynamic content
- **Important**: Multiple `get_driver()` definitions exist throughout notebook for different scraping stages

### Data Files Structure

```
data/
├── pokemon_dataset.csv              # Raw base stats (1,220 lines)
├── pokemon_dataset_variations.csv   # With variation types (1,220 lines)
├── pokemon_dataset_MASTER.csv      # Complete dataset (1,220 lines, 17 columns)
├── more_pokes.csv                  # Supplementary data (1,272 lines)
├── more_pokes_data/                # Batch-processed evolution CSVs
└── images_notebook/                # Visualization assets
    ├── POKESPROJECT_banner_logo.jpg
    └── POKESPROJECT_variation_height-weight_example.png
```

## Critical Implementation Details

### Notebook Execution Pattern
- **Non-sequential execution**: Cells executed out of order (verify with execution numbers)
- **Multiple function redefinitions**: Same functions defined multiple times with variations
- **Data dependencies**: Later cells may depend on CSV files created earlier

### Data Processing Specifics
- **Chained assignment suppression**: `pd.set_option('mode.chained_assignment', None)`
- **Variation regex**: `r'(?<=\().*(?=\))'` extracts text within parentheses
- **Name cleaning**: In-place modification using `.split('(')[0].rstrip()`
- **CSV saving**: Files saved to both project root and `data/` directory

### Visualization Pipeline (Cells 99+)

Implements 12+ visualization types using Plotly, Seaborn, and Matplotlib:

1. **Type Distributions**: Bar charts, pie charts, heatmaps
2. **Polar/Radar Charts**: Stat distributions by type, type by generation
3. **Histograms**: Generation and evolution stage distributions
4. **Strip Plots**: Stat totals by generation/evolution
5. **Statistical Analysis**: Average stats by type, correlation matrices
6. **Data Tables**: Summary statistics for Type 1 and Type 2

### Common Operations

```python
# Load master dataset
pokes_df = pd.read_csv('pokemon_dataset_MASTER.csv')

# Filter out variations
base_forms = pokes_df[pokes_df['Variation'] == 'No Variation']

# Group by type for analysis
type1_stats = pokes_df.groupby('Type 1')['Stat Total'].mean()

# Create visualization with Plotly
import plotly.express as px
fig = px.bar(type1_stats, title='Average Stats by Primary Type')
fig.show()
```

## Data Validation Checks

When modifying the scraping pipeline:
1. Verify row counts match expected Pokemon count (~1,220 including variations)
2. Check for null values in required columns (Type 1, Category)
3. Validate Height/Weight are properly converted to float
4. Ensure Generation column contains integers 1-9
5. Confirm Variation column has "No Variation" or specific variation type

## Troubleshooting

### Common Issues
- **Selenium timeout**: Increase timeout beyond 90 seconds or check Bulbapedia availability
- **Missing geckodriver**: Ensure `.venv/bin/geckodriver` exists and is executable
- **Duplicate Pokemon**: Run deduplication step after merging datasets
- **Memory issues**: Clear notebook output before saving (`--clear-output`)

### File Dependencies
- Notebook expects CSV files in both root and `data/` directories
- Images in `data/images_notebook/` used for notebook display
- Virtual environment must be activated for proper package versions