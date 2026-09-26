"""Generate the 1,000-title dataset.

Fictional products only. No real brands, no scraped or proprietary catalog data.

Diversity is the point: 48 product types across 12 departments, each with its own
attribute pools, combined with 8 distinct corruption styles per difficulty class.
A handful of templates would produce near-duplicates, which would make the
per-category cost estimates meaningless.

    python generate_titles.py            # writes titles_1000.json
    python generate_titles.py --report   # diversity report only, writes nothing
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

SEED = 20260926
N_TOTAL = 1000
MIX = {"MINOR": 400, "MAJOR": 300, "UNCLEAR": 300}

HERE = Path(__file__).parent

COLORS = [
    "Black", "White", "Navy", "Charcoal", "Slate Grey", "Ivory", "Sage Green",
    "Olive", "Burgundy", "Teal", "Mustard", "Blush Pink", "Sky Blue", "Cream",
    "Walnut Brown", "Rust", "Lavender", "Forest Green", "Sand", "Graphite",
    "Copper", "Silver", "Midnight Blue", "Terracotta",
]

# Size pools are deliberately narrow and product-appropriate. A shared
# catch-all pool produces implausible pairings (a 10 Qt French press, a 6"
# floor lamp), and an implausible spec is a legitimate reason for a classifier
# to flag a title as unreliable - which would contaminate the routing measurement.
SIZE_POOLS = {
    "volume_bottle": ["16oz", "20oz", "24oz", "32oz", "40oz", "64oz", "1L", "1.5L"],
    "volume_mug": ["8oz", "10oz", "12oz", "14oz", "16oz", "20oz"],
    "volume_press": ["12oz", "17oz", "20oz", "34oz", "51oz", "1L"],
    "volume_fountain": ["50oz", "70oz", "100oz", "2L", "3L"],
    "apparel": ["XS", "S", "M", "L", "XL", "2XL", "3XL"],
    "shoe": ["Size 6", "Size 7", "Size 8", "Size 9", "Size 10", "Size 11", "Size 12"],
    "in_pan": ['8"', '10"', '12"', '14"'],
    "in_knife": ['6"', '7"', '8"', '10"'],
    "in_board": ['12"', '14"', '16"', '18"'],
    "in_pillow": ['16"', '18"', '20"', '22"', '24"'],
    "in_post": ['20"', '26"', '32"', '36"'],
    "in_basket": ['10"', '12"', '14"', '16"'],
    "in_floorlamp": ['58"', '60"', '63"', '65"', '70"'],
    "in_pole": ['43"', '47"', '51"', '54"'],
    "in_mat": ['68"', '72"', '74"'],
    "in_roller": ['12"', '18"', '24"', '36"'],
    "in_dogbed": ['24"', '30"', '36"', '42"', '48"'],
    "in_cloth": ['12"', '16"'],
    "in_notebook": ['5x8"', '6x9"', '8.5x11"'],
    "ft_cable": ["1 ft", "3 ft", "6 ft", "10 ft"],
    "ft_lights": ["25 ft", "50 ft", "100 ft"],
    "watt": ["5W", "7W", "9W", "12W", "15W", "18W", "24W", "40W", "60W"],
    "weight": ["5 lb", "10 lb", "15 lb", "20 lb", "25 lb", "35 lb", "50 lb"],
    "area": ["2x3 ft", "3x5 ft", "4x6 ft", "5x8 ft", "8x10 ft"],
    "cap_pot": ["1 Qt", "2 Qt", "3 Qt", "4 Qt", "6 Qt"],
    "cap_bowl": ["3 Qt", "5 Qt", "8 Qt"],
    "cap_box": ["1 Qt", "2 Qt", "4 Qt"],
    "cap_cooler": ["6 Qt", "12 Qt", "20 Qt", "30 Qt"],
}

PACKS = ["2 Pack", "3 Pack", "4 Pack", "6 Pack", "8 Pack", "12 Pack", "Set of 2", "Set of 4"]

# (noun, department, materials, size_pool, features)
PRODUCTS: list[tuple] = [
    ("Insulated Water Bottle", "drinkware", ["Stainless Steel", "Tritan", "Copper Lined"], "volume_bottle",
     ["Leak Proof", "Wide Mouth", "Double Wall", "BPA Free", "Sweat Proof"]),
    ("Travel Tumbler", "drinkware", ["Stainless Steel", "Ceramic Coated"], "volume_bottle",
     ["Spill Resistant", "Cup Holder Friendly", "Vacuum Sealed"]),
    ("Coffee Mug", "drinkware", ["Stoneware", "Porcelain", "Enamel"], "volume_mug",
     ["Microwave Safe", "Dishwasher Safe", "Handle Grip"]),
    ("French Press", "kitchen", ["Borosilicate Glass", "Stainless Steel"], "volume_press",
     ["4 Level Filter", "Heat Resistant", "Non Slip Base"]),
    ("Frying Pan", "kitchen", ["Cast Iron", "Hard Anodized Aluminum", "Ceramic Coated"], "in_pan",
     ["Non Stick", "Oven Safe", "Induction Ready", "Riveted Handle"]),
    ("Saucepan", "kitchen", ["Tri Ply Stainless Steel", "Enameled Cast Iron"], "cap_pot",
     ["Tempered Glass Lid", "Dishwasher Safe", "Even Heat Base"]),
    ("Cutting Board", "kitchen", ["Acacia Wood", "Bamboo", "Composite"], "in_board",
     ["Juice Groove", "Reversible", "Knife Friendly"]),
    ("Chef Knife", "kitchen", ["High Carbon Steel", "Damascus Pattern Steel"], "in_knife",
     ["Full Tang", "Ergonomic Handle", "Razor Sharp Edge"]),
    ("Mixing Bowl Set", "kitchen", ["Stainless Steel", "Melamine"], "cap_bowl",
     ["Nesting", "Non Slip Base", "Pour Spout"]),
    ("Storage Container Set", "kitchen", ["Borosilicate Glass", "BPA Free Plastic"], "cap_box",
     ["Airtight", "Stackable", "Freezer Safe"]),
    ("Running Shoes", "footwear", ["Breathable Mesh", "Knit Upper"], "shoe",
     ["Cushioned Midsole", "Arch Support", "Lightweight", "Reflective Trim"]),
    ("Hiking Boots", "footwear", ["Full Grain Leather", "Suede and Mesh"], "shoe",
     ["Waterproof", "Ankle Support", "Vibram Style Outsole"]),
    ("Slip On Sneakers", "footwear", ["Canvas", "Recycled Knit"], "shoe",
     ["Memory Foam Insole", "Machine Washable"]),
    ("Crew Neck T Shirt", "apparel", ["Organic Cotton", "Cotton Blend", "Tri Blend"], "apparel",
     ["Pre Shrunk", "Tagless", "Relaxed Fit", "Soft Hand Feel"]),
    ("Fleece Hoodie", "apparel", ["Sherpa Lined Fleece", "Cotton Fleece"], "apparel",
     ["Kangaroo Pocket", "Drawstring Hood", "Ribbed Cuffs"]),
    ("Rain Jacket", "apparel", ["Ripstop Nylon", "Recycled Polyester"], "apparel",
     ["Waterproof", "Packable", "Sealed Seams", "Adjustable Hood"]),
    ("Merino Wool Socks", "apparel", ["Merino Wool Blend"], "apparel",
     ["Cushioned Heel", "Moisture Wicking", "Seamless Toe"]),
    ("Yoga Leggings", "apparel", ["Nylon Spandex", "Recycled Poly Blend"], "apparel",
     ["High Waisted", "Squat Proof", "Side Pockets", "Four Way Stretch"]),
    ("Wireless Earbuds", "electronics", ["Matte Finish ABS"], None,
     ["Active Noise Cancelling", "24 Hour Battery", "Touch Controls", "IPX5 Water Resistant"]),
    ("Bluetooth Speaker", "electronics", ["Fabric Wrapped"], None,
     ["12 Hour Playtime", "IPX7 Waterproof", "Deep Bass", "Pairs in Stereo"]),
    ("Over Ear Headphones", "electronics", ["Protein Leather"], None,
     ["Noise Isolating", "40mm Drivers", "Foldable", "Inline Mic"]),
    ("USB C Charging Cable", "electronics", ["Braided Nylon"], "ft_cable",
     ["Fast Charge", "Reinforced Connector", "Data Sync"]),
    ("Power Bank", "electronics", ["Aluminum Shell"], None,
     ["20000mAh", "Dual Port", "Pass Through Charging", "LED Indicator"]),
    ("Laptop Stand", "office", ["Anodized Aluminum", "Bamboo"], None,
     ["Adjustable Height", "Ventilated", "Foldable", "Non Slip Pads"]),
    ("Desk Lamp", "office", ["Powder Coated Steel"], "watt",
     ["Dimmable", "Adjustable Arm", "Touch Control", "Eye Caring"]),
    ("Ergonomic Office Chair", "office", ["Breathable Mesh"], None,
     ["Lumbar Support", "Adjustable Armrests", "Tilt Lock", "360 Swivel"]),
    ("Notebook", "office", ["Recycled Paper", "Vegan Leather Cover"], "in_notebook",
     ["Dotted Pages", "Lay Flat Binding", "Elastic Closure"]),
    ("Gel Pen", "office", ["Matte Barrel"], None,
     ["0.5mm Tip", "Quick Dry Ink", "Smudge Resistant"]),
    ("LED Bulb", "lighting", ["Frosted Glass"], "watt",
     ["Dimmable", "2700K Warm White", "5000K Daylight", "800 Lumens", "E26 Base"]),
    ("String Lights", "lighting", ["Shatterproof Acrylic"], "ft_lights",
     ["Outdoor Rated", "Warm White", "Plug In", "Weatherproof"]),
    ("Floor Lamp", "lighting", ["Brushed Brass", "Matte Black Steel"], "in_floorlamp",
     ["Adjustable Shade", "Foot Switch", "Weighted Base"]),
    ("Throw Blanket", "home", ["Chunky Knit", "Sherpa Fleece", "Cotton Waffle"], "area",
     ["Machine Washable", "Oversized", "Reversible"]),
    ("Area Rug", "home", ["Jute", "Low Pile Polypropylene", "Wool Blend"], "area",
     ["Stain Resistant", "Non Shedding", "Pet Friendly"]),
    ("Throw Pillow Cover", "home", ["Linen Blend", "Boucle", "Velvet"], "in_pillow",
     ["Hidden Zipper", "Double Sided", "Fade Resistant"]),
    ("Blackout Curtains", "home", ["Triple Weave Polyester"], "area",
     ["Thermal Insulated", "Grommet Top", "Noise Reducing"]),
    ("Storage Basket", "home", ["Seagrass", "Cotton Rope", "Felt"], "in_basket",
     ["Collapsible", "Reinforced Handles", "Lined Interior"]),
    ("Yoga Mat", "fitness", ["TPE Foam", "Natural Rubber", "Cork"], "in_mat",
     ["6mm Thick", "Non Slip", "Carrying Strap", "Odor Free"]),
    ("Adjustable Dumbbell", "fitness", ["Cast Iron", "Neoprene Coated"], "weight",
     ["Quick Lock", "Knurled Grip", "Space Saving"]),
    ("Resistance Band Set", "fitness", ["Natural Latex"], None,
     ["5 Levels", "Door Anchor", "Carry Bag", "Snap Resistant"]),
    ("Foam Roller", "fitness", ["EVA Foam", "High Density Foam"], "in_roller",
     ["Textured Surface", "Deep Tissue", "Lightweight"]),
    ("Camping Tent", "outdoor", ["Ripstop Polyester"], None,
     ["2 Person", "4 Person", "Waterproof Fly", "Quick Pitch", "Mesh Vents"]),
    ("Sleeping Bag", "outdoor", ["Hollow Fiber Fill", "Down Alternative"], None,
     ["20F Rated", "Mummy Shape", "Compression Sack"]),
    ("Insulated Cooler Bag", "outdoor", ["600D Polyester"], "cap_cooler",
     ["Leak Proof Liner", "Shoulder Strap", "Keeps Cold 24 Hours"]),
    ("Trekking Poles", "outdoor", ["7075 Aluminum", "Carbon Fiber"], "in_pole",
     ["Collapsible", "Cork Grip", "Shock Absorbing"]),
    ("Dog Bed", "pet", ["Orthopedic Memory Foam", "Bolstered Plush"], "in_dogbed",
     ["Removable Cover", "Machine Washable", "Non Skid Base"]),
    ("Pet Water Fountain", "pet", ["BPA Free Plastic", "Ceramic"], "volume_fountain",
     ["Ultra Quiet Pump", "Carbon Filter", "LED Water Level"]),
    ("Cat Scratching Post", "pet", ["Sisal Rope", "Carpet Wrapped"], "in_post",
     ["Weighted Base", "Sturdy", "Includes Toy"]),
    ("Car Phone Mount", "auto", ["Reinforced ABS"], None,
     ["Dashboard Mount", "Vent Clip", "360 Rotation", "One Hand Release"]),
    ("Microfiber Cleaning Cloth", "auto", ["Split Microfiber"], "in_cloth",
     ["Lint Free", "Streak Free", "Machine Washable"]),
]

CODES = ["X200", "A14", "MK7", "Series 7", "V3", "Pro 9", "RT-40", "Gen 4", "ZX5", "N120",
         "T8", "HD2", "C45", "Model 22", "S3", "K90", "E11", "P600", "L7", "B24",
         "QX9", "M15", "TR-2", "D80", "Type C4", "R7S", "AV12", "G33", "XL-6", "F250",
         "NS4", "W90", "J17", "U5", "PT-8", "H600", "Z14", "CR3", "Y22", "VX1"]

# Extra entropy for the UNCLEAR class. None of these name a product.
UNITS = ["Standard Size", "One Size", "Regular", "Compact", "Full Size", "Mini",
         "Large", "Universal Size", "Adjustable", "Original Size"]
CONDITIONS = ["New", "Open Box", "Bulk", "OEM", "Aftermarket", "Refurbished",
              "Genuine", "Replacement", "Spare", "Factory Sealed"]

FILLER = ["Fast Shipping", "Best Seller", "Free Delivery", "New Arrival", "Top Rated",
          "Limited Stock", "Hot Item", "Great Gift", "Must Have", "Sale"]

MARKETING = ["Premium", "Ultra", "Professional Grade", "Heavy Duty", "Luxury", "Deluxe",
             "Super Soft", "Extra Durable", "High Quality", "Comfortable", "Versatile",
             "Perfect for Everyday Use", "Ideal for Home and Office", "Great for Travel"]


def pick_parts(rng: random.Random) -> dict:
    noun, dept, materials, size_pool, features = rng.choice(PRODUCTS)
    return {
        "noun": noun,
        "dept": dept,
        "size_pool": size_pool,
        "material": rng.choice(materials),
        "color": rng.choice(COLORS),
        "size": rng.choice(SIZE_POOLS[size_pool]) if size_pool else None,
        "pack": rng.choice(PACKS) if rng.random() < 0.28 else None,
        "features": rng.sample(features, k=min(len(features), rng.randint(1, 3))),
        "code": rng.choice(CODES),
    }


def canonical(p: dict) -> list[str]:
    bits = [p["noun"], p["material"], p["color"]]
    bits += p["features"]
    if p["size"]:
        bits.append(p["size"])
    if p["pack"]:
        bits.append(p["pack"])
    return bits


# ---------------------------------------------------------------- MINOR
# Product obvious; wording, casing, punctuation or order need fixing.

def minor_allcaps(p, rng):
    return " ".join(canonical(p)).upper()


def minor_lowercase(p, rng):
    return " ".join(canonical(p)).lower()


def minor_dashes(p, rng):
    return " - ".join(canonical(p))


def minor_commas(p, rng):
    return ", ".join(canonical(p))


def minor_filler(p, rng):
    return " ".join(canonical(p)) + " - " + rng.choice(FILLER)


def minor_shuffled(p, rng):
    bits = canonical(p)
    rng.shuffle(bits)
    return " ".join(bits)


def minor_spacing(p, rng):
    return "  ".join(canonical(p)).replace(" ", "  ", 2)


def minor_mixedcase(p, rng):
    return " ".join(w.upper() if i % 2 else w.lower() for i, w in enumerate(" ".join(canonical(p)).split()))


# ---------------------------------------------------------------- MAJOR
# Product identifiable from the text, but the title needs restructuring.
# No new information is ever required to fix these.

def major_specdump(p, rng):
    bits = [p["material"], p["color"]] + p["features"]
    if p["size"]:
        bits.append(p["size"])
    return " ".join(bits) + " " + p["noun"]


def major_keyword_stuff(p, rng):
    head = p["noun"]
    return f"{head} {p['color']} {head} {p['material']} {head} " + " ".join(p["features"])


def major_marketing_bloat(p, rng):
    return (" ".join(rng.sample(MARKETING, 3)) + " " + p["noun"] + " " + p["material"] + " "
            + p["color"] + " " + " ".join(p["features"]) + " " + rng.choice(MARKETING))


def major_runon(p, rng):
    return (f"{p['noun']} for home and travel use with {p['material']} construction in "
            f"{p['color']} featuring " + " and ".join(p["features"])
            + (f" available in {p['size']}" if p["size"] else ""))


def major_pipes(p, rng):
    bits = [p["material"], p["color"]] + p["features"] + ([p["size"]] if p["size"] else [])
    return " | ".join(bits) + " | " + p["noun"]


def major_size_first(p, rng):
    """Multi-size set listed before the product noun. Sizes come from the
    product's own pool, so a 3-size set is only ever plausible sizes."""
    pool = SIZE_POOLS.get(p["size_pool"]) if p["size_pool"] else None
    if pool and len(pool) >= 2:
        k = min(3, len(pool))
        sizes = sorted(rng.sample(pool, k), key=pool.index)
        lead = " ".join(sizes) + " " + (p["pack"] or f"{k}pc Set")
    else:
        lead = p["pack"] or "3pc Set"
    return f"{lead} {p['noun']} {p['material']} {p['color']} " + " ".join(p["features"])


