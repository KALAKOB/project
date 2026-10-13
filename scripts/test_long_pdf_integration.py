import tkinter as tk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== Starting Long.pdf Integration Test ===")

# 1. Check all extracted assets
cards_dir = "assets/med_cards"
items_dir = "assets/items_clean"
pdf_dir = "assets/long_pdf"

required_cards = [
    "card_01_stomach.png", "card_02_diarrhea.png", "card_03_pain_fever.png",
    "card_04_laxatives.png", "card_05_cough.png", "card_06_dizziness.png",
    "card_07_throat.png", "card_08_eye.png", "card_09_muscle.png",
    "card_10_wound.png", "card_11_skin.png", "banner_title.png", "banner_footer.png"
]

for c in required_cards:
    p = os.path.join(cards_dir, c)
    if not os.path.exists(p):
        print(f"ERROR: Missing card {p}")
        sys.exit(1)
print(f"Verified all {len(required_cards)} medical cards exist!")

# 2. Check Tkinter loading
root = tk.Tk()
root.withdraw()

from ui_theme import get_image
from vn_widgets import show_moph_poster_modal
from data import MOPH_HOUSEHOLD_CATEGORIES, CABINET_MEDICINES, SHOP_ITEMS
from main import PharmacyAfterlifeApp

# Verify get_image loads cards and items
for cat in MOPH_HOUSEHOLD_CATEGORIES:
    img = get_image(cat["card_image"], (200, 100))
    if not img:
        print(f"ERROR: Could not load card {cat['card_image']}")
        sys.exit(1)
print("All MOPH category cards loaded in Tkinter successfully!")

for med in CABINET_MEDICINES:
    if med.get("image"):
        img = get_image(med["image"], (50, 50))
        if not img:
            print(f"ERROR: Could not load cabinet med image {med['image']}")
            sys.exit(1)
print("All cabinet med images loaded in Tkinter successfully!")

# Initialize app
app = PharmacyAfterlifeApp(root)
print("PharmacyAfterlifeApp initialized successfully!")

# Test opening MOPH poster modal
show_moph_poster_modal(root)
print("show_moph_poster_modal opened successfully!")

# Test opening with specific category
show_moph_poster_modal(root, initial_category_id="card_03_pain_fever.png")
print("show_moph_poster_modal with initial_category_id opened successfully!")

# Test Scene 1 with cabinet minigame & shopping minigame
app.load_scene("scene1")
s1 = app.current_scene_frame
print("Scene 1 loaded successfully!")

s1.start_cabinet_minigame()
print("Cabinet minigame started successfully!")

# Inspect first medicine
s1.select_medicine_to_inspect(CABINET_MEDICINES[0])
print("Cabinet medicine inspected successfully with long.pdf image!")

# Start shopping minigame
s1.start_shopping_minigame()
print("Shopping minigame started successfully with long.pdf thumbnails!")

root.destroy()
print("=== All Long.pdf Integration Tests Passed Successfully! ===")
