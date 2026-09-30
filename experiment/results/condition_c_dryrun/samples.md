# Reviewable sample of outputs

From run 1. 6 titles per intended label, loop and graph side by side on the same input.

## MINOR

**t0002** — original:

> Non Skid Base Dog Bed 24" Removable Cover Bolstered Plush Midnight Blue

- **loop** → PASS (route=-, score=12/12, calls=2, 1002 tok, $0.00336)  
  Bolstered Plush Dog Bed with Removable Cover, Non-Skid Base, Midnight Blue, 24"
- **graph** → PASS (route=done, score=12/12, calls=2, 1002 tok, $0.00336)  
  Bolstered Plush Dog Bed with Removable Cover, Non-Skid Base, Midnight Blue, 24"

**t0005** — original:

> Desk Lamp Powder Coated Steel Slate Grey Adjustable Arm Eye Caring Dimmable 5W - Limited Stock

- **loop** → PASS (route=-, score=12/12, calls=4, 2240 tok, $0.00755)  
  Desk Lamp Powder Coated Steel Slate Grey Adjustable Arm Eye Caring Dimmable 5W
- **graph** → PASS (route=fix_attribute_preservation, score=12/12, calls=4, 2240 tok, $0.00766)  
  Desk Lamp - Powder Coated Steel, Slate Grey, Adjustable Arm, Eye Caring, Dimmable - 5W - Limited Stock

**t0007** — original:

> string lights shatterproof acrylic walnut brown plug in 50 ft

- **loop** → FAIL_CAP (route=-, score=11/12, calls=8, 4251 tok, $0.01474)  
  String Lights Shatterproof Acrylic Walnut Brown Plug-In 50 ft
- **graph** → FAIL_CAP (route=fix_consistency, score=10/12, calls=8, 4229 tok, $0.01473)  
  String Lights Shatterproof Acrylic Walnut Brown Plug-In 50 ft

**t0008** — original:

> Set of 2 Copper Powder Coated Steel 24W Dimmable Desk Lamp Touch Control

- **loop** → FAIL_CAP (route=-, score=10/12, calls=8, 4468 tok, $0.01538)  
  Desk Lamp Copper Powder Coated Steel 24W Dimmable Touch Control Set of 2
- **graph** → FAIL_CAP (route=fix_consistency, score=10/12, calls=8, 4426 tok, $0.01559)  
  Desk Lamp Copper Powder Coated Steel 24W Dimmable Touch Control Set of 2

**t0010** — original:

> crew NECK t SHIRT tri BLEND terracotta TAGLESS soft HAND feel XS

- **loop** → PASS (route=-, score=12/12, calls=8, 4441 tok, $0.01543)  
  T-Shirt, Crew Neck, Tri-Blend, Terracotta, Tagless, Soft Hand Feel, XS
- **graph** → PASS (route=fix_consistency, score=12/12, calls=4, 2172 tok, $0.00775)  
  T-Shirt Crew Neck Tri-Blend Terracotta Tagless Soft Hand Feel XS

**t0011** — original:

> Bluetooth Speaker Fabric Wrapped Charcoal 12 Hour Playtime IPX7 Waterproof Deep Bass 6 Pack - Fast Shipping

- **loop** → PASS (route=-, score=12/12, calls=2, 1108 tok, $0.00386)  
  Bluetooth Speaker Fabric Wrapped Charcoal IPX7 Waterproof Deep Bass 12 Hour Playtime - 6 Pack
- **graph** → PASS (route=done, score=12/12, calls=2, 1111 tok, $0.00389)  
  Bluetooth Speaker Fabric Wrapped Charcoal IPX7 Waterproof Deep Bass 12 Hour Playtime - 6 Pack

## MAJOR

**t0006** — original:

> Travel Tumbler Sky Blue Travel Tumbler Stainless Steel Travel Tumbler Vacuum Sealed Cup Holder Friendly

- **loop** → PASS (route=-, score=12/12, calls=6, 3360 tok, $0.01118)  
  Travel Tumbler Sky Blue Stainless Steel Vacuum Sealed Cup Holder Friendly
- **graph** → FAIL_CAP (route=fix_searchability, score=11/12, calls=8, 4569 tok, $0.01550)  
  Travel Tumbler Sky Blue, Stainless Steel, Vacuum Sealed, Cup Holder Friendly

