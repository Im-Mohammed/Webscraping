from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# === Setup Headless Chrome Driver ===
def start_driver():
    options = Options()
    options.headless = True
    options.add_argument("--log-level=3")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Configuration for One Sub-category ===
BASE_URL = "https://www.ecommerce.com/product-list/"
slug = "pizza-boxes/26"           # 🔁 Change this for different sub-category
category = "Paper Products"       # ✅ Set the category name manually
subcat = slug.split("/")[0].replace("-", " ").title()  # 🧭 Format sub-category label

# === Main Scraping Function ===
def scrape_one_subcategory(driver):
    page = 1
    product_rows = []

    while True:
        listing_url = f"{BASE_URL}{slug}?per_page={page}" if page > 1 else f"{BASE_URL}{slug}"
        print(f"📄 Listing page: {listing_url}")
        driver.get(listing_url)
        time.sleep(2.5)

        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        if not cards:
            break

        product_links = []
        for card in cards:
            try:
                link = card.find_element(By.XPATH, ".//a[not(contains(@href,'hover'))]").get_attribute("href")
                product_links.append(link)
            except:
                continue

        for link in product_links:
            try:
                driver.get(link)
                time.sleep(1.5)
                # Extract product name reliably from <h3 class="product-title product_viva_nameXX">
                name = driver.find_element(By.XPATH, "//h3[contains(@class, 'product-title')]").text.strip()
            except:
                name = "N/A"

            product_rows.append([category, subcat, name, link])

        page += 1

    return product_rows

# === Run the Script ===
driver = start_driver()
rows = scrape_one_subcategory(driver)
driver.quit()

# === Save to CSV File ===
df = pd.DataFrame(rows, columns=["Category", "Sub-category", "Product Name", "Product URL"])
df.to_csv("pizza_boxes.csv", index=False)
print("✅ Done! Scraped data saved to 'pizza_boxes.csv'")