def major_duplicated(p, rng):
    return " ".join(canonical(p) + [p["color"], p["material"]])


def major_abbrev(p, rng):
    abb = "".join(w[0] for w in p["noun"].split())
    return f"{abb} {p['material']} {p['color']} " + " ".join(f[:4] for f in p["features"]) + " " + p["noun"]


# ---------------------------------------------------------------- UNCLEAR
# Core product NOT identifiable. Any complete rewrite would require invention.

def unclear_premium(p, rng):
    return (f"{rng.choice(MARKETING)} Quality Item - Model {p['code']} - "
            f"{rng.choice(FILLER)}")


def unclear_part(p, rng):
    return (f"{rng.choice(CONDITIONS)} Part Compatible with {p['code']} - "
            f"{p['color']} - {rng.choice(UNITS)}")


def unclear_assorted(p, rng):
    return (f"{p['pack'] or str(rng.randint(2, 12)) + ' Pack'} - Assorted "
            f"{p['color']} - {rng.choice(UNITS)} - {rng.choice(CONDITIONS)}")


def unclear_color_size(p, rng):
    return f"{p['color']} {p['size'] or rng.choice(UNITS)} - {rng.choice(CONDITIONS)} - {p['code']}"


def unclear_accessory(p, rng):
    return (f"Accessory for {p['code']} Series - {rng.choice(UNITS)} - "
            f"{rng.choice(FILLER)}")


