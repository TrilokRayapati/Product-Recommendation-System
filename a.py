import pandas as pd
import random
import string

# Define categories and product name prefixes
categories = ["Electronics", "Fiction", "Sports", "Clothing", "Home", "Beauty", "Toys"]
product_prefixes = {
    "Electronics": ["Smart", "Wireless", "Gaming", "Portable"],
    "Fiction": ["Mystery", "Fantasy", "Sci-Fi", "Romance"],
    "Sports": ["Running", "Yoga", "Soccer", "Cycling"],
    "Clothing": ["Casual", "Formal", "Sportswear", "Winter"],
    "Home": ["Kitchen", "Decor", "Furniture", "Garden"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Perfume"],
    "Toys": ["Educational", "Action", "Building", "Dolls"]
}
personality_traits = [
    "Tech-savvy", "Curious", "Active", "Creative", "Organized", "Adventurous",
    "Social", "Detail-oriented", "Relaxed", "Ambitious", "Caring", "Analytical"
]

# Generate 1000 product entries
data = []
for product_id in range(1, 1001):
    category = random.choice(categories)
    prefix = random.choice(product_prefixes[category])
    product_name = f"{prefix} {''.join(random.choices(string.ascii_uppercase, k=3))}"
    interest_score = round(random.uniform(0.5, 0.95), 2)
    traits = ", ".join(random.sample(personality_traits, random.randint(2, 4)))
    data.append([product_id, product_name, category, interest_score, traits])

# Create DataFrame and save to CSV
df = pd.DataFrame(data, columns=["product_id", "product_name", "category", "interest_score", "personality_traits"])
df.to_csv("data/products.csv", index=False)
print("Dataset saved as data/products.csv")
print("\nSample of the first 5 rows:")
print(df.head().to_string())