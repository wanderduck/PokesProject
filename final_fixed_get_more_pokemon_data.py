"""
Final fixed get_more_pokemon_data function with correct variant data extraction
Copy this into a cell in your pokesproject_main.ipynb
"""

import re
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def get_more_pokemon_data(df, driver, start, end):
    '''
    Takes a dataframe, driver, and start and end index values and returns a dictionary of pokemon data.
    Fixed to correctly extract variant-specific height and weight data.
    '''

    # Empty lists to store data values
    pokemons = []
    categories = []
    type1s = []
    type2s = []
    heights = []
    weights = []

    def find_variant_index(variant, variants_list, pokemon_name=None):
        """
        Helper function to find variant index with fuzzy matching
        Returns the index or None if not found
        """
        # Try exact match first
        if variant in variants_list:
            return variants_list.index(variant)

        # Try pokemon name match
        if pokemon_name and pokemon_name in variants_list:
            return variants_list.index(pokemon_name)

        # Fuzzy matching strategies for common variant patterns
        variant_lower = variant.lower()

        # Strategy 1: Look for Mega variants
        if "mega" in variant_lower:
            for i, v in enumerate(variants_list):
                v_lower = v.lower()
                # Check for Mega X or Y
                if "mega" in v_lower:
                    if "x" in variant_lower and "x" in v_lower:
                        return i
                    elif "y" in variant_lower and "y" in v_lower:
                        return i
                    elif "x" not in variant_lower and "y" not in variant_lower and "x" not in v_lower and "y" not in v_lower:
                        # Plain Mega variant
                        return i

        # Strategy 2: Check if variant contains the list item or vice versa
        for i, v in enumerate(variants_list):
            # Skip base form entries
            if v.lower() == pokemon_name.lower() if pokemon_name else False:
                continue
            # Check for substring matches
            if variant in v or v in variant:
                return i
            # Check for common patterns
            variant_parts = variant.split()
            v_parts = v.split()
            # Check if main variant type matches (e.g., "Alolan" in both)
            if any(part in v_parts for part in variant_parts if len(part) > 3):
                return i

        # Strategy 3: For specific patterns
        patterns = {
            "alolan": ["alola", "alolan"],
            "galarian": ["galar", "galarian"],
            "hisuian": ["hisui", "hisuian"],
            "paldean": ["paldea", "paldean"],
            "partner": ["partner"],
            "primal": ["primal"],
            "origin": ["origin"],
            "sky": ["sky"],
            "land": ["land"],
            "therian": ["therian"],
            "incarnate": ["incarnate"],
            "defense": ["defense"],
            "attack": ["attack"],
            "speed": ["speed"]
        }

        for pattern_key, pattern_values in patterns.items():
            if any(p in variant_lower for p in pattern_values):
                for i, v in enumerate(variants_list):
                    if any(p in v.lower() for p in pattern_values):
                        return i

        return None

    def extract_height_weight_from_table(driver, variant, pokemon_name):
        """
        Extract height and weight for a specific variant from the table structure
        Returns (height, weight) tuple
        """
        height_value = None
        weight_value = None

        try:
            # Find the height table
            height_table = driver.find_element(By.XPATH, "//b[contains(.,'Height')]/ancestor::td/following-sibling::table[1]")
            height_rows = height_table.find_elements(By.TAG_NAME, "tr")

            # Process height table rows in pairs (value row, name row)
            for i in range(0, len(height_rows), 2):
                if i + 1 < len(height_rows):
                    value_row = height_rows[i]
                    name_row = height_rows[i + 1]

                    # Skip hidden rows
                    if 'display:none' in name_row.get_attribute('style') or 'display:none' in value_row.get_attribute('style'):
                        continue

                    name_text = name_row.text.strip()

                    # Check if this is our variant
                    if variant == 'No Variation' or pd.isna(variant):
                        # For base form, use the first visible row
                        if i == 0 or name_text == pokemon_name:
                            height_cells = value_row.find_elements(By.TAG_NAME, "td")
                            if len(height_cells) >= 2:
                                height_value = height_cells[1].text.strip()
                                break
                    else:
                        # For variants, match the name
                        if variant in name_text or name_text in variant:
                            height_cells = value_row.find_elements(By.TAG_NAME, "td")
                            if len(height_cells) >= 2:
                                height_value = height_cells[1].text.strip()
                                break
                        # Check for Mega variants
                        elif "mega" in variant.lower() and "mega" in name_text.lower():
                            if ("x" in variant.lower() and "x" in name_text.lower()) or \
                               ("y" in variant.lower() and "y" in name_text.lower()) or \
                               ("x" not in variant.lower() and "y" not in variant.lower()):
                                height_cells = value_row.find_elements(By.TAG_NAME, "td")
                                if len(height_cells) >= 2:
                                    height_value = height_cells[1].text.strip()
                                    break

            # If no variant match found and there are hidden rows, use the first value (all variants same)
            if not height_value and len(height_rows) > 0:
                value_row = height_rows[0]
                height_cells = value_row.find_elements(By.TAG_NAME, "td")
                if len(height_cells) >= 2:
                    height_value = height_cells[1].text.strip()

        except Exception as e:
            print(f"  Warning: Could not extract height from table: {e}")

        try:
            # Find the weight table
            weight_table = driver.find_element(By.XPATH, "//b[contains(.,'Weight')]/ancestor::td/following-sibling::table[1]")
            weight_rows = weight_table.find_elements(By.TAG_NAME, "tr")

            # Process weight table rows in pairs (value row, name row)
            for i in range(0, len(weight_rows), 2):
                if i + 1 < len(weight_rows):
                    value_row = weight_rows[i]
                    name_row = weight_rows[i + 1]

                    # Skip hidden rows
                    if 'display:none' in name_row.get_attribute('style') or 'display:none' in value_row.get_attribute('style'):
                        continue

                    name_text = name_row.text.strip()

                    # Check if this is our variant
                    if variant == 'No Variation' or pd.isna(variant):
                        # For base form, use the first visible row
                        if i == 0 or name_text == pokemon_name:
                            weight_cells = value_row.find_elements(By.TAG_NAME, "td")
                            if len(weight_cells) >= 2:
                                weight_value = weight_cells[1].text.strip()
                                break
                    else:
                        # For variants, match the name
                        if variant in name_text or name_text in variant:
                            weight_cells = value_row.find_elements(By.TAG_NAME, "td")
                            if len(weight_cells) >= 2:
                                weight_value = weight_cells[1].text.strip()
                                break
                        # Check for Mega variants
                        elif "mega" in variant.lower() and "mega" in name_text.lower():
                            if ("x" in variant.lower() and "x" in name_text.lower()) or \
                               ("y" in variant.lower() and "y" in name_text.lower()) or \
                               ("x" not in variant.lower() and "y" not in variant.lower()):
                                weight_cells = value_row.find_elements(By.TAG_NAME, "td")
                                if len(weight_cells) >= 2:
                                    weight_value = weight_cells[1].text.strip()
                                    break

            # If no variant match found and there are hidden rows, use the first value (all variants same)
            if not weight_value and len(weight_rows) > 0:
                value_row = weight_rows[0]
                weight_cells = value_row.find_elements(By.TAG_NAME, "td")
                if len(weight_cells) >= 2:
                    weight_value = weight_cells[1].text.strip()

        except Exception as e:
            print(f"  Warning: Could not extract weight from table: {e}")

        return height_value, weight_value

    try:
        # Process each Pokemon in the batch
        for link, variation in zip(df['Link'][start:end], df['Variation'][start:end]):

            variant = variation

            # Navigate to Pokemon page
            driver.get(link)
            driver.set_page_load_timeout(90)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # POKEMON NAME
            try:
                wait = WebDriverWait(driver, 30)
                pokemon = wait.until(
                    EC.presence_of_element_located((By.XPATH,
                        '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr/td[1]/big/big/b'))
                ).text
                pokemons.append(pokemon)
                print(f"Processing: {pokemon} - Variant: {variant}")
            except TimeoutException:
                print(f'Page load timed out for {link}')
                continue

            # CATEGORY
            try:
                category = driver.find_element(By.XPATH,
                    '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr/td[1]/a/span').text
                categories.append(category)
            except NoSuchElementException:
                try:
                    category = driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[1]/td/table/tbody/tr/td[1]/a/span/span').text
                    categories.append(category)
                except NoSuchElementException:
                    print(f'{pokemon} has no category')
                    categories.append(np.nan)

            # TYPES - Improved logic with better variant matching
            if variant == 'No Variation' or pd.isna(variant):
                # TYPE 1
                type1 = driver.find_element(By.XPATH,
                    '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[1]/a/span/b').text
                type1s.append(type1)

                # TYPE 2
                try:
                    type2 = driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/a/span/b').text
                    type2s.append(type2)
                except NoSuchElementException:
                    type2 = np.nan
                    type2s.append(type2)
            else:
                try:
                    # Find variants with types
                    variants_with_types = driver.find_elements(By.XPATH,
                        '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr/td/small')
                    variants_list = []
                    for element in variants_with_types:
                        variants_list.append(element.text)

                    # Use the helper function to find variant index
                    variant_idx = find_variant_index(variant, variants_list, pokemon)

                    if variant_idx is not None:
                        current_variant = str(variant_idx + 1)
                    else:
                        # If no match found, try using the first variant (index 0 is usually base form)
                        print(f"  Warning: Could not find exact match for variant '{variant}', using fallback")
                        # Check if there are any variants at all
                        if len(variants_list) > 1:
                            current_variant = "2"  # Use second entry (first variant after base)
                        else:
                            current_variant = "1"  # Fall back to base form

                    # TYPE 1
                    type1 = driver.find_element(By.XPATH,
                        f'/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[{current_variant}]/table/tbody/tr/td[1]/a/span/b').text
                    type1s.append(type1)

                    # TYPE 2
                    try:
                        type2 = driver.find_element(By.XPATH,
                            f'/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[{current_variant}]/table/tbody/tr/td[2]/a/span/b').text
                        type2s.append(type2)
                    except NoSuchElementException:
                        type2 = np.nan
                        type2s.append(type2)

                except (NoSuchElementException, IndexError) as e:
                    print(f"  Warning: Could not find variant types, using base form types. Error: {e}")
                    # Fallback to base types
                    type1 = driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[1]/a/span/b').text
                    type1s.append(type1)

                    try:
                        type2 = driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[2]/div[1]/div[3]/div[4]/div[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/a/span/b').text
                        type2s.append(type2)
                    except NoSuchElementException:
                        type2 = np.nan
                        type2s.append(type2)

            # HEIGHT & WEIGHT - NEW APPROACH using table structure
            height, weight = extract_height_weight_from_table(driver, variant, pokemon)

            if height:
                heights.append(height)
            else:
                heights.append(np.nan)

            if weight:
                weights.append(weight)
            else:
                weights.append(np.nan)

            print(f"  → Height: {height if height else 'Not found'}, Weight: {weight if weight else 'Not found'}")

        driver.close()

    except Exception as e:
        print(f'Error: {e}')
        if 'pokemon' in locals():
            print(f'Failed at: {pokemon}')
        driver.close()

        # Ensure all lists have the same length for DataFrame creation
        max_len = max(len(pokemons), len(categories), len(type1s), len(type2s), len(heights), len(weights)) if pokemons else 0

        while len(pokemons) < max_len:
            pokemons.append(np.nan)
        while len(categories) < max_len:
            categories.append(np.nan)
        while len(type1s) < max_len:
            type1s.append(np.nan)
        while len(type2s) < max_len:
            type2s.append(np.nan)
        while len(heights) < max_len:
            heights.append(np.nan)
        while len(weights) < max_len:
            weights.append(np.nan)

    # Final check to ensure all lists have the same length
    min_len = min(len(pokemons), len(categories), len(type1s), len(type2s), len(heights), len(weights)) if pokemons else 0

    return {
        'Pokemon': pokemons[:min_len] if min_len > 0 else pokemons,
        'Category': categories[:min_len] if min_len > 0 else categories,
        'Type 1': type1s[:min_len] if min_len > 0 else type1s,
        'Type 2': type2s[:min_len] if min_len > 0 else type2s,
        'Height (m)': heights[:min_len] if min_len > 0 else heights,
        'Weight (kg)': weights[:min_len] if min_len > 0 else weights
    }