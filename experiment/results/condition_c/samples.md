# Reviewable sample of outputs

From run 1. 6 titles per intended label, loop and graph side by side on the same input.

## MINOR

**t0002** — original:

> Non Skid Base Dog Bed 24" Removable Cover Bolstered Plush Midnight Blue

- **loop** → PASS (route=-, score=12/12, calls=2, 1010 tok, $0.00344)  
  Bolstered Plush Dog Bed with Removable Cover, Non-Skid Base, Midnight Blue, 24"
- **graph** → FAIL_CAP (route=fix_consistency, score=10/12, calls=8, 4447 tok, $0.01575)  
  Dog Bed Non Skid Base Bolstered Plush Removable Cover Midnight Blue 24"

**t0005** — original:

> Desk Lamp Powder Coated Steel Slate Grey Adjustable Arm Eye Caring Dimmable 5W - Limited Stock

- **loop** → PASS (route=-, score=12/12, calls=4, 2285 tok, $0.00778)  
  Desk Lamp Powder Coated Steel Slate Grey Adjustable Arm Eye Caring Dimmable 5W
- **graph** → PASS (route=fix_attribute_preservation, score=12/12, calls=4, 2236 tok, $0.00762)  
  Desk Lamp - Powder Coated Steel, Slate Grey, Adjustable Arm, Eye Caring, Dimmable - 5W - Limited Stock

**t0007** — original:

> string lights shatterproof acrylic walnut brown plug in 50 ft

- **loop** → PASS (route=-, score=12/12, calls=2, 962 tok, $0.00320)  
  String Lights, Shatterproof Acrylic, Walnut Brown, Plug-In, 50 ft
- **graph** → PASS (route=done, score=12/12, calls=2, 967 tok, $0.00325)  
  String Lights, Shatterproof Acrylic, Walnut Brown, Plug-In, 50 ft

**t0008** — original:

> Set of 2 Copper Powder Coated Steel 24W Dimmable Desk Lamp Touch Control

- **loop** → FAIL_CAP (route=-, score=10/12, calls=8, 4503 tok, $0.01573)  
  Desk Lamp Copper Powder Coated Steel 24W Dimmable Touch Control Set of 2
- **graph** → FAIL_CAP (route=fix_consistency, score=10/12, calls=8, 4382 tok, $0.01515)  
  Desk Lamp Copper Powder Coated Steel 24W Dimmable Touch Control Set of 2

**t0010** — original:

> crew NECK t SHIRT tri BLEND terracotta TAGLESS soft HAND feel XS

- **loop** → PASS (route=-, score=12/12, calls=4, 2133 tok, $0.00715)  
  T-Shirt Crew Neck Tri-Blend Terracotta Tagless Soft Hand Feel XS
- **graph** → PASS (route=done, score=12/12, calls=2, 1002 tok, $0.00338)  
  Crew Neck T-Shirt Tri-Blend Terracotta Tagless Soft Hand Feel Size XS

**t0011** — original:

> Bluetooth Speaker Fabric Wrapped Charcoal 12 Hour Playtime IPX7 Waterproof Deep Bass 6 Pack - Fast Shipping

- **loop** → PASS (route=-, score=12/12, calls=2, 1111 tok, $0.00389)  
  Bluetooth Speaker Fabric Wrapped Charcoal IPX7 Waterproof Deep Bass 12 Hour Playtime - 6 Pack
- **graph** → PASS (route=done, score=12/12, calls=2, 1109 tok, $0.00387)  
  Bluetooth Speaker Fabric Wrapped Charcoal IPX7 Waterproof Deep Bass 12 Hour Playtime - 6 Pack

## MAJOR

**t0006** — original:

> Travel Tumbler Sky Blue Travel Tumbler Stainless Steel Travel Tumbler Vacuum Sealed Cup Holder Friendly

- **loop** → PASS (route=-, score=12/12, calls=4, 2230 tok, $0.00739)  
  Travel Tumbler Sky Blue Stainless Steel Vacuum Sealed Cup Holder Friendly
