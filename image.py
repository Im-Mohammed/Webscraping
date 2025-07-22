import pandas as pd
import os
from difflib import get_close_matches

# Load product CSV
df = pd.read_csv("catalog.csv")

# Root image folder
root_folder = "D:/webscraping/downloaded_images"

# Gather all image filenames from folder tree
def get_all_images():
    image_files = []
    for category in os.listdir(root_folder):
        cat_path = os.path.join(root_folder, category)
        if os.path.isdir(cat_path):
            for subcat in os.listdir(cat_path):
                subcat_path = os.path.join(cat_path, subcat)
                if os.path.isdir(subcat_path):
                    for filename in os.listdir(subcat_path):
                        filepath = os.path.join("downloaded_images", category, subcat, filename)
                        image_files.append((filename, filepath))
    return image_files

image_index = get_all_images()

# Match function with fuzzy logic
def find_image(product_name):
    normalized = product_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_") + ".jpg"
    candidates = [img[0] for img in image_index]
    match = get_close_matches(normalized, candidates, n=1, cutoff=0.8)
    if match:
        for img_file, img_path in image_index:
            if img_file == match[0]:
                return img_path
    return "N/A"

# Apply and export
df["Image"] = df["Product Name"].apply(find_image)
df.to_csv("catalog_with_images.csv", index=False)
print("✅ Fuzzy image matching complete and saved to CSV")