**t0009** — original:

> Heavy Duty Deluxe Perfect for Everyday Use Throw Pillow Cover Velvet Terracotta Hidden Zipper Premium

- **loop** → PASS (route=-, score=12/12, calls=8, 4530 tok, $0.01539)  
  Throw Pillow Cover Velvet Terracotta Hidden Zipper Heavy Duty Deluxe Premium
- **graph** → PASS (route=done, score=12/12, calls=2, 1086 tok, $0.00382)  
  Velvet Throw Pillow Cover - Terracotta, Hidden Zipper, Heavy Duty Deluxe Premium, Perfect for Everyday Use

**t0012** — original:

> Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt Ivory Borosilicate Glass

- **loop** → PASS (route=-, score=12/12, calls=2, 1059 tok, $0.00366)  
  Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt
- **graph** → PASS (route=done, score=12/12, calls=2, 1059 tok, $0.00366)  
  Storage Container Set Borosilicate Glass Ivory Freezer Safe Stackable Airtight 4 Qt

**t0016** — original:

> CK Damascus Pattern Steel Cream Razo Full Chef Knife

- **loop** → PASS (route=-, score=12/12, calls=2, 973 tok, $0.00333)  
  Chef Knife - Damascus Pattern Cream Razor Steel - Full Size
- **graph** → FAIL_CAP (route=fix_groundedness, score=10/12, calls=9, 4735 tok, $0.01764)  
  Chef Knife Damascus Pattern Steel Cream Razor Full

**t0017** — original:

> Power Bank Aluminum Shell Black Pass Through Charging 20000mAh Dual Port Black Aluminum Shell

- **loop** → PASS (route=-, score=12/12, calls=2, 1020 tok, $0.00349)  
  Power Bank Aluminum Shell Black Dual Port Pass Through Charging 20000mAh
- **graph** → PASS (route=done, score=12/12, calls=2, 1030 tok, $0.00359)  
  Power Bank Aluminum Shell Black Dual Port Pass Through Charging 20000mAh

**t0021** — original:

> Camping Tent White Camping Tent Ripstop Polyester Camping Tent Quick Pitch Mesh Vents Waterproof Fly

- **loop** → PASS (route=-, score=12/12, calls=2, 1026 tok, $0.00339)  
  Camping Tent - White Ripstop Polyester, Quick Pitch, Mesh Vents, Waterproof Fly
- **graph** → PASS (route=done, score=12/12, calls=2, 1036 tok, $0.00349)  
  Camping Tent - White Ripstop Polyester, Quick Pitch, Mesh Vents, Waterproof Fly

## UNCLEAR

**t0001** — original:

> Set of 7 - Multi Purpose - Premium - Walnut Brown

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 964 tok, $0.00331)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=6/12, calls=2, 956 tok, $0.00322)  
  _(routed to human review)_

**t0003** — original:

> Universal Fit N120 - Shatterproof Acrylic - Aftermarket

- **loop** → HUMAN_REVIEW (route=-, score=12/12, calls=2, 981 tok, $0.00339)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=fix_groundedness, score=7/12, calls=8, 4191 tok, $0.01425)  
  _(routed to human review)_

**t0004** — original:

> Accessory for F250 Series - Compact - New Arrival

- **loop** → HUMAN_REVIEW (route=-, score=9/12, calls=2, 942 tok, $0.00321)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=10/12, calls=2, 948 tok, $0.00327)  
  _(routed to human review)_

**t0013** — original:

> 3 Pack - Assorted Midnight Blue - Original Size - New

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 950 tok, $0.00320)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=7/12, calls=2, 963 tok, $0.00331)  
  _(routed to human review)_

**t0014** — original:

> Navy Compact - Replacement - G33

- **loop** → HUMAN_REVIEW (route=-, score=9/12, calls=2, 930 tok, $0.00323)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=9/12, calls=2, 939 tok, $0.00332)  
  _(routed to human review)_

**t0018** — original:

> 7 Pack - Assorted White - Full Size - Bulk

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 959 tok, $0.00333)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=human_review, score=7/12, calls=2, 955 tok, $0.00329)  
  _(routed to human review)_