- **graph** → PASS (route=fix_searchability, score=12/12, calls=8, 4540 tok, $0.01521)  
  Travel Tumbler - Sky Blue, Stainless Steel, Vacuum Sealed, Cup Holder Friendly

**t0009** — original:

> Heavy Duty Deluxe Perfect for Everyday Use Throw Pillow Cover Velvet Terracotta Hidden Zipper Premium

- **loop** → PASS (route=-, score=12/12, calls=2, 1053 tok, $0.00357)  
  Velvet Throw Pillow Cover - Terracotta, Heavy Duty, Deluxe, Hidden Zipper, Premium
- **graph** → PASS (route=done, score=12/12, calls=2, 1038 tok, $0.00346)  
  Throw Pillow Cover Velvet Terracotta Hidden Zipper Heavy Duty Deluxe Premium

**t0012** — original:

> Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt Ivory Borosilicate Glass

- **loop** → PASS (route=-, score=12/12, calls=2, 1059 tok, $0.00366)  
  Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt
- **graph** → PASS (route=done, score=12/12, calls=2, 1061 tok, $0.00368)  
  Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt

**t0016** — original:

> CK Damascus Pattern Steel Cream Razo Full Chef Knife

- **loop** → FAIL_CAP (route=-, score=7/12, calls=8, 4299 tok, $0.01496)  
  Chef Knife CK Damascus Pattern Steel Cream Razor Full
- **graph** → FAIL_CAP (route=fix_consistency, score=10/12, calls=9, 4627 tok, $0.01653)  
  Chef Knife Damascus Pattern Steel Cream Handle

**t0017** — original:

> Power Bank Aluminum Shell Black Pass Through Charging 20000mAh Dual Port Black Aluminum Shell

- **loop** → PASS (route=-, score=12/12, calls=2, 1022 tok, $0.00351)  
  Power Bank Aluminum Shell Black Dual Port Pass Through Charging 20000mAh
- **graph** → PASS (route=done, score=12/12, calls=2, 1041 tok, $0.00370)  
  Power Bank Aluminum Shell Pass Through Charging Dual Port Black 20000mAh

**t0021** — original:

> Camping Tent White Camping Tent Ripstop Polyester Camping Tent Quick Pitch Mesh Vents Waterproof Fly

- **loop** → PASS (route=-, score=12/12, calls=4, 2182 tok, $0.00736)  
  Camping Tent White Ripstop Polyester Quick Pitch Mesh Vents Waterproof Fly
- **graph** → PASS (route=fix_searchability, score=12/12, calls=4, 2224 tok, $0.00778)  
  Camping Tent White Ripstop Polyester Quick Pitch Mesh Vents Waterproof Fly

## UNCLEAR

**t0001** — original:

> Set of 7 - Multi Purpose - Premium - Walnut Brown

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 951 tok, $0.00317)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=7/12, calls=2, 956 tok, $0.00322)  
  _(routed to human review)_

**t0003** — original:

> Universal Fit N120 - Shatterproof Acrylic - Aftermarket

- **loop** → HUMAN_REVIEW (route=-, score=12/12, calls=2, 989 tok, $0.00347)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=12/12, calls=2, 976 tok, $0.00334)  
  _(routed to human review)_

**t0004** — original:

> Accessory for F250 Series - Compact - New Arrival

- **loop** → HUMAN_REVIEW (route=-, score=10/12, calls=2, 955 tok, $0.00334)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=9/12, calls=2, 945 tok, $0.00324)  
  _(routed to human review)_

**t0013** — original:

> 3 Pack - Assorted Midnight Blue - Original Size - New

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 953 tok, $0.00323)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=7/12, calls=2, 958 tok, $0.00328)  
  _(routed to human review)_

**t0014** — original:

> Navy Compact - Replacement - G33

- **loop** → HUMAN_REVIEW (route=-, score=9/12, calls=2, 916 tok, $0.00309)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=9/12, calls=2, 931 tok, $0.00325)  
  _(routed to human review)_

**t0018** — original:

> 7 Pack - Assorted White - Full Size - Bulk

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 960 tok, $0.00334)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=6/12, calls=2, 951 tok, $0.00325)  
  _(routed to human review)_
