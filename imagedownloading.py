from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import requests
import os

# === Setup Headless Chrome Driver ===
def start_driver():
    options = Options()
    options.headless = True
    options.add_argument("--log-level=3")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Category Map ===
category_map = {
    "Paper Products": [
        "standard-products/15" , "pizza-boxes/26", "cups-glasses-for-cold-beverages/29",
        "tea-flasks/50", "paper-meal-boxes/53", "cups-glasses-for-hot-beverages/58",
        "burger-fries/71", "sandwich-and-waffle-/74", "paper-containers/79",
        "ready-stickers/81", "paper-packaging-accessories/90", "kraft-meal-boxes-with-window/92",
        "qsr-takeout-and-servings/100", "clear-lid-paper-containers/102",
        "paper-food-trays/103", "wrap-roll-boxes/109"
    ],
    "Reusable Plastics": [
        "round-containers/11", "rectangular-containers/12", "rore-series/14",
        "rectangular-sealable-containers/16", "pet-products/17", "compostable-produts/21",
        "dipportion-cups/22", "meal-trays/25", "tamperproof-containers/104",
        "takeaway-beverage-cups/105"
    ],
    "Kitchen Utilities": [
        "cleaning-agents/33", "tissue-papers/34", "packaging-accessories/35",
        "packing-machines/36", "housekeeping-products/37", "kitchen-tools-essentials/59",
        "home-care-essentials/93", "baking-moulds/94", "bar-aid-accessories/95",
        "kitchen-cutlery/96", "pizza-tools-and-bakeware/98",
        "baking-smallwares-and-accessories/99"
    ],
    "Eco-Friendly Products": [
        "glass-items/18", "aluminium-foil-products/19", "bagasse-plates-bowls/23",
        "bagasse-trays-with-lid/24", "wooden-products/31", "earthen-clay-products/32",
        "areca-leaf-products/48", "clamshell-boxes/110", "anti-leak-bagasse-containers/111"
    ],
    "Carry Bags": [
        "paper-handle-bags/38", "grocery-bags/39", "side-gusset-envelopes/40",
        "non-woven-bags/41", "flat-paper-envelopes/42", "standup-zipper-pouches/57",
        "aluminium-coated-envelopes/106"
    ],
    "Bakery Supplies": [
        "window-cake-boxes/5", "corrugated-cake-boxes/27", "bake-and-serve/30",
        "metal-moulds/51", "brownie-boxes/55", "cup-cake-boxes/56", "pastry-boxes/85",
        "decoration-accessories/87", "cake-base/88", "standard-bakery-boxes/89",
        "rigid-crystal-products/97"
    ],
    "Pack by Menu for Beginners": [
        "rice-biryani/64", "soups-thukpas/65", "hot-gravies/66", "noodles-spaghetti/67",
        "brunch-meal-combos/68", "pizzas/69", "salads/70", "dumplings/72",
        "wraps-rolls/73", "coffee-tea-bar/107", "confectionery-patisserie-shop/108"
    ]
}

BASE_URL = "https://www.ecommerce.com/product-list/"

# === Scraping Logic for One Sub-category ===
def scrape_subcategory(driver, category, slug):
    subcat = slug.split("/")[0].replace("-", " ").title()
    page = 1
    product_rows = []

    while True:
        url = f"{BASE_URL}{slug}?per_page={page}" if page > 1 else f"{BASE_URL}{slug}"
        driver.get(url)
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
            driver.get(link)
            time.sleep(1.5)

            # ✅ Product Name
            try:
                name = driver.find_element(By.XPATH, "//h3[contains(@class, 'product-title')]").text.strip()
            except:
                name = "N/A"

            # 💸 Product Price
            try:
                price = driver.find_element(By.XPATH, "//span[contains(@class, 'price-new')]").text.strip()
            except:
                price = "N/A"

            # 📋 Description
            try:
                description = driver.find_element(By.XPATH, "//article[contains(@class, 'review-article')]").text.strip()
            except:
                description = "N/A"

            # 🧾 Product Details
            details = {}
            try:
                wrapper = driver.find_element(By.CLASS_NAME, "review-wrapper")
                strong_tags = wrapper.find_elements(By.TAG_NAME, "strong")

                for tag in strong_tags:
                    label = tag.text.strip().replace(":", "")
                    parent = tag.find_element(By.XPATH, "..")
                    html = parent.get_attribute("innerHTML")

                    match = re.search(rf"<strong[^>]*>{re.escape(label)}:?<\/strong>\s*:?([\s\S]+?)(<|$)", html)
                    value = match.group(1).strip() if match else ""
                    value = re.sub(r"<[^>]+>", "", value).strip()

                    if label and label not in details and value:
                        details[label] = value
            except:
                details = {}

            flat_details = "; ".join([f"{k}: {v}" for k, v in details.items()])

            # 🖼️ Image URL + Download
# 🖼️ Product Image URL from slick-slide container
            try:
                image_element = driver.find_element(By.XPATH, "//div[contains(@class, 'single-slide')]//img")
                image_url = image_element.get_attribute("src")
            except:
                image_url = None


            image_path = "N/A"
            if image_url and name != "N/A":
                folder_path = os.path.join("images", category, subcat)
                os.makedirs(folder_path, exist_ok=True)
                filename = name.replace("/", "_").replace("\\", "_").replace(":", "_").strip() + ".jpg"
                image_path = os.path.join(folder_path, filename)
                try:
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(response.content)
                except Exception as e:
                    print(f"⚠️ Failed to download image for {name}: {e}")
                    image_path = "N/A"

            # 📄 Append product row
            product_rows.append({
                "Category": category,
                "Sub-category": subcat,
                "Product Name": name,
                "Price": price,
                "Description": description,
                "Details": flat_details,
                "Image": image_path
            })

        page += 1

    return product_rows

# === Main Execution ===
driver = start_driver()
all_data = []

for category, slugs in category_map.items():
    print(f"🔍 Scraping Category: {category}")
    for slug in slugs:
        print(f"   • Sub-category: {slug}")
        rows = scrape_subcategory(driver, category, slug)
        all_data.extend(rows)

driver.quit()

# === Export to CSV ===
df = pd.DataFrame(all_data)
df.to_csv("catalog_with_all_images.csv", index=False)
print("✅ All categories scraped and saved to 'catalog_with_all_images.csv'")
