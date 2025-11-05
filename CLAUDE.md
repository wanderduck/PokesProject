# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pokémon data analysis portfolio project that scrapes data from Bulbapedia, processes it, and performs exploratory data analysis with visualizations. Primary workflow is in `pokesportfolioproject-main-35866.ipynb`.

## Environment Setup

```bash
# Activate virtual environment
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
```

## Architecture

### Web Scraping Pipeline

Three-stage scraping workflow implemented in the notebook:

1. **Base Stats Scraping**: Scrapes Pokémon base stats from Generation IX Bulbapedia table
   - Functions: `get_pokemon_table_rows()`, `pokemon_table_rows_parser()`, `pokemon_csv_maker()`
   - Source: `https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_base_stats_in_Generation_IX`
   - Output: `pokemon_dataset.csv` with columns: Pokedex Number, Pokemon, Link, HP, Attack, Defense, Speed, Special Attack, Special Defense, Stat Total

2. **Data Cleaning**: Removes variant forms and extracts forme information
   - Filters out Mega, Alolan, Partner, Galarian, Hisuian, Primal, and Paldean forms
   - Uses regex to extract forme names from parentheses (e.g., "Rotom (Heat)" → forme="Heat")
   - Output: `pokemon_dataset_cleaned.csv` with added `Forme` column

3. **Additional Data Scraping**: Scrapes supplementary information (types, categories, evolutions)
   - Functions: `get_more_pokemon_data()`, `get_pokes_rows()`, `pokes_parser1()`, `pokes_parser2()`, `pokes_csv_maker()`
   - Generates numbered evolution CSVs

### Selenium Configuration

- Uses headless Firefox with geckodriver located at `.venv/bin/geckodriver`
- Driver initialization: `get_driver()` creates Firefox instance with headless mode
- Scraping includes 90-second page load timeout and scroll execution for dynamic content
- Multiple `get_driver()` instances defined throughout notebook for different scraping stages

### Data Processing Workflow

1. Scrape raw HTML tables from Bulbapedia using Selenium
2. Parse table rows into structured dictionaries
3. Convert to Pandas DataFrames
4. Clean data (remove variants, extract formes)
5. Export to CSV files in project root
6. Perform EDA with Plotly, Seaborn, and Matplotlib

## Important Implementation Details

- Notebook cells are executed non-sequentially (check execution numbers)
- CSVs are saved to project root, not `data/` directory
- `pd.set_option('mode.chained_assignment', None)` disables chained assignment warnings
- Forme extraction regex: `r'(?<=\().*(?=\))'` captures text within parentheses
- Data cleaning modifies Pokemon names in-place using `.split('(')[0].rstrip()`