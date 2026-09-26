# Reviewable sample of outputs

From run 1. 6 titles per intended label, loop and graph side by side on the same input.

## MINOR

**t0001** — original:

> french PRESS stainless STEEL sand 4 level FILTER 6 QT

- **loop** → PASS (route=-, score=11/12, calls=2, 973 tok, $0.00337)  
  French Press Stainless Steel 4-Level Filter, 6 QT
- **graph** → PASS (route=MINOR, score=10/12, calls=4, 2274 tok, $0.00844)  
  French Press Stainless Steel 4-Level Filter 6 QT

**t0002** — original:

> Trekking Poles Carbon Fiber Charcoal Shock Absorbing Collapsible 24" - Sale

- **loop** → PASS (route=-, score=12/12, calls=2, 1010 tok, $0.00344)  
  Trekking Poles Carbon Fiber Charcoal Shock Absorbing Collapsible 24"
- **graph** → PASS (route=MAJOR, score=12/12, calls=3, 1419 tok, $0.00477)  
  Carbon Fiber Trekking Poles Charcoal Shock Absorbing Collapsible 24"

**t0004** — original:

> Resistance Band Set, Natural Latex, Blush Pink, Door Anchor, Carry Bag

- **loop** → PASS (route=-, score=12/12, calls=2, 997 tok, $0.00336)  
  Resistance Band Set, Natural Latex, Blush Pink, with Door Anchor and Carry Bag
- **graph** → PASS (route=MINOR, score=11/12, calls=3, 1403 tok, $0.00472)  
  Resistance Band Set, Natural Latex, Blush Pink, Door Anchor, Carry Bag

**t0013** — original:

> Cutting Board, Bamboo, Charcoal, Reversible, Juice Groove, 24"

- **loop** → PASS (route=-, score=12/12, calls=2, 986 tok, $0.00332)  
  Bamboo Cutting Board, Charcoal, Reversible, Juice Groove, 24"
- **graph** → PASS (route=MAJOR, score=11/12, calls=3, 1398 tok, $0.00475)  
  Reversible Bamboo Charcoal Cutting Board with Juice Groove, 24"

**t0015** — original:

> DESK LAMP POWDER COATED STEEL SAGE GREEN TOUCH CONTROL DIMMABLE 7W SET OF 4

- **loop** → PASS (route=-, score=12/12, calls=2, 1038 tok, $0.00345)  
  Desk Lamp, Powder Coated Steel, Sage Green, Touch Control, Dimmable, 7W - Set of 4
- **graph** → PASS (route=MAJOR, score=12/12, calls=3, 1434 tok, $0.00461)  
  Desk Lamp Powder Coated Steel Sage Green Touch Control Dimmable 7W Set of 4

**t0017** — original:

> Ergonomic Office Chair Breathable Mesh Silver Tilt Lock - New Arrival

- **loop** → PASS (route=-, score=10/12, calls=4, 2126 tok, $0.00720)  
  New Arrival Ergonomic Office Chair Breathable Mesh Silver Tilt Lock
- **graph** → PASS (route=MAJOR, score=12/12, calls=3, 1417 tok, $0.00491)  
  Ergonomic Office Chair - Breathable Mesh, Silver, Tilt Lock

## MAJOR

**t0003** — original:

> Great for Travel Ideal for Home and Office Versatile Blackout Curtains Triple Weave Polyester Sand Grommet Top Extra Durable

- **loop** → PASS (route=-, score=12/12, calls=2, 1077 tok, $0.00376)  
  Blackout Curtains - Triple Weave Polyester, Grommet Top, Sand, Extra Durable - Versatile for Home, Office, and Travel
- **graph** → PASS (route=MAJOR, score=11/12, calls=3, 1450 tok, $0.00484)  
  Blackout Curtains Triple Weave Polyester Sand Grommet Top

**t0005** — original:

> French Press for home and travel use with Borosilicate Glass construction in Slate Grey featuring 4 Level Filter and Non Slip Base available in 10 Qt