def unclear_universal(p, rng):
    return (f"Universal Fit {p['code']} - {p['material']} - {rng.choice(CONDITIONS)}")


def unclear_code_color(p, rng):
    return f"{p['code']} - {p['color']} - {p['size'] or rng.choice(UNITS)} - {rng.choice(FILLER)}"


def unclear_multipurpose(p, rng):
    return (f"Set of {rng.randint(2, 12)} - Multi Purpose - {rng.choice(MARKETING)} - "
            f"{p['color']}")


STYLES = {
    "MINOR": [minor_allcaps, minor_lowercase, minor_dashes, minor_commas,
              minor_filler, minor_shuffled, minor_spacing, minor_mixedcase],
    "MAJOR": [major_specdump, major_keyword_stuff, major_marketing_bloat, major_runon,
              major_pipes, major_size_first, major_duplicated, major_abbrev],
    "UNCLEAR": [unclear_premium, unclear_part, unclear_assorted, unclear_color_size,
                unclear_accessory, unclear_universal, unclear_code_color, unclear_multipurpose],
}


def generate() -> list[dict]:
    rng = random.Random(SEED)
    seen: set[str] = set()
    # Also dedup on token set: a shuffled permutation is an exact-string miss but
    # a genuine near-duplicate, and can even land in a different difficulty class.
    seen_tokens: set[frozenset] = set()
    rows: list[dict] = []
    for label, n in MIX.items():
        styles = STYLES[label]
        made = 0
        guard = 0
        while made < n and guard < n * 200:
            guard += 1
            p = pick_parts(rng)
            style = styles[made % len(styles)]
            title = " ".join(style(p, rng).split()) if style is not minor_spacing else style(p, rng)
            key = title.lower().strip()
            tokens = frozenset(key.split())
            if key in seen or tokens in seen_tokens or len(title) < 8:
                continue
            seen.add(key)
            seen_tokens.add(tokens)
            rows.append({
                "intended_label": label,
                "style": style.__name__,
                "department": p["dept"],
                "title": title,
            })
            made += 1
        if made < n:
            raise RuntimeError(f"could not generate {n} unique {label} titles")
    rng.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["id"] = f"t{i:04d}"
    return [{"id": r["id"], "intended_label": r["intended_label"], "style": r["style"],
             "department": r["department"], "title": r["title"]} for r in rows]


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def report(rows: list[dict]) -> None:
    print(f"total: {len(rows)}   unique titles: {len({r['title'].lower() for r in rows})}")
    print("\nby intended label:")
    for k, v in sorted(Counter(r["intended_label"] for r in rows).items()):
        print(f"  {k:<9} {v:>4}  ({v / len(rows) * 100:.0f}%)")
    print("\nby style (8 per class):")
    for label in MIX:
        c = Counter(r["style"] for r in rows if r["intended_label"] == label)
        print(f"  {label}: " + ", ".join(f"{k.split('_', 1)[1]}={v}" for k, v in sorted(c.items())))
    print("\nby department:")
    c = Counter(r["department"] for r in rows)
    print("  " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    print(f"\ndistinct product nouns used: {len({r['title'] for r in rows})} titles from {len(PRODUCTS)} product types")

    lens = sorted(len(r["title"]) for r in rows)
    print(f"title length chars: min={lens[0]} p50={lens[len(lens) // 2]} p90={lens[int(len(lens) * .9)]} max={lens[-1]}")

    toks = [(r["id"], set(r["title"].lower().split())) for r in rows]
    high = 0
    worst = (0.0, "", "")
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            s = jaccard(toks[i][1], toks[j][1])
            if s >= 0.8:
                high += 1
            if s > worst[0]:
                worst = (s, toks[i][0], toks[j][0])
    pairs = len(toks) * (len(toks) - 1) // 2
    print(f"\nnear-duplicate check (token Jaccard >= 0.80): {high} of {pairs} pairs ({high / pairs * 100:.3f}%)")
    print(f"most similar pair: {worst[1]} / {worst[2]} at {worst[0]:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print the report without writing")
    args = ap.parse_args()

    rows = generate()
    report(rows)
    if not args.report:
        out = HERE / "titles_1000.json"
        out.write_text(json.dumps({
            "_note": "Fictional products, generated programmatically. intended_label and style "
                     "are ground truth for post-hoc analysis ONLY; both are stripped before any "
                     "model call. Seed and generator are committed for reproducibility.",
            "seed": SEED,
            "mix": MIX,
            "titles": rows,
        }, indent=2), encoding="utf-8")
        print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
