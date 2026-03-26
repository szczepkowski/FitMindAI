import spacy
import re
from rapidfuzz import process
from pymongo import MongoClient

# NLP
nlp = spacy.load("en_core_web_sm")

# Mongo
client = MongoClient("mongodb://localhost:27017/")
db = client["fitmind"]
products_col = db["products"]


# -------------------------
# 1. Extract food + grams
# -------------------------
def extract_items(text: str):
    doc = nlp(text.lower())

    items = []

    # prosty pattern: "kurczak 200g"
    pattern = r"(\w+)\s*(\d+)\s*g"
    matches = re.findall(pattern, text.lower())

    for name, grams in matches:
        items.append({
            "name": name,
            "grams": int(grams)
        })

    return items


# -------------------------
# 2. Fuzzy match
# -------------------------
def resolve_product(word: str, product_names: list):
    match = process.extractOne(word, product_names)

    if match and match[1] > 80:
        return match[0]

    return None


# -------------------------
# 3. Main function
# -------------------------
def calculate(text: str):
    items = extract_items(text)

    # pobierz produkty z Mongo
    products = list(products_col.find())
    product_names = [p["name"] for p in products]

    total = 0
    result = []

    for item in items:
        resolved = resolve_product(item["name"], product_names)

        if not resolved:
            result.append({
                "input": item["name"],
                "error": "not found"
            })
            continue

        product = next(p for p in products if p["name"] == resolved)

        kcal = (item["grams"] / 100) * product["kcal_per_100g"]
        total += kcal

        result.append({
            "input": item["name"],
            "resolved": resolved,
            "grams": item["grams"],
            "kcal": kcal
        })

    return {
        "items": result,
        "total_kcal": total
    }