- **loop** → PASS (route=-, score=11/12, calls=2, 1106 tok, $0.00399)  
  French Press with Borosilicate Glass Construction, Slate Grey, 4 Level Filter, Non Slip Base, for Home and Travel Use - 10 Qt
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 382 tok, $0.00132)  
  _(routed to human review)_

**t0007** — original:

> Shatterproof Acrylic Sand Plug In Warm White 24" String Lights

- **loop** → PASS (route=-, score=9/12, calls=2, 1006 tok, $0.00360)  
  String Lights, Shatterproof Acrylic Sand, Plug In, Warm White, 24"
- **graph** → PASS (route=MINOR, score=11/12, calls=3, 1384 tok, $0.00474)  
  Shatterproof Acrylic Sand Plug-In Warm White String Lights 24"

**t0009** — original:

> Bolstered Plush Walnut Brown Non Skid Base 18" Dog Bed

- **loop** → PASS (route=-, score=11/12, calls=2, 1007 tok, $0.00354)  
  Dog Bed with Bolstered Plush Walnut Brown Design and Non-Skid Base, 18"
- **graph** → PASS (route=MINOR, score=11/12, calls=3, 1414 tok, $0.00498)  
  Bolstered Plush Walnut Brown Non-Skid Base Dog Bed 18"

**t0010** — original:

> Yoga Mat Graphite Yoga Mat Natural Rubber Yoga Mat Carrying Strap Odor Free Non Slip

- **loop** → PASS (route=-, score=12/12, calls=2, 1027 tok, $0.00341)  
  Yoga Mat - Natural Rubber, Graphite, Non-Slip, Odor Free, with Carrying Strap
- **graph** → PASS (route=MAJOR, score=11/12, calls=3, 1458 tok, $0.00492)  
  Graphite Yoga Mat, Natural Rubber, Non Slip, Odor Free, with Carrying Strap

**t0011** — original:

> Comfortable Super Soft Professional Grade Over Ear Headphones Protein Leather Navy Noise Isolating Perfect for Everyday Use

- **loop** → PASS (route=-, score=10/12, calls=2, 1060 tok, $0.00371)  
  Over Ear Headphones - Professional Grade, Super Soft Protein Leather, Noise Isolating, Navy
- **graph** → PASS (route=MAJOR, score=10/12, calls=3, 1467 tok, $0.00497)  
  Over Ear Headphones, Professional Grade, Protein Leather, Noise Isolating, Navy

## UNCLEAR

**t0006** — original:

> New Part Compatible with Y22 - White - Standard Size

- **loop** → HUMAN_REVIEW (route=-, score=8/12, calls=2, 956 tok, $0.00332)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 337 tok, $0.00115)  
  _(routed to human review)_

**t0008** — original:

> Accessory for P600 Series - Original Size - Hot Item

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 950 tok, $0.00331)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 328 tok, $0.00106)  
  _(routed to human review)_

**t0012** — original:

> Accessory for Gen 4 Series - Mini - Sale

- **loop** → HUMAN_REVIEW (route=-, score=7/12, calls=2, 952 tok, $0.00331)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 334 tok, $0.00112)  
  _(routed to human review)_

**t0018** — original:

> Set of 4 - Assorted Blush Pink - Full Size - New

- **loop** → HUMAN_REVIEW (route=-, score=9/12, calls=2, 983 tok, $0.00349)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 329 tok, $0.00104)  
  _(routed to human review)_

**t0028** — original:

> OEM Part Compatible with B24 - Forest Green - Original Size

- **loop** → HUMAN_REVIEW (route=-, score=6/12, calls=2, 975 tok, $0.00344)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 330 tok, $0.00105)  
  _(routed to human review)_

**t0030** — original:

> Universal Fit AV12 - Shatterproof Acrylic - OEM

- **loop** → HUMAN_REVIEW (route=-, score=9/12, calls=2, 980 tok, $0.00346)  
  _(routed to human review)_
- **graph** → HUMAN_REVIEW (route=UNCLEAR, score=-/12, calls=1, 343 tok, $0.00117)  
  _(routed to human review)_
