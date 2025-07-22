import pandas as pd

# === Load original CSV ===
df = pd.read_csv("catalog.csv")

# === Replace backslashes with forward slashes in Image column ===
df["Image"] = df["Image"].astype(str).str.replace("\\", "/", regex=False)

# === Save to new CSV ===
df.to_csv("restokart_catalog_fixed.csv", index=False)

print("✅ Image paths cleaned and saved to 'catalog_fixed.csv'")
