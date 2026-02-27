import re

units =  "kg|tons|liters|cans|bottles|boxes|cartons|packs|packets|bags|sacks|drums|containers|crates|pallets|bundles|pieces|pcs|units|items|dozen|pairs|sets|trays"

actions = [
    # stock movement
    "received", "arrived", "shipped", "sent",
    "dispatched", "delivered", "issued",
    "transferred", "moved",

    # stock status
    "left", "remaining", "available",
    "in stock", "out of stock",

    # inventory operations
    "added", "removed", "returned",
    "damaged", "expired", "consumed",
    "used", "allocated", "picked",
    "packed", "loaded", "unloaded",

    # adjustments
    "adjusted", "updated", "counted",
    "reconciled", "restocked","finished"
]
# stop item before action words
action_pattern = "|".join(actions)

patterns = [
    # ---- WITH UNIT ----
    rf'(\d+)\s*({units})\s*of\s*([a-zA-Z]+)',
    rf'([a-zA-Z]+)\s*of\s*(\d+)\s*({units})',
    rf'(\d+)\s*({units})\s*([a-zA-Z]+)',

    # ---- WITHOUT UNIT ----
    rf'(\d+)\s+([a-zA-Z]+)(?=\s*(?:{action_pattern}))',
    rf'([a-zA-Z]+)\s+(\d+)',
    rf'([a-zA-Z]+)\s*of\s*(\d+)'
]

def singular(word):
    if word.endswith("s"):
        return word[:-1]
    return word

def extract_info(text):
    quantity = unit = item = action = None
    text = text.lower()

    for p in patterns:
        m = re.search(p, text)
        if m:
            groups = m.groups()

            if len(groups) == 3:
                if groups[0].isdigit():
                    quantity, unit, item = groups
                else:
                    item, quantity, unit = groups
            elif len(groups) == 2:
                if groups[0].isdigit():
                    quantity, item = groups
                else:
                    item, quantity = groups

            break

    # detect action
    for a in actions:
        if a in text:
            action = a
            break

    # clean item
    if item:
        item = singular(item.strip())

    return quantity, unit, item, action


"""tests = [
    "30 kg of fruits left",
    "fruits of 30 kg left",
    "30 kg fruits left",
    "milk of 30 cans left",
    "10 dozen of eggs are left",
    "50 apples arrived"
]"""

"""for t in tests:
    print(t, "→", extract_info(t))"""