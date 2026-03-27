import spacy
from rapidfuzz import process
from pymongo import MongoClient

# NLP (lepiej użyj PL!)
nlp = spacy.load("pl_core_news_sm")

# Mongo
client = MongoClient("mongodb://localhost:27017/")
db = client["fitmind"]
products_col = db["products"]


# -------------------------
# 1. Extract food + grams (spaCy 🔥)
# -------------------------
def extract_items(text: str):
    doc = nlp(text.lower())

    items = []

    for token in doc:
        # szukamy rzeczowników (produkty)
        if token.pos_ in ["NOUN", "PROPN"]:
            grams = None

            # 1. sprawdź dzieci (najlepsze dopasowanie)
            for child in token.children:
                if child.like_num:
                    grams = int(child.text)

            # 2. fallback — sprawdź sąsiednie tokeny
            if not grams:
                for neighbor in doc[max(0, token.i-2): token.i+3]:
                    if neighbor.like_num:
                        grams = int(neighbor.text)

            # jeśli znaleziono ilość → dodaj
            if grams:
                items.append({
                    "name": token.text,
                    "grams": grams
                })


    return items


# -------------------------
# 2. Fuzzy match
# -------------------------
def resolve_product(word: str, product_names: list):
    match = process.extractOne(word, product_names)

    if match and match[1] > 75:  # lekko obniżone dla PL fleksji
        return match[0]

    return None


# -------------------------
# 3. Main function
# -------------------------
def calculate(text: str):
    items = extract_items(text)

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

    result = [
         item for item in result
         if item.get("kcal") and item.get("grams") and item.get("resolved")
    ]

    response = {
        "items": result,
        "totalKcal": total
    }

    print(response)
    return response