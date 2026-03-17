"""
build_gold_set_uc4.py
Builds the pre-registered 100-item gold set for UC4: Product Review Sentiment
Saves to: data/gold_sets/uc4_product_review_sentiment.csv

Gold set structure:
  40 POSITIVE reviews
  40 NEGATIVE reviews
  20 NEUTRAL reviews  (harder to classify — deliberate imbalance mirrors real world)

  Stratified split: 70 train / 30 test, proportional per class
  POSITIVE: 28 train / 12 test
  NEGATIVE: 28 train / 12 test
  NEUTRAL:  14 train /  6 test

Categories:
  Electronics, Clothing, Food & Grocery, Home & Kitchen, Books, Software

Difficulty levels:
  easy   — clear sentiment, unambiguous language
  medium — mixed signals, some hedging
  hard   — sarcasm, faint praise, double negatives, NEUTRAL edge cases

PRE-REGISTRATION DATE: March 3, 2026
DO NOT MODIFY after benchmark execution begins.
"""

import csv
import os
import json
from datetime import datetime

OUTPUT_DIR  = "data/gold_sets"
OUTPUT_FILE = "uc4_product_review_sentiment.csv"
META_FILE   = "uc4_metadata.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GOLD_SET = [

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Electronics (8 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_001", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "Absolutely love this laptop. Fast, lightweight, and the battery lasts all day. Best purchase I have made this year.",
        "notes": "Clear positive, multiple praise signals"
    },
    {
        "id": "UC4_002", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "The headphones arrived quickly and sound incredible. Deep bass, clear highs. Totally worth the price.",
        "notes": "Unambiguous positive"
    },
    {
        "id": "UC4_003", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "medium",
        "text": "Setup took a while but once it was running the smart TV is fantastic. Picture quality is stunning.",
        "notes": "Minor negative (setup time) but overall positive"
    },
    {
        "id": "UC4_004", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "medium",
        "text": "A bit pricier than alternatives but the build quality is exceptional. You get what you pay for.",
        "notes": "Price acknowledgment but positive conclusion"
    },
    {
        "id": "UC4_005", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "hard",
        "text": "Not the cheapest option and the manual is terrible but honestly this camera takes photos that make me look like a professional.",
        "notes": "Two negatives before strong positive — hard to classify"
    },
    {
        "id": "UC4_006", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "Five stars. This keyboard is a dream to type on. Clicky, responsive, and looks great on my desk.",
        "notes": "Explicit five stars"
    },
    {
        "id": "UC4_007", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "medium",
        "text": "I was sceptical at first but this wireless charger works perfectly with my phone. No more fumbling with cables at night.",
        "notes": "Initial scepticism resolved positively"
    },
    {
        "id": "UC4_008", "label": "POSITIVE",
        "category": "Electronics", "difficulty": "hard",
        "text": "The fan is louder than I expected and it runs warm under load but for the price this gaming laptop outperforms everything else I tested.",
        "notes": "Specific complaints but clear positive verdict"
    },

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Clothing (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_009", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "Perfect fit, beautiful colour, and the fabric feels luxurious. I already ordered two more in different colours.",
        "notes": "Clear positive with repeat purchase signal"
    },
    {
        "id": "UC4_010", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "These jeans are exactly as described. Comfortable, well-made, and look exactly like the photos.",
        "notes": "Simple positive confirmation"
    },
    {
        "id": "UC4_011", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "medium",
        "text": "Runs slightly small so I exchanged for the next size up. The replacement fits perfectly and I love the style.",
        "notes": "Size issue resolved, positive overall"
    },
    {
        "id": "UC4_012", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "medium",
        "text": "The colour is slightly darker than the website image but the quality is outstanding. Very happy with this.",
        "notes": "Minor colour discrepancy, positive verdict"
    },
    {
        "id": "UC4_013", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "hard",
        "text": "I almost returned it because the stitching looked loose on arrival but after washing it a few times it has held up better than my more expensive shirts.",
        "notes": "Near-return story with positive resolution"
    },
    {
        "id": "UC4_014", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "Incredibly soft and warm. This hoodie is my new favourite thing to wear. Great quality for the price.",
        "notes": "Simple positive"
    },
    {
        "id": "UC4_015", "label": "POSITIVE",
        "category": "Clothing", "difficulty": "hard",
        "text": "Not what I imagined from the description but honestly it looks even better in person. Pleasantly surprised.",
        "notes": "Expectation mismatch but positive surprise"
    },

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Food & Grocery (6 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_016", "label": "POSITIVE",
        "category": "Food", "difficulty": "easy",
        "text": "These coffee beans are exceptional. Rich, smooth flavour with no bitterness. My morning routine has been transformed.",
        "notes": "Clear positive food review"
    },
    {
        "id": "UC4_017", "label": "POSITIVE",
        "category": "Food", "difficulty": "easy",
        "text": "Best protein bars I have ever tried. Actually taste like chocolate and not cardboard. Will definitely reorder.",
        "notes": "Comparison positive"
    },
    {
        "id": "UC4_018", "label": "POSITIVE",
        "category": "Food", "difficulty": "medium",
        "text": "A little sweet for my taste but my kids absolutely love these snacks and they are gone within a day of arriving.",
        "notes": "Personal taste caveat but family positive"
    },
    {
        "id": "UC4_019", "label": "POSITIVE",
        "category": "Food", "difficulty": "medium",
        "text": "More expensive than the supermarket equivalent but the quality difference is noticeable. Worth it for a treat.",
        "notes": "Price acknowledged, quality positive"
    },
    {
        "id": "UC4_020", "label": "POSITIVE",
        "category": "Food", "difficulty": "hard",
        "text": "I was not expecting much for this price point but these olive oils have genuinely changed how I cook. Incredible flavour.",
        "notes": "Low expectation exceeded — hard because opener sounds negative"
    },
    {
        "id": "UC4_021", "label": "POSITIVE",
        "category": "Food", "difficulty": "easy",
        "text": "Fast delivery and the tea selection is wonderful. Every blend I have tried has been delicious. Highly recommend.",
        "notes": "Simple positive"
    },

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Home & Kitchen (6 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_022", "label": "POSITIVE",
        "category": "Home", "difficulty": "easy",
        "text": "This air fryer has changed how I cook. Food comes out crispy and delicious every time. No more deep frying for me.",
        "notes": "Lifestyle change positive"
    },
    {
        "id": "UC4_023", "label": "POSITIVE",
        "category": "Home", "difficulty": "easy",
        "text": "Beautiful duvet cover, soft material, and the zip closure is a nice touch. Exactly what I was looking for.",
        "notes": "Simple positive"
    },
    {
        "id": "UC4_024", "label": "POSITIVE",
        "category": "Home", "difficulty": "medium",
        "text": "Assembly was frustrating but the bookcase looks stunning once built. Solid, sturdy, and exactly the right size.",
        "notes": "Assembly complaint but product positive"
    },
    {
        "id": "UC4_025", "label": "POSITIVE",
        "category": "Home", "difficulty": "medium",
        "text": "I have bought three of these lamps now. One for every room. The warm light is perfect for evenings.",
        "notes": "Repeat purchase = strong positive signal"
    },
    {
        "id": "UC4_026", "label": "POSITIVE",
        "category": "Home", "difficulty": "hard",
        "text": "Took two attempts to get the fit right and customer service could be faster but the blackout curtains work perfectly and I sleep so much better now.",
        "notes": "Two complaints then strong positive outcome"
    },
    {
        "id": "UC4_027", "label": "POSITIVE",
        "category": "Home", "difficulty": "easy",
        "text": "The knife set is sharp, balanced, and came in a beautiful wooden block. A real upgrade from my old set.",
        "notes": "Simple positive"
    },

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Books (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_028", "label": "POSITIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Could not put this book down. Stayed up until 2am finishing it. One of the best thrillers I have read in years.",
        "notes": "Unambiguous positive"
    },
    {
        "id": "UC4_029", "label": "POSITIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Brilliant, thought-provoking and beautifully written. This book changed the way I think about the world.",
        "notes": "Strong positive"
    },
    {
        "id": "UC4_030", "label": "POSITIVE",
        "category": "Books", "difficulty": "medium",
        "text": "The first half was slow but the second half more than made up for it. By the end I was completely gripped.",
        "notes": "Slow start, positive ending"
    },
    {
        "id": "UC4_031", "label": "POSITIVE",
        "category": "Books", "difficulty": "medium",
        "text": "Not my usual genre but I am so glad I gave it a chance. Completely captivating from start to finish.",
        "notes": "Outside comfort zone, positive surprise"
    },
    {
        "id": "UC4_032", "label": "POSITIVE",
        "category": "Books", "difficulty": "hard",
        "text": "Dense and demanding reading that requires real concentration but the payoff is enormous. Unlike anything I have read before.",
        "notes": "Hard because dense/demanding sounds like complaint"
    },
    {
        "id": "UC4_033", "label": "POSITIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Perfect for the beach. Light, fun, and genuinely funny. Read it in two sittings.",
        "notes": "Simple positive"
    },
    {
        "id": "UC4_034", "label": "POSITIVE",
        "category": "Books", "difficulty": "hard",
        "text": "I almost gave up after the first chapter but a friend convinced me to keep going. By chapter three I understood the hype completely.",
        "notes": "Near-abandonment with positive resolution"
    },

    # ══════════════════════════════════════════════════════════
    # POSITIVE — Software (6 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_035", "label": "POSITIVE",
        "category": "Software", "difficulty": "easy",
        "text": "This project management tool has transformed how our team works. Everything in one place, intuitive, and the support is excellent.",
        "notes": "Clear positive"
    },
    {
        "id": "UC4_036", "label": "POSITIVE",
        "category": "Software", "difficulty": "easy",
        "text": "Best antivirus I have used. Lightweight, does not slow down my computer, and has caught several threats already.",
        "notes": "Simple positive"
    },
    {
        "id": "UC4_037", "label": "POSITIVE",
        "category": "Software", "difficulty": "medium",
        "text": "Steep learning curve at first but once you get used to it this design tool is far superior to anything else I have tried.",
        "notes": "Learning curve caveat, strong positive"
    },
    {
        "id": "UC4_038", "label": "POSITIVE",
        "category": "Software", "difficulty": "medium",
        "text": "Pricey subscription but honestly I use it every single day and it has paid for itself many times over.",
        "notes": "Price concern, value positive"
    },
    {
        "id": "UC4_039", "label": "POSITIVE",
        "category": "Software", "difficulty": "hard",
        "text": "The interface looks outdated and the onboarding is confusing but under the hood this accounting software is the most powerful I have ever used.",
        "notes": "Two UI complaints, strong functional positive"
    },
    {
        "id": "UC4_040", "label": "POSITIVE",
        "category": "Software", "difficulty": "easy",
        "text": "Simple, clean, and does exactly what it promises. No bloat, no ads, just a great note-taking app.",
        "notes": "Minimalist positive"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Electronics (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_041", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "Broke after three weeks. Absolute waste of money. Do not buy this.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_042", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "The worst headphones I have ever owned. Tinny sound, uncomfortable fit, and the cable frayed within a month.",
        "notes": "Multiple clear negatives"
    },
    {
        "id": "UC4_043", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "medium",
        "text": "The picture quality is fine but the smart TV software is so slow and buggy that I dread using it. Constant freezing.",
        "notes": "Partial positive then dominant negative"
    },
    {
        "id": "UC4_044", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "medium",
        "text": "Looks great on the desk but the battery barely lasts three hours despite claiming eight. Very disappointed.",
        "notes": "Appearance positive, function negative — negative wins"
    },
    {
        "id": "UC4_045", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "hard",
        "text": "For the price I suppose I cannot complain too much but honestly the build quality feels cheap and the camera is mediocre at best.",
        "notes": "Hard — hedged language but clearly negative"
    },
    {
        "id": "UC4_046", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "easy",
        "text": "Arrived damaged and the seller refused to issue a refund. One star. Avoid.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_047", "label": "NEGATIVE",
        "category": "Electronics", "difficulty": "hard",
        "text": "I wanted to love this tablet and I really tried but after two months the screen has developed dead pixels and the charging port is already loose.",
        "notes": "Wanted to be positive — clearly negative outcome"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Clothing (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_048", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "Terrible quality. Seams came apart after the first wash. Not worth even half the price they charge.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_049", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "Nothing like the photos. The colour is completely different and the material feels like plastic. Returning immediately.",
        "notes": "Misrepresentation complaint"
    },
    {
        "id": "UC4_050", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "medium",
        "text": "The design is cute but the sizing is wildly inconsistent and the fabric pills after just a few wears. Not impressed.",
        "notes": "Design note, dominant negatives"
    },
    {
        "id": "UC4_051", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "medium",
        "text": "Looked good at first but shrank dramatically in the wash even on a cold cycle. Now completely unwearable.",
        "notes": "Initial positive, negative after use"
    },
    {
        "id": "UC4_052", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "hard",
        "text": "I have bought from this brand for years and this new line is such a step down in quality. Genuinely sad about it.",
        "notes": "Emotional language, clearly negative but not angry"
    },
    {
        "id": "UC4_053", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "easy",
        "text": "Buttons fell off within a week. The stitching is appalling. Complete rubbish.",
        "notes": "Simple negative"
    },
    {
        "id": "UC4_054", "label": "NEGATIVE",
        "category": "Clothing", "difficulty": "hard",
        "text": "Maybe I just got a bad batch but the zip broke on first use and the lining was already coming unstitched when it arrived. Hard to recommend.",
        "notes": "Hedged language but clear negative experience"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Food & Grocery (6 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_055", "label": "NEGATIVE",
        "category": "Food", "difficulty": "easy",
        "text": "Disgusting taste. Threw the whole box away after one bite. Complete waste of money.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_056", "label": "NEGATIVE",
        "category": "Food", "difficulty": "easy",
        "text": "Arrived damaged and two of the bottles had leaked. Everything in the package was ruined. Very disappointing.",
        "notes": "Shipping damage complaint"
    },
    {
        "id": "UC4_057", "label": "NEGATIVE",
        "category": "Food", "difficulty": "medium",
        "text": "The smell is pleasant but the taste is extremely artificial. Nothing like a real product should taste. Will not reorder.",
        "notes": "Partial positive (smell) overwhelmed by negative"
    },
    {
        "id": "UC4_058", "label": "NEGATIVE",
        "category": "Food", "difficulty": "medium",
        "text": "I wanted to support a small brand but the quality is nowhere near good enough to justify the premium price. Back to the supermarket.",
        "notes": "Goodwill attempted, quality negative"
    },
    {
        "id": "UC4_059", "label": "NEGATIVE",
        "category": "Food", "difficulty": "hard",
        "text": "Not the worst coffee I have ever had but far too bitter for everyday drinking and the packaging made it go stale within days.",
        "notes": "Faint praise then dominant negatives"
    },
    {
        "id": "UC4_060", "label": "NEGATIVE",
        "category": "Food", "difficulty": "easy",
        "text": "Ordered twice now and both times items were missing from the box. Zero quality control. Do not bother.",
        "notes": "Repeated negative experience"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Home & Kitchen (6 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_061", "label": "NEGATIVE",
        "category": "Home", "difficulty": "easy",
        "text": "Stopped working after two months. Customer service was no help at all. Complete waste of money.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_062", "label": "NEGATIVE",
        "category": "Home", "difficulty": "easy",
        "text": "The pan warped the first time I used it on high heat. Food sticks everywhere despite being advertised as non-stick. Terrible.",
        "notes": "Specific failure complaint"
    },
    {
        "id": "UC4_063", "label": "NEGATIVE",
        "category": "Home", "difficulty": "medium",
        "text": "It looks stylish in photos but in person the materials feel very cheap and it wobbled constantly until I gave up and returned it.",
        "notes": "Photo vs reality complaint"
    },
    {
        "id": "UC4_064", "label": "NEGATIVE",
        "category": "Home", "difficulty": "medium",
        "text": "Assembly instructions were missing half the steps and I ended up with leftover screws. Not confident it is safe.",
        "notes": "Safety concern = clear negative"
    },
    {
        "id": "UC4_065", "label": "NEGATIVE",
        "category": "Home", "difficulty": "hard",
        "text": "Works as described technically but the noise level is far beyond acceptable for a home setting. My neighbours have already complained.",
        "notes": "Technical positive but practical negative"
    },
    {
        "id": "UC4_066", "label": "NEGATIVE",
        "category": "Home", "difficulty": "easy",
        "text": "Smells of chemicals even after multiple washes. Gave me a headache just being in the same room. Returning it.",
        "notes": "Health complaint, clear negative"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Books (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_067", "label": "NEGATIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Boring, predictable, and poorly written. Could not finish it. One of the worst books I have read.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_068", "label": "NEGATIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Total waste of time. The plot went nowhere and the ending was insulting to the reader. Avoid.",
        "notes": "Simple negative"
    },
    {
        "id": "UC4_069", "label": "NEGATIVE",
        "category": "Books", "difficulty": "medium",
        "text": "The premise was interesting but the execution was dreadful. Flat characters, lazy writing, and a plot full of holes.",
        "notes": "Premise positive, execution negative"
    },
    {
        "id": "UC4_070", "label": "NEGATIVE",
        "category": "Books", "difficulty": "medium",
        "text": "I pushed through to the end hoping it would improve. It did not. A disappointing book from an author I usually love.",
        "notes": "Perseverance with negative outcome"
    },
    {
        "id": "UC4_071", "label": "NEGATIVE",
        "category": "Books", "difficulty": "hard",
        "text": "Technically well-written in places but so relentlessly bleak and joyless that I found no pleasure in reading it.",
        "notes": "Technical praise but experiential negative"
    },
    {
        "id": "UC4_072", "label": "NEGATIVE",
        "category": "Books", "difficulty": "easy",
        "text": "Badly edited with obvious errors on almost every page. Distracting and unprofessional.",
        "notes": "Editing complaint"
    },
    {
        "id": "UC4_073", "label": "NEGATIVE",
        "category": "Books", "difficulty": "hard",
        "text": "I can see what the author was trying to do and I respect the ambition but the result is unfortunately unreadable for most people.",
        "notes": "Respectful but clearly negative recommendation"
    },

    # ══════════════════════════════════════════════════════════
    # NEGATIVE — Software (7 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_074", "label": "NEGATIVE",
        "category": "Software", "difficulty": "easy",
        "text": "Crashes constantly. Lost hours of work. Completely unreliable and the support team is useless.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_075", "label": "NEGATIVE",
        "category": "Software", "difficulty": "easy",
        "text": "They changed the pricing model without warning and now charge three times as much. Will be switching to a competitor.",
        "notes": "Pricing complaint = negative"
    },
    {
        "id": "UC4_076", "label": "NEGATIVE",
        "category": "Software", "difficulty": "medium",
        "text": "Some features work well but the core functionality I bought it for is broken and has been for six months with no fix in sight.",
        "notes": "Partial positive, dominant core failure"
    },
    {
        "id": "UC4_077", "label": "NEGATIVE",
        "category": "Software", "difficulty": "medium",
        "text": "The free version was great. The paid version has more bugs, not fewer. Feels like a bait and switch.",
        "notes": "Downgrade perception = negative"
    },
    {
        "id": "UC4_078", "label": "NEGATIVE",
        "category": "Software", "difficulty": "hard",
        "text": "I have used this software for years and each update makes it slower and more cluttered. It used to be elegant.",
        "notes": "Historical positive but current negative trend"
    },
    {
        "id": "UC4_079", "label": "NEGATIVE",
        "category": "Software", "difficulty": "easy",
        "text": "Filled with ads even in the paid version. Completely unacceptable. Deleted immediately.",
        "notes": "Clear negative"
    },
    {
        "id": "UC4_080", "label": "NEGATIVE",
        "category": "Software", "difficulty": "hard",
        "text": "On paper it does everything I need but in practice it is so slow and unintuitive that I spend more time fighting the software than using it.",
        "notes": "Feature positive, experience negative"
    },

    # ══════════════════════════════════════════════════════════
    # NEUTRAL (20 items — across all categories)
    # These are the hardest items. Genuinely mixed reviews.
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC4_081", "label": "NEUTRAL",
        "category": "Electronics", "difficulty": "hard",
        "text": "Does what it says on the box. Nothing more, nothing less. If you need a basic speaker for this price it will do the job.",
        "notes": "Purely functional, no positive or negative sentiment"
    },
    {
        "id": "UC4_082", "label": "NEUTRAL",
        "category": "Electronics", "difficulty": "hard",
        "text": "Good battery life and solid build but the software needs work. Sound quality is average. Three stars.",
        "notes": "Explicit three stars, balanced"
    },
    {
        "id": "UC4_083", "label": "NEUTRAL",
        "category": "Clothing", "difficulty": "hard",
        "text": "The quality is fine for the price. Not exceptional but not bad either. Exactly what you would expect at this price point.",
        "notes": "Explicitly middle ground"
    },
    {
        "id": "UC4_084", "label": "NEUTRAL",
        "category": "Clothing", "difficulty": "medium",
        "text": "I like the style but the fit is not quite right for my body shape. Someone else might love it. Hard to say.",
        "notes": "Personal fit issue — not a product defect"
    },
    {
        "id": "UC4_085", "label": "NEUTRAL",
        "category": "Food", "difficulty": "hard",
        "text": "Tastes fine. Not as good as my local bakery but perfectly acceptable for a packaged product. Would buy again if on offer.",
        "notes": "Conditional reorder — genuinely neutral"
    },
    {
        "id": "UC4_086", "label": "NEUTRAL",
        "category": "Food", "difficulty": "hard",
        "text": "Some flavours in the variety pack are excellent and some are not for me at all. Averages out to an okay purchase.",
        "notes": "Mixed within product — neutral overall"
    },
    {
        "id": "UC4_087", "label": "NEUTRAL",
        "category": "Home", "difficulty": "medium",
        "text": "It does the job. My old one was better but this gets the dishes clean. Functional if unexciting.",
        "notes": "Comparative neutral"
    },
    {
        "id": "UC4_088", "label": "NEUTRAL",
        "category": "Home", "difficulty": "hard",
        "text": "Looks great in the photos and looks great in my home too but I have had some reliability issues that make me hesitant to fully recommend it.",
        "notes": "Positive appearance, negative reliability — balanced"
    },
    {
        "id": "UC4_089", "label": "NEUTRAL",
        "category": "Books", "difficulty": "medium",
        "text": "Well written but not really my kind of book. I can see why others love it. Just not for me.",
        "notes": "Personal preference neutral — quality vs taste distinction"
    },
    {
        "id": "UC4_090", "label": "NEUTRAL",
        "category": "Books", "difficulty": "hard",
        "text": "The first and third acts are excellent but the middle drags considerably. Overall an uneven but worthwhile read.",
        "notes": "Mixed quality parts — genuinely neutral verdict"
    },
    {
        "id": "UC4_091", "label": "NEUTRAL",
        "category": "Software", "difficulty": "hard",
        "text": "Does some things brilliantly and other things poorly. Whether it works for you depends entirely on your specific use case.",
        "notes": "Conditional recommendation — neutral"
    },
    {
        "id": "UC4_092", "label": "NEUTRAL",
        "category": "Software", "difficulty": "medium",
        "text": "Reasonable value for money. Not the best tool available but not the worst either. Gets the job done most of the time.",
        "notes": "Explicit middle ground language"
    },
    {
        "id": "UC4_093", "label": "NEUTRAL",
        "category": "Electronics", "difficulty": "hard",
        "text": "Mixed feelings on this one. The hardware is impressive but the software lets it down. Potential that has not been fully realised.",
        "notes": "Explicit mixed feelings"
    },
    {
        "id": "UC4_094", "label": "NEUTRAL",
        "category": "Clothing", "difficulty": "hard",
        "text": "Wore it twice and I am still not sure how I feel about it. The quality seems fine but I keep questioning whether it suits me.",
        "notes": "Genuine indecision — neutral"
    },
    {
        "id": "UC4_095", "label": "NEUTRAL",
        "category": "Food", "difficulty": "medium",
        "text": "Decent enough product. Does what it says. Nothing special but nothing wrong with it either. Three stars feels right.",
        "notes": "Explicit three-star language"
    },
    {
        "id": "UC4_096", "label": "NEUTRAL",
        "category": "Home", "difficulty": "hard",
        "text": "I replaced a much cheaper version with this and I am honestly not sure the upgrade was worth the extra cost. Similar performance.",
        "notes": "Upgrade regret — genuinely neutral"
    },
    {
        "id": "UC4_097", "label": "NEUTRAL",
        "category": "Books", "difficulty": "hard",
        "text": "Important subject matter handled in an adequate but not inspiring way. You will learn something but you will not be moved.",
        "notes": "Functional positive, emotional neutral"
    },
    {
        "id": "UC4_098", "label": "NEUTRAL",
        "category": "Software", "difficulty": "hard",
        "text": "The company clearly has good intentions and the product is improving with each update but right now it is not quite there yet.",
        "notes": "Positive trajectory but current state neutral"
    },
    {
        "id": "UC4_099", "label": "NEUTRAL",
        "category": "Electronics", "difficulty": "medium",
        "text": "Works perfectly well for basic tasks. If you need more than the basics you will want something more powerful. Honest product.",
        "notes": "Scoped positive = neutral overall"
    },
    {
        "id": "UC4_100", "label": "NEUTRAL",
        "category": "Home", "difficulty": "hard",
        "text": "My partner loves it. I think it is just okay. Maybe it depends on personal taste more than product quality.",
        "notes": "Disagreement between users — genuinely neutral"
    },
]


def assign_splits(items):
    """
    Stratified split — 30% test from each label class.
    POSITIVE: 28 train / 12 test
    NEGATIVE: 28 train / 12 test
    NEUTRAL:  14 train /  6 test
    """
    from collections import defaultdict
    by_label = defaultdict(list)
    for item in items:
        by_label[item["label"]].append(item)

    for label, group in by_label.items():
        n_test = round(len(group) * 0.30)
        for i, item in enumerate(group):
            item["split"] = "test" if i >= len(group) - n_test else "train"

    return items


def build_csv():
    items = assign_splits(GOLD_SET)
    filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    fieldnames = ["id", "text", "label", "category", "difficulty", "source", "notes", "split"]
    for item in items:
        item["source"] = "synthetic"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    return filepath


def build_metadata():
    items = [i for i in GOLD_SET]
    pos = [i for i in items if i["label"] == "POSITIVE"]
    neg = [i for i in items if i["label"] == "NEGATIVE"]
    neu = [i for i in items if i["label"] == "NEUTRAL"]

    meta = {
        "use_case": "UC4",
        "name": "Product Review Sentiment",
        "pre_registration_date": "2026-03-03",
        "s3_score": 2.1,
        "s3_prediction": "Pure SLM",
        "version": "1.0",
        "total_items": len(items),
        "label_distribution": {
            "POSITIVE": len(pos),
            "NEGATIVE": len(neg),
            "NEUTRAL":  len(neu),
        },
        "categories": ["Electronics", "Clothing", "Food", "Home", "Books", "Software"],
        "difficulty_distribution": {
            "easy":   len([i for i in items if i["difficulty"] == "easy"]),
            "medium": len([i for i in items if i["difficulty"] == "medium"]),
            "hard":   len([i for i in items if i["difficulty"] == "hard"]),
        },
        "split": {
            "train": len([i for i in items if i.get("split") == "train"]),
            "test":  len([i for i in items if i.get("split") == "test"]),
        },
        "split_method": "stratified_by_label",
        "evaluation_metrics": [
            "Accuracy", "Macro F1", "Per-class F1 (POSITIVE / NEGATIVE / NEUTRAL)",
            "Confusion Matrix 3x3", "Hallucination Rate", "Latency P50/P95"
        ],
        "pre_registered_hypotheses": [
            "H4.1: Best SLM achieves >= 90% of LLM accuracy on UC4",
            "H4.2: Best SLM P95 latency < 2000ms",
            "H4.3: UC4 graduates to Pure SLM (S3=2.1, Stakes=1)",
            "H4.4: NEUTRAL class will have lowest per-class F1 across all models",
        ]
    }
    meta_path = os.path.join(OUTPUT_DIR, META_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta_path


def print_summary():
    items = assign_splits(GOLD_SET)
    pos = [i for i in items if i["label"] == "POSITIVE"]
    neg = [i for i in items if i["label"] == "NEGATIVE"]
    neu = [i for i in items if i["label"] == "NEUTRAL"]
    train_n = len([i for i in items if i["split"] == "train"])
    test_n  = len([i for i in items if i["split"] == "test"])

    print()
    print("=" * 64)
    print("  UC4 GOLD SET — Build Complete")
    print("  Product Review Sentiment — Pre-Registration v1.0")
    print("  S³ Score: 2.1  →  Pure SLM predicted")
    print("=" * 64)
    print()
    print(f"  Total items  : {len(items)}")
    print(f"  POSITIVE     : {len(pos)} items")
    print(f"  NEGATIVE     : {len(neg)} items")
    print(f"  NEUTRAL      : {len(neu)} items  ← hardest class")
    print()
    print("  Category breakdown:")
    from collections import Counter
    cats = Counter(i["category"] for i in items)
    for cat, n in sorted(cats.items()):
        print(f"    {cat:<20} {n} items")
    print()
    print("  Difficulty distribution:")
    for diff in ["easy", "medium", "hard"]:
        n = len([i for i in items if i["difficulty"] == diff])
        bar = "█" * n
        print(f"    {diff:<8} {bar:<45} {n}")
    print()
    print(f"  Split method : STRATIFIED by label (fixes UC1 issue)")
    print(f"  Train / Test : {train_n} train / {test_n} test")
    print()

    # Verify test distribution
    from collections import Counter
    test_items = [i for i in items if i["split"] == "test"]
    test_labels = Counter(i["label"] for i in test_items)
    print("  Test set label distribution:")
    for label, n in sorted(test_labels.items()):
        print(f"    {label:<12} {n} items")
    print()
    print("  Files saved:")
    print(f"    data/gold_sets/{OUTPUT_FILE}")
    print(f"    data/gold_sets/uc4_metadata.json")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print()
    print("  KEY DIFFERENCE FROM UC1:")
    print("  → 3-class output (POSITIVE / NEGATIVE / NEUTRAL)")
    print("  → NEUTRAL class is the hard case — watch per-class F1")
    print("  → Stakes=1 means wrong answer has no real consequence")
    print("  → S³=2.1 predicts Pure SLM — this is your proof point")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc4.py")
    print("=" * 64)
    print()


if __name__ == "__main__":
    print()
    print("Building UC4 Gold Set — Product Review Sentiment...")
    build_csv()
    build_metadata()
    print_summary()