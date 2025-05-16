import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def extract_part_details(driver, part_number):
    part_details = []
    try:
        driver.get("https://boodmo.com")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.search-form")))

        search_input = driver.find_element(By.CSS_SELECTOR, "input.form-control.search-form__filed__control")
        search_input.clear()
        search_input.send_keys(part_number)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button.search-form__button__search")
        submit_button.click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "compatibility-list__item")))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='compatibility-list__item')

        product_name_tag = soup.find('h2', class_='part-info-heading')
        product_name = product_name_tag.text.strip() if product_name_tag else 'N/A'

        brand_anchor = soup.find('a', class_='part-info-top__brand')
        brand_img = brand_anchor.find('img', class_='lazy-load-images__image') if brand_anchor else None
        brand_name = brand_img['alt'].strip() if brand_img and 'alt' in brand_img.attrs else 'N/A'

        price_tag = soup.find('span', class_='part-info-price__mrp')
        price = price_tag.text.strip() if price_tag else 'N/A'

        pin = '122003'  # Default pincode

        for item in items:
            try:
                model = item.find('span', class_='compatibility-list__item__head__name').text.strip()
                year = item.find('div', {'data-head-title': 'Year'}).text.strip()
                engine = item.find('div', {'data-head-title': 'Engine'}).text.strip()
                power = item.find('div', {'data-head-title': 'Power (hp)'}).text.strip()
                fuel = item.find('div', {'data-head-title': 'Fuel type'}).text.strip()
                engine_type = item.find('div', {'data-head-title': 'Engine type'}).text.strip()

                part_details.append({
                    'Part Number': part_number,
                    'Product Name': product_name,
                    'Brand Name': brand_name,
                    'Pincode': pin,
                    'Price': price,
                    'Model': model,
                    'Year': year,
                    'Engine': engine,
                    'Power (hp)': power,
                    'Fuel Type': fuel,
                    'Engine Type': engine_type
                })
            except Exception as e:
                print(f"Error parsing compatibility item for {part_number}: {e}")
                continue

    except Exception as e:
        print(f"Search interaction failed for {part_number}: {e}")

    return part_details

def read_part_numbers_from_excel(file_path):
    try:
        df_excel = pd.read_excel(file_path)
        print("Column Names in Excel Sheet:", df_excel.columns.tolist())

        if "Part Number" in df_excel.columns:
            return df_excel["Part Number"].astype(str).tolist()
        else:
            print("Error: 'Part Number' column not found.")
            return []

    except FileNotFoundError:
        print(f"Error: Excel file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
    return []

def main():
    excel_file = r"C:\Users\DIPIN KARUNAKARAN\Downloads\Sample_Larsen (4).xlsx"
    part_numbers = read_part_numbers_from_excel(excel_file)

    all_results = []

    if part_numbers:
        driver = initialize_browser()

        try:
            for pn in part_numbers:
                print(f"\nSearching for part: {pn}")
                results = extract_part_details(driver, pn)

                if results:
                    print(f"Found {len(results)} compatibility records for {pn}")
                    all_results.extend(results)
                else:
                    print(f"No compatibility data found for {pn}")

                print("\n" + "=" * 80 + "\n")
        finally:
            driver.quit()

        if all_results:
            df_results = pd.DataFrame(all_results)
            output_file = "boodmo_compatibility_data.xlsx"

            # Check if the file is open or locked
            if os.path.exists(output_file):
                try:
                    os.rename(output_file, output_file)
                except OSError:
                    print(f"Error: The file '{output_file}' is open or locked. Please close it and try again.")
                    return

            try:
                df_results.to_excel(output_file, index=False)
                print(f"\nData saved to {output_file}")
            except PermissionError:
                print(f"Error: Permission denied when trying to write to '{output_file}'. Please ensure the file is not open and you have write permissions.")
        else:
            print("\nNo data to save to Excel.")
    else:
        print("\nNo part numbers to search.")

if __name__ == "__main__":
    main()
