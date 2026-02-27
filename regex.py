import re
import spacy

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Units & actions
units = [
    "kg","tons","liters","cans","bottles","boxes","cartons","packs","packets",
    "bags","sacks","drums","containers","crates","pallets","bundles",
    "pieces","pcs","units","items","dozen","pairs","sets","trays"
]

actions = [
    "received", "arrived", "shipped", "sent",
    "dispatched", "delivered", "issued",
    "transferred", "moved", "left", "remaining",
    "available", "added", "removed", "returned",
    "damaged", "expired", "consumed",
    "used", "allocated", "picked",
    "packed", "loaded", "unloaded",
    "got", "found", "lost", "counted",
    "adjusted", "updated", "reconciled", "restocked", "finished"
]

# Helper to singularize
def singular(word):
    if word.endswith("es"):
        return word[:-2]
    if word.endswith("s"):
        return word[:-1]
    return word


def extract_info(text):
    text = text.lower().strip()
    doc = nlp(text)

    quantity = None
    unit = None
    item = None
    action = None

    # -------------------------------
    # Detect quantity, unit, item
    # -------------------------------
    for i, token in enumerate(doc):

        if quantity and item:
            break

        if token.like_num and quantity is None:
            quantity = token.text

            # Case 1: number + unit
            if i + 1 < len(doc) and doc[i + 1].text in units:
                unit = doc[i + 1].text

                # Case 1A: number + unit + of + item
                if i + 2 < len(doc) and doc[i + 2].text == "of":
                    if i + 3 < len(doc):
                        item = singular(doc[i + 3].text)

                # Case 1B: number + unit + item
                elif i + 2 < len(doc):
                    item = singular(doc[i + 2].text)

            # Case 2: number + item (no unit)
            elif i + 1 < len(doc):
                item = singular(doc[i + 1].text)

    # -------------------------------
    # Regex fallback (if SpaCy fails)
    # -------------------------------
    if not item:
        patterns = [
            rf'(\d+)\s*({"|".join(units)})\s*of\s*([a-zA-Z]+)',
            rf'([a-zA-Z]+)\s*of\s*(\d+)\s*({"|".join(units)})',
            rf'(\d+)\s*({"|".join(units)})\s*([a-zA-Z]+)'
        ]

        for p in patterns:
            m = re.search(p, text)
            if m:
                g = m.groups()
                if g[0].isdigit():
                    quantity, unit, item = g
                else:
                    item, quantity, unit = g
                item = singular(item)
                break

    # -------------------------------
    # Detect action
    # -------------------------------
    for token in doc:
        if token.text in actions:
            action = token.text
            break

    # -------------------------------
    # Final Safety Normalization
    # -------------------------------
    if quantity:
        quantity = int(quantity)

    if item:
        item = item.strip()

    if not unit:
        unit = "units"

    if action:
        action = action.lower()

    # Prevent garbage words as item
    if item in ["of", "the", "and"]:
        item = None

    return quantity, unit, item, action


# -------------------------------
# Test Section
# -------------------------------
""""
if __name__ == "__main__":
    tests = [
        "I got 5 tons of mangoes",
        "30 kg of fruits left",
        "fruits of 30 kg left",
        "30 kg fruits left",
        "milk of 30 cans left",
        "10 dozen of eggs are left",
        "50 apples arrived",
        "20 bottles of water shipped"
    ]

    for t in tests:
        print(t, "→", extract_info(t))
        """